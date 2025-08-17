from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ....core import security
from ....core.config import settings
from ....core.exceptions import AuthenticationError, ValidationError, create_http_exception
from ....schemas.user import Token, TokenRefresh
from ....models.user import User
from ....db.base import get_db

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login with refresh token support."""
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
        if not user or not security.verify_password(form_data.password, user.hashed_password):
            raise AuthenticationError("Incorrect email or password")
        
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            data={"sub": str(user.id)}, 
            expires_delta=access_token_expires
        )
        refresh_token = security.create_refresh_token(data={"sub": str(user.id)})
        
        # Store refresh token
        user.refresh_token = refresh_token
        user.last_login = func.now()
        db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except AuthenticationError as e:
        raise create_http_exception(e)
    except Exception as e:
        raise create_http_exception(
            AuthenticationError(f"Login failed: {str(e)}")
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: TokenRefresh,
    db: Session = Depends(get_db)
) -> Any:
    """Refresh access token using refresh token."""
    try:
        result = await security.refresh_access_token(
            refresh_data.refresh_token, 
            db
        )
        
        if not result:
            raise AuthenticationError("Invalid or expired refresh token")
        
        return result
        
    except AuthenticationError as e:
        raise create_http_exception(e)


@router.post("/logout")
async def logout(
    current_user: User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Logout user and revoke refresh token."""
    try:
        security.revoke_refresh_token(current_user, db)
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.post("/validate-token")
async def validate_token(
    current_user: User = Depends(security.get_current_user)
) -> Any:
    """Validate current access token."""
    return {
        "valid": True,
        "user_id": current_user.id,
        "role": current_user.role.value,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/change-password")
async def change_password(
    *,
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Change user password with validation."""
    try:
        # Verify current password
        if not security.verify_password(current_password, current_user.hashed_password):
            raise AuthenticationError("Current password is incorrect")
        
        # Validate new password
        if not security.validate_password(new_password):
            raise ValidationError(
                "Password must be at least 8 characters with uppercase, lowercase, number, and special character"
            )
        
        # Update password
        current_user.hashed_password = security.get_password_hash(new_password)
        
        # Revoke existing refresh token to force re-login
        security.revoke_refresh_token(current_user, db)
        
        return {"message": "Password updated successfully"}
        
    except (AuthenticationError, ValidationError) as e:
        raise create_http_exception(e)