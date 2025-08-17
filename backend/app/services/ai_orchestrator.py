import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
from ..core.config import settings
from ..core.exceptions import AIGenerationError, ValidationError
from ..ai.factory import AIAgentFactory
from .cache import cache_service, cached_ai_request


class AIOrchestrator:
    """Orchestrates AI agent execution with caching, rate limiting, and error handling."""
    
    def __init__(self):
        self.logger = structlog.get_logger("ai.orchestrator")
        self.max_concurrent_requests = settings.MAX_CONCURRENT_AI_REQUESTS
        self.request_semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        self.active_requests: Dict[str, asyncio.Task] = {}
    
    async def process_with_agent(
        self,
        agent_type: str,
        input_data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process data with specified agent type."""
        options = options or {}
        
        # Validate input
        if not agent_type or not input_data:
            raise ValidationError("Agent type and input data are required")
        
        # Check if agent type exists
        if agent_type not in AIAgentFactory.list_available_agents():
            raise ValidationError(f"Unknown agent type: {agent_type}")
        
        # Generate request context
        request_id = self._generate_request_id()
        context = {
            "request_id": request_id,
            "agent_type": agent_type,
            "timestamp": datetime.now().isoformat(),
            "options": options
        }
        
        self.logger.info(
            "AI processing started",
            **context
        )
        
        try:
            async with self.request_semaphore:
                # Create processing task
                task = asyncio.create_task(
                    self._process_with_caching(agent_type, input_data, options)
                )
                
                # Track active request
                self.active_requests[request_id] = task
                
                try:
                    result = await task
                    
                    self.logger.info(
                        "AI processing completed",
                        request_id=request_id,
                        agent_type=agent_type,
                        status=result.get('status')
                    )
                    
                    return result
                    
                finally:
                    # Clean up active request tracking
                    self.active_requests.pop(request_id, None)
                    
        except asyncio.TimeoutError:
            raise AIGenerationError(
                f"AI processing timed out for agent {agent_type}",
                model_used=options.get('model_preference')
            )
        except Exception as e:
            self.logger.error(
                "AI processing failed",
                request_id=request_id,
                agent_type=agent_type,
                error=str(e),
                error_type=type(e).__name__
            )
            
            if isinstance(e, AIGenerationError):
                raise
            else:
                raise AIGenerationError(
                    f"AI processing failed: {str(e)}",
                    model_used=options.get('model_preference')
                )
    
    async def _process_with_caching(
        self,
        agent_type: str,
        input_data: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process with caching support."""
        model = options.get('model_preference', 'auto')
        
        async def processor(data):
            agent = AIAgentFactory.get_agent(agent_type)
            return await agent.process_with_timeout(data)
        
        return await cached_ai_request(
            agent_type=agent_type,
            input_data=input_data,
            processor_func=processor,
            model=model,
            ttl=options.get('cache_ttl')
        )
    
    async def generate_battlecard(
        self,
        competitor_info: Dict[str, Any],
        product_segment: str,
        focus_areas: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a complete battlecard using multiple agents."""
        options = options or {}
        request_id = self._generate_request_id()
        
        self.logger.info(
            "Battlecard generation started",
            request_id=request_id,
            competitor=competitor_info.get('name'),
            product_segment=product_segment
        )
        
        try:
            # Step 1: Collect and analyze competitor data
            aggregation_input = {
                "competitor_name": competitor_info.get('name'),
                "context": {
                    "product_segment": product_segment,
                    "focus_areas": focus_areas
                }
            }
            
            aggregation_result = await self.process_with_agent(
                "aggregator",
                aggregation_input,
                options
            )
            
            if aggregation_result.get('status') != 'success':
                raise AIGenerationError("Failed to aggregate competitor data")
            
            # Step 2: Generate battlecard content
            battlecard_input = {
                "competitor_info": competitor_info,
                "aggregated_data": aggregation_result['data'],
                "product_segment": product_segment,
                "focus_areas": focus_areas,
                "include_sections": options.get('include_sections', [
                    'overview', 'strengths_weaknesses', 'objection_handling', 'winning_strategies'
                ])
            }
            
            battlecard_result = await self.process_with_agent(
                "battlecard_generation",
                battlecard_input,
                options
            )
            
            if battlecard_result.get('status') != 'success':
                raise AIGenerationError("Failed to generate battlecard content")
            
            # Combine results
            final_result = {
                "status": "success",
                "data": {
                    "battlecard": battlecard_result['data'],
                    "source_data": aggregation_result['data'],
                    "metadata": {
                        "request_id": request_id,
                        "generated_at": datetime.now().isoformat(),
                        "competitor": competitor_info.get('name'),
                        "product_segment": product_segment,
                        "focus_areas": focus_areas,
                        "processing_time": {
                            "aggregation": aggregation_result.get('metadata', {}).get('processing_time'),
                            "generation": battlecard_result.get('metadata', {}).get('processing_time')
                        }
                    }
                }
            }
            
            self.logger.info(
                "Battlecard generation completed",
                request_id=request_id,
                competitor=competitor_info.get('name')
            )
            
            return final_result
            
        except Exception as e:
            self.logger.error(
                "Battlecard generation failed",
                request_id=request_id,
                competitor=competitor_info.get('name'),
                error=str(e)
            )
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status and metrics."""
        return {
            "active_requests": len(self.active_requests),
            "max_concurrent": self.max_concurrent_requests,
            "available_agents": AIAgentFactory.list_available_agents(),
            "cache_stats": await cache_service.get_stats(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def cancel_request(self, request_id: str) -> bool:
        """Cancel an active AI request."""
        if request_id in self.active_requests:
            task = self.active_requests[request_id]
            task.cancel()
            
            self.logger.info(
                "AI request cancelled",
                request_id=request_id
            )
            
            return True
        return False
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        import uuid
        return str(uuid.uuid4())


# Global orchestrator instance
ai_orchestrator = AIOrchestrator()