from typing import Any, Dict, Optional
from fastapi import HTTPException
from enum import Enum


class ErrorCode(str, Enum):
    # Authentication & Authorization
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    
    # Business Logic
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    
    # AI Processing
    AI_GENERATION_FAILED = "AI_GENERATION_FAILED"
    AI_SERVICE_UNAVAILABLE = "AI_SERVICE_UNAVAILABLE"
    PROMPT_TEMPLATE_NOT_FOUND = "PROMPT_TEMPLATE_NOT_FOUND"
    
    # External Services
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    NETWORK_ERROR = "NETWORK_ERROR"
    
    # System
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    CACHE_ERROR = "CACHE_ERROR"


class BattlecardException(Exception):
    """Base exception for all battlecard-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details,
            "timestamp": datetime.utcnow().isoformat()
        }


class ValidationError(BattlecardException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field_errors: Optional[Dict[str, str]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            details={"field_errors": field_errors or {}}
        )


class AuthenticationError(BattlecardException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_CREDENTIALS
        )


class AuthorizationError(BattlecardException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str = "Insufficient permissions", required_role: Optional[str] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            details={"required_role": required_role}
        )


class ResourceNotFoundError(BattlecardException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with id '{resource_id}' not found",
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class AIGenerationError(BattlecardException):
    """Raised when AI content generation fails."""
    
    def __init__(self, message: str, model_used: Optional[str] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.AI_GENERATION_FAILED,
            details={"model_used": model_used}
        )


class ExternalAPIError(BattlecardException):
    """Raised when external API calls fail."""
    
    def __init__(self, service: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(
            message=f"External API error from {service}",
            error_code=ErrorCode.EXTERNAL_API_ERROR,
            details={
                "service": service,
                "status_code": status_code,
                "response_body": response_body
            }
        )


def create_http_exception(error: BattlecardException) -> HTTPException:
    """Convert a BattlecardException to an HTTPException."""
    status_code_mapping = {
        ErrorCode.INVALID_CREDENTIALS: 401,
        ErrorCode.TOKEN_EXPIRED: 401,
        ErrorCode.INSUFFICIENT_PERMISSIONS: 403,
        ErrorCode.VALIDATION_ERROR: 400,
        ErrorCode.INVALID_INPUT: 400,
        ErrorCode.MISSING_REQUIRED_FIELD: 400,
        ErrorCode.RESOURCE_NOT_FOUND: 404,
        ErrorCode.DUPLICATE_RESOURCE: 409,
        ErrorCode.OPERATION_NOT_ALLOWED: 409,
        ErrorCode.RATE_LIMIT_EXCEEDED: 429,
        ErrorCode.AI_GENERATION_FAILED: 503,
        ErrorCode.AI_SERVICE_UNAVAILABLE: 503,
        ErrorCode.EXTERNAL_API_ERROR: 502,
        ErrorCode.NETWORK_ERROR: 502,
        ErrorCode.INTERNAL_ERROR: 500,
        ErrorCode.DATABASE_ERROR: 500,
        ErrorCode.CACHE_ERROR: 500,
    }
    
    status_code = status_code_mapping.get(error.error_code, 500)
    
    return HTTPException(
        status_code=status_code,
        detail=error.to_dict()
    )