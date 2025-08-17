import json
import hashlib
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
import redis
import asyncio
from ..core.config import settings
import structlog


class CacheService:
    """Centralized caching service with Redis backend."""
    
    def __init__(self):
        self.logger = structlog.get_logger("cache")
        self.redis_client: Optional[redis.Redis] = None
        self.default_ttl = settings.AI_CACHE_TTL
        self.key_prefix = f"battlecard:{settings.ENVIRONMENT}:"
        
        if settings.ENABLE_CACHING:
            self._connect_redis()
    
    def _connect_redis(self) -> None:
        """Connect to Redis with error handling."""
        try:
            self.redis_client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=20
            )
            
            # Test connection
            self.redis_client.ping()
            self.logger.info("Connected to Redis cache")
            
        except Exception as e:
            self.logger.error(
                "Failed to connect to Redis",
                error=str(e),
                redis_url=settings.REDIS_URL
            )
            self.redis_client = None
    
    def _generate_cache_key(self, namespace: str, key: str) -> str:
        """Generate a standardized cache key."""
        # Create hash of the key to avoid issues with special characters
        key_hash = hashlib.md5(str(key).encode()).hexdigest()
        return f"{self.key_prefix}{namespace}:{key_hash}"
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for storage."""
        try:
            return json.dumps({
                'data': value,
                'cached_at': datetime.now().isoformat(),
                'type': type(value).__name__
            })
        except (TypeError, ValueError) as e:
            self.logger.warning(
                "Failed to serialize cache value",
                error=str(e),
                value_type=type(value).__name__
            )
            return json.dumps({
                'data': str(value),
                'cached_at': datetime.now().isoformat(),
                'type': 'string'
            })
    
    def _deserialize_value(self, serialized: str) -> Any:
        """Deserialize value from storage."""
        try:
            cached_data = json.loads(serialized)
            return cached_data.get('data')
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.warning(
                "Failed to deserialize cache value",
                error=str(e)
            )
            return None
    
    async def get(self, namespace: str, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        
        cache_key = self._generate_cache_key(namespace, key)
        
        try:
            serialized = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.get, cache_key
            )
            
            if serialized:
                self.logger.debug(
                    "Cache hit",
                    namespace=namespace,
                    key=key[:50]  # Truncate for logging
                )
                return self._deserialize_value(serialized)
            
            self.logger.debug(
                "Cache miss",
                namespace=namespace,
                key=key[:50]
            )
            return None
            
        except Exception as e:
            self.logger.error(
                "Cache get error",
                namespace=namespace,
                key=key[:50],
                error=str(e)
            )
            return None
    
    async def set(
        self, 
        namespace: str, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        if not self.redis_client:
            return False
        
        cache_key = self._generate_cache_key(namespace, key)
        ttl = ttl or self.default_ttl
        
        try:
            serialized = self._serialize_value(value)
            
            success = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.redis_client.setex(cache_key, ttl, serialized)
            )
            
            self.logger.debug(
                "Cache set",
                namespace=namespace,
                key=key[:50],
                ttl=ttl,
                success=bool(success)
            )
            
            return bool(success)
            
        except Exception as e:
            self.logger.error(
                "Cache set error",
                namespace=namespace,
                key=key[:50],
                error=str(e)
            )
            return False
    
    async def delete(self, namespace: str, key: str) -> bool:
        """Delete value from cache."""
        if not self.redis_client:
            return False
        
        cache_key = self._generate_cache_key(namespace, key)
        
        try:
            deleted = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.delete, cache_key
            )
            
            self.logger.debug(
                "Cache delete",
                namespace=namespace,
                key=key[:50],
                deleted=bool(deleted)
            )
            
            return bool(deleted)
            
        except Exception as e:
            self.logger.error(
                "Cache delete error",
                namespace=namespace,
                key=key[:50],
                error=str(e)
            )
            return False
    
    async def clear_namespace(self, namespace: str) -> int:
        """Clear all keys in a namespace."""
        if not self.redis_client:
            return 0
        
        pattern = f"{self.key_prefix}{namespace}:*"
        
        try:
            keys = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.keys, pattern
            )
            
            if keys:
                deleted = await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.delete, *keys
                )
                
                self.logger.info(
                    "Cache namespace cleared",
                    namespace=namespace,
                    keys_deleted=deleted
                )
                
                return deleted
            
            return 0
            
        except Exception as e:
            self.logger.error(
                "Cache clear error",
                namespace=namespace,
                error=str(e)
            )
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.redis_client:
            return {"status": "disabled"}
        
        try:
            info = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.info
            )
            
            return {
                "status": "connected",
                "used_memory": info.get('used_memory_human', 'unknown'),
                "connected_clients": info.get('connected_clients', 0),
                "total_commands_processed": info.get('total_commands_processed', 0),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0),
                "hit_rate": (
                    info.get('keyspace_hits', 0) / 
                    max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1)
                )
            }
            
        except Exception as e:
            self.logger.error("Failed to get cache stats", error=str(e))
            return {"status": "error", "error": str(e)}
    
    def generate_request_id(self) -> str:
        """Generate unique request ID."""
        import uuid
        return str(uuid.uuid4())


# Global cache instance
cache_service = CacheService()


def cache_key_for_ai_request(
    agent_type: str, 
    input_data: Dict[str, Any],
    model: str = "default"
) -> str:
    """Generate cache key for AI requests."""
    # Create deterministic hash of input data
    data_str = json.dumps(input_data, sort_keys=True)
    data_hash = hashlib.md5(data_str.encode()).hexdigest()
    
    return f"ai:{agent_type}:{model}:{data_hash}"


async def cached_ai_request(
    agent_type: str,
    input_data: Dict[str, Any],
    processor_func,
    model: str = "default",
    ttl: Optional[int] = None
) -> Dict[str, Any]:
    """Wrapper for caching AI requests."""
    cache_key = cache_key_for_ai_request(agent_type, input_data, model)
    
    # Try to get from cache first
    cached_result = await cache_service.get("ai_responses", cache_key)
    if cached_result:
        structlog.get_logger("cache").info(
            "AI response served from cache",
            agent_type=agent_type,
            model=model
        )
        return cached_result
    
    # Process and cache result
    result = await processor_func(input_data)
    
    if result.get('status') == 'success':
        await cache_service.set("ai_responses", cache_key, result, ttl)
    
    return result