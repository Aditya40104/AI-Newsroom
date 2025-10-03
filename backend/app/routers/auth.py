"""
Authentication API routes for login, registration, and OAuth.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.database import get_db
from app.models import User, UserRole
from app.utils.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    verify_google_token,
    verify_github_token,
    get_current_user
)
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class OAuthLogin(BaseModel):
    token: str
    provider: str  # "google" or "github"


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    Args:
        user_data: User registration data
        db: Database session
    
    Returns:
        Access token and user information
    
    Raises:
        HTTPException: If user already exists or validation fails
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    try:
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=UserRole.WRITER,  # Default role
            is_active=True,
            is_verified=False
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"New user registered: {user_data.email}")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(db_user.id), "email": db_user.email}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": {
                "id": db_user.id,
                "email": db_user.email,
                "username": db_user.username,
                "full_name": db_user.full_name,
                "role": db_user.role.value,
                "is_active": db_user.is_active
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user account"
        )


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password.
    
    Args:
        user_credentials: Login credentials
        db: Database session
    
    Returns:
        Access token and user information
    
    Raises:
        HTTPException: If credentials are invalid
    """
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    try:
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/oauth/google", response_model=Token)
async def google_oauth_login(oauth_data: OAuthLogin, db: Session = Depends(get_db)):
    """
    Login or register using Google OAuth.
    
    Args:
        oauth_data: Google OAuth token
        db: Database session
    
    Returns:
        Access token and user information
    """
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth not configured"
        )
    
    try:
        # Verify Google token and get user info
        user_info = await verify_google_token(oauth_data.token)
        return await _handle_oauth_user(db, user_info, "google", "google_id")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication failed"
        )


@router.post("/oauth/github", response_model=Token)
async def github_oauth_login(oauth_data: OAuthLogin, db: Session = Depends(get_db)):
    """
    Login or register using GitHub OAuth.
    
    Args:
        oauth_data: GitHub OAuth token
        db: Database session
    
    Returns:
        Access token and user information
    """
    if not settings.github_client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub OAuth not configured"
        )
    
    try:
        # Verify GitHub token and get user info
        user_info = await verify_github_token(oauth_data.token)
        return await _handle_oauth_user(db, user_info, "github", "github_id")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub OAuth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub authentication failed"
        )


async def _handle_oauth_user(db: Session, user_info: dict, provider: str, id_field: str):
    """Helper function to handle OAuth user creation/login"""
    email = user_info.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by OAuth provider"
        )
    
    oauth_id_value = str(user_info.get("id"))
    
    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        # Update OAuth ID if not set
        if getattr(user, id_field) is None:
            setattr(user, id_field, oauth_id_value)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
    else:
        # Create new user
        username = user_info.get("login", user_info.get("name", email.split("@")[0]))
        
        # Ensure unique username
        base_username = username
        counter = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        user_data = {
            "email": email,
            "username": username,
            "full_name": user_info.get("name"),
            "avatar_url": user_info.get("avatar_url", user_info.get("picture")),
            "role": UserRole.WRITER,
            "is_active": True,
            "is_verified": True,  # OAuth users are considered verified
            id_field: oauth_id_value
        }
        
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"New {provider} OAuth user created: {email}")
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer", 
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active
        }
    }


@router.post("/oauth", response_model=Token)
async def oauth_login(oauth_data: OAuthLogin, db: Session = Depends(get_db)):
    """
    Login or register using OAuth (Google/GitHub).
    
    Args:
        oauth_data: OAuth token and provider
        db: Database session
    
    Returns:
        Access token and user information
    
    Raises:
        HTTPException: If OAuth verification fails
    """
    try:
        # Verify OAuth token and get user info
        if oauth_data.provider == "google":
            if not settings.google_client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google OAuth not configured"
                )
            user_info = await verify_google_token(oauth_data.token)
            oauth_id_field = "google_id"
            oauth_id_value = user_info.get("id")
            
        elif oauth_data.provider == "github":
            if not settings.github_client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="GitHub OAuth not configured"
                )
            user_info = await verify_github_token(oauth_data.token)
            oauth_id_field = "github_id"
            oauth_id_value = str(user_info.get("id"))
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported OAuth provider"
            )
        
        email = user_info.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by OAuth provider"
            )
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Update OAuth ID if not set
            if getattr(user, oauth_id_field) is None:
                setattr(user, oauth_id_field, oauth_id_value)
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
        else:
            # Create new user
            username = user_info.get("login", user_info.get("name", email.split("@")[0]))
            
            # Ensure unique username
            base_username = username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            user_data = {
                "email": email,
                "username": username,
                "full_name": user_info.get("name"),
                "avatar_url": user_info.get("avatar_url", user_info.get("picture")),
                "role": UserRole.WRITER,
                "is_active": True,
                "is_verified": True,  # OAuth users are considered verified
                oauth_id_field: oauth_id_value
            }
            
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"New OAuth user created: {email} via {oauth_data.provider}")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"OAuth login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth authentication failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User information
    """
    return current_user


@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh access token.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        New access token
    """
    access_token = create_access_token(
        data={"sub": str(current_user.id), "email": current_user.email}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client should discard token).
    
    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}


@router.get("/oauth-config")
async def get_oauth_config():
    """
    Get OAuth configuration for frontend.
    
    Returns:
        Available OAuth providers and their client IDs
    """
    config = {}
    
    if settings.google_client_id:
        config["google"] = {
            "client_id": settings.google_client_id,
            "enabled": True
        }
    
    if settings.github_client_id:
        config["github"] = {
            "client_id": settings.github_client_id,
            "enabled": True
        }
    
    return config