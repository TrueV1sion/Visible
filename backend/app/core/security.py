from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..db.base import get_db
from ..models.user import User
from ..core.exceptions import AuthenticationError, AuthorizationError, create_http_exception
from .config import settings
import secrets
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Password validation regex
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')


def validate_password(password: str) -> bool:
    """Validate password meets security requirements."""
    return bool(PASSWORD_REGEX.match(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    if not validate_password(password):
        raise ValueError(
            "Password must be at least 8 characters with uppercase, lowercase, number, and special character"
        )
    return pwd_context.hash(password)


def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm="HS256"
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm="HS256"
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user."""
    try:
        payload = verify_token(token, "access")
        if payload is None:
            raise AuthenticationError("Invalid or expired token")
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token payload")
            
    except AuthenticationError as e:
        raise create_http_exception(e)
    except JWTError:
        raise create_http_exception(AuthenticationError("Invalid token"))
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise create_http_exception(AuthenticationError("User not found"))
    
    if not user.is_active:
        raise create_http_exception(AuthenticationError("Inactive user"))
    
    return user


def require_role(required_roles: Union[str, list]):
    """Decorator to require specific user roles."""
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in required_roles:
            raise create_http_exception(
                AuthorizationError(
                    f"Access denied. Required role: {', '.join(required_roles)}",
                    required_role=', '.join(required_roles)
                )
            )
        return current_user
    
    return role_checker


def generate_secure_token() -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(32)


async def refresh_access_token(
    refresh_token: str,
    db: Session
) -> Optional[dict]:
    """Refresh access token using refresh token."""
    payload = verify_token(refresh_token, "refresh")
    if payload is None:
        return None
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active or user.refresh_token != refresh_token:
        return None
    
    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Update refresh token in database
    user.refresh_token = new_refresh_token
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


def revoke_refresh_token(user: User, db: Session) -> None:
    """Revoke user's refresh token."""
    user.refresh_token = None
    db.commit()