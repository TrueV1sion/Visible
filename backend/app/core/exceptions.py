from typing import Any, Dict, Optional
from fastapi import HTTPException
from enum import Enum
import traceback
from datetime import datetime


class ErrorCode(str, Enum):
    # Authentication & Authorization
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    ACCOUNT_DISABLED = "ACCOUNT_DISABLED"
    
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FILE_FORMAT = "INVALID_FILE_FORMAT"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    
    # Business Logic
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    INVALID_STATE_TRANSITION = "INVALID_STATE_TRANSITION"
    
    # AI Processing
    AI_GENERATION_FAILED = "AI_GENERATION_FAILED"
    AI_SERVICE_UNAVAILABLE = "AI_SERVICE_UNAVAILABLE"
    AI_TIMEOUT = "AI_TIMEOUT"
    PROMPT_TEMPLATE_NOT_FOUND = "PROMPT_TEMPLATE_NOT_FOUND"
    MODEL_NOT_AVAILABLE = "MODEL_NOT_AVAILABLE"
    
    # External Services
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    NETWORK_ERROR = "NETWORK_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # System
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    CACHE_ERROR = "CACHE_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"


class BattlecardException(Exception):
    """Base exception for all battlecard-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        user_message: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
        self.user_message = user_message or message
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error_code": self.error_code.value,
            "message": self.user_message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "trace_id": getattr(self, 'trace_id', None)
        }
    
    def add_context(self, **kwargs) -> 'BattlecardException':
        """Add contextual information to the exception."""
        self.details.update(kwargs)
        return self


class ValidationError(BattlecardException):
    """Raised when input validation fails."""
    
    def __init__(
        self, 
        message: str, 
        field_errors: Optional[Dict[str, str]] = None,
        invalid_fields: Optional[list] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            details={
                "field_errors": field_errors or {},
                "invalid_fields": invalid_fields or []
            },
            user_message="Please check your input and try again"
        )


class AuthenticationError(BattlecardException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", login_required: bool = True):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_CREDENTIALS,
            details={"login_required": login_required},
            user_message="Please sign in to continue"
        )


class AuthorizationError(BattlecardException):
    """Raised when user lacks required permissions."""
    
    def __init__(
        self, 
        message: str = "Insufficient permissions", 
        required_role: Optional[str] = None,
        current_role: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            details={
                "required_role": required_role,
                "current_role": current_role
            },
            user_message="You don't have permission to perform this action"
        )


class ResourceNotFoundError(BattlecardException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str, resource_name: Optional[str] = None):
        super().__init__(
            message=f"{resource_type} with id '{resource_id}' not found",
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            details={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "resource_name": resource_name
            },
            user_message=f"The requested {resource_type.lower()} was not found"
        )


class AIGenerationError(BattlecardException):
    """Raised when AI content generation fails."""
    
    def __init__(
        self, 
        message: str, 
        model_used: Optional[str] = None,
        retry_count: int = 0,
        max_retries: int = 3
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.AI_GENERATION_FAILED,
            details={
                "model_used": model_used,
                "retry_count": retry_count,
                "max_retries": max_retries,
                "retryable": retry_count < max_retries
            },
            user_message="AI generation failed. Please try again or contact support"
        )


class AITimeoutError(BattlecardException):
    """Raised when AI processing times out."""
    
    def __init__(self, timeout_duration: float, operation: str):
        super().__init__(
            message=f"AI processing timed out after {timeout_duration}s for {operation}",
            error_code=ErrorCode.AI_TIMEOUT,
            details={
                "timeout_duration": timeout_duration,
                "operation": operation
            },
            user_message="The request is taking longer than expected. Please try again"
        )


class ExternalAPIError(BattlecardException):
    """Raised when external API calls fail."""
    
    def __init__(
        self, 
        service: str, 
        status_code: Optional[int] = None, 
        response_body: Optional[str] = None,
        endpoint: Optional[str] = None
    ):
        super().__init__(
            message=f"External API error from {service}",
            error_code=ErrorCode.EXTERNAL_API_ERROR,
            details={
                "service": service,
                "status_code": status_code,
                "response_body": response_body,
                "endpoint": endpoint
            },
            user_message=f"External service {service} is temporarily unavailable"
        )


class RateLimitExceededError(BattlecardException):
    """Raised when rate limits are exceeded."""
    
    def __init__(
        self, 
        limit: int, 
        window: int, 
        retry_after: Optional[int] = None,
        limit_type: str = "requests"
    ):
        super().__init__(
            message=f"Rate limit exceeded: {limit} {limit_type} per {window} seconds",
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            details={
                "limit": limit,
                "window": window,
                "retry_after": retry_after,
                "limit_type": limit_type
            },
            user_message=f"Too many {limit_type}. Please wait before trying again"
        )


class DatabaseError(BattlecardException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: str, table: Optional[str] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR,
            details={
                "operation": operation,
                "table": table
            },
            user_message="A database error occurred. Please try again"
        )


def create_http_exception(error: BattlecardException) -> HTTPException:
    """Convert a BattlecardException to an HTTPException with proper status codes."""
    status_code_mapping = {
        ErrorCode.INVALID_CREDENTIALS: 401,
        ErrorCode.TOKEN_EXPIRED: 401,
        ErrorCode.ACCOUNT_DISABLED: 401,
        ErrorCode.INSUFFICIENT_PERMISSIONS: 403,
        ErrorCode.VALIDATION_ERROR: 400,
        ErrorCode.INVALID_INPUT: 400,
        ErrorCode.MISSING_REQUIRED_FIELD: 400,
        ErrorCode.INVALID_FILE_FORMAT: 400,
        ErrorCode.FILE_TOO_LARGE: 413,
        ErrorCode.RESOURCE_NOT_FOUND: 404,
        ErrorCode.DUPLICATE_RESOURCE: 409,
        ErrorCode.OPERATION_NOT_ALLOWED: 409,
        ErrorCode.INVALID_STATE_TRANSITION: 409,
        ErrorCode.RATE_LIMIT_EXCEEDED: 429,
        ErrorCode.AI_GENERATION_FAILED: 503,
        ErrorCode.AI_SERVICE_UNAVAILABLE: 503,
        ErrorCode.AI_TIMEOUT: 504,
        ErrorCode.MODEL_NOT_AVAILABLE: 503,
        ErrorCode.EXTERNAL_API_ERROR: 502,
        ErrorCode.NETWORK_ERROR: 502,
        ErrorCode.SERVICE_UNAVAILABLE: 503,
        ErrorCode.INTERNAL_ERROR: 500,
        ErrorCode.DATABASE_ERROR: 500,
        ErrorCode.CACHE_ERROR: 500,
        ErrorCode.CONFIGURATION_ERROR: 500,
    }
    
    status_code = status_code_mapping.get(error.error_code, 500)
    
    return HTTPException(
        status_code=status_code,
        detail=error.to_dict()
    )


def handle_unexpected_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> BattlecardException:
    """Convert unexpected errors to BattlecardException with proper logging."""
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Log the full traceback for debugging
    logger.error(
        "Unexpected error occurred",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "traceback": traceback.format_exc()
        }
    )
    
    # Create sanitized exception for user
    battlecard_error = BattlecardException(
        message=f"Unexpected {type(error).__name__}: {str(error)}",
        error_code=ErrorCode.INTERNAL_ERROR,
        details=context or {},
        cause=error,
        user_message="An unexpected error occurred. Please try again or contact support"
    )
    
    return battlecard_error


# Error handling decorator
def handle_exceptions(func):
    """Decorator to handle exceptions in API endpoints."""
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BattlecardException:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Convert unexpected exceptions
            battlecard_error = handle_unexpected_error(e, {
                "function": func.__name__,
                "args": str(args)[:200],  # Truncate for logging
                "kwargs": str(kwargs)[:200]
            })
            raise create_http_exception(battlecard_error)
    
    return wrapper