from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
import asyncio
import structlog
from datetime import datetime


class BaseAgent(ABC):
    """Enhanced base class for all AI agents with proper error handling and timeouts."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the base agent with enhanced configuration."""
        self.config = config or {}
        self.logger = self._setup_structured_logger()
        self.timeout = self.config.get('timeout', 30)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 1.0)
        
        # Performance tracking
        self._request_count = 0
        self._error_count = 0
        self._total_processing_time = 0.0
    
    def _setup_structured_logger(self) -> structlog.BoundLogger:
        """Set up structured logging for better observability."""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        return structlog.get_logger(self.__class__.__name__)
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return results."""
        pass
    
    async def process_with_timeout(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process with timeout and retry logic."""
        start_time = datetime.now()
        self._request_count += 1
        
        try:
            # Validate input first
            if not self.validate_input(input_data):
                raise ValueError("Input validation failed")
            
            # Process with timeout
            result = await asyncio.wait_for(
                self._process_with_retries(input_data),
                timeout=self.timeout
            )
            
            # Track performance
            processing_time = (datetime.now() - start_time).total_seconds()
            self._total_processing_time += processing_time
            
            # Log success
            self.logger.info(
                "Agent processing completed",
                processing_time=processing_time,
                request_count=self._request_count,
                avg_processing_time=self._total_processing_time / self._request_count
            )
            
            return result
            
        except asyncio.TimeoutError:
            self._error_count += 1
            self.logger.error(
                "Agent processing timed out",
                timeout=self.timeout,
                error_rate=self._error_count / self._request_count
            )
            raise TimeoutError(f"Agent {self.__class__.__name__} timed out after {self.timeout}s")
        
        except Exception as e:
            self._error_count += 1
            self.logger.error(
                "Agent processing failed",
                error=str(e),
                error_type=type(e).__name__,
                error_rate=self._error_count / self._request_count
            )
            raise
    
    async def _process_with_retries(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process with retry logic for transient failures."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await self.process(input_data)
            except Exception as e:
                last_exception = e
                
                # Don't retry on validation errors or permanent failures
                if isinstance(e, (ValueError, TypeError)):
                    raise
                
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(
                        "Agent processing failed, retrying",
                        attempt=attempt + 1,
                        max_retries=self.max_retries,
                        delay=delay,
                        error=str(e)
                    )
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(
                        "Agent processing failed after all retries",
                        attempts=attempt + 1,
                        error=str(e)
                    )
        
        raise last_exception
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data format. Override in subclasses."""
        if not isinstance(input_data, dict):
            return False
        return True
    
    def format_output(self, raw_output: Any) -> Dict[str, Any]:
        """Format raw output into standardized structure."""
        return {
            "result": raw_output,
            "timestamp": datetime.now().isoformat(),
            "agent": self.__class__.__name__,
            "processing_metadata": {
                "request_count": self._request_count,
                "error_count": self._error_count,
                "avg_processing_time": (
                    self._total_processing_time / self._request_count 
                    if self._request_count > 0 else 0
                )
            }
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get agent health status for monitoring."""
        error_rate = self._error_count / self._request_count if self._request_count > 0 else 0
        avg_time = self._total_processing_time / self._request_count if self._request_count > 0 else 0
        
        status = "healthy"
        if error_rate > 0.1:  # More than 10% error rate
            status = "degraded"
        if error_rate > 0.5:  # More than 50% error rate
            status = "unhealthy"
        
        return {
            "status": status,
            "error_rate": error_rate,
            "avg_processing_time": avg_time,
            "total_requests": self._request_count,
            "total_errors": self._error_count,
            "config": {
                "timeout": self.timeout,
                "max_retries": self.max_retries
            }
        }