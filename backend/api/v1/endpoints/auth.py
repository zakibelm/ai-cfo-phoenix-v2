"""
Authentication Endpoints
Login, Register, Refresh Token, Logout
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
import uuid

from core.auth import (
    auth_service,
    UserCreate,
    UserLogin,
    Token,
    UserInDB,
    get_current_user,
    TokenData
)

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory user store (replace with database in production)
# This is just for demonstration
users_db: dict[str, UserInDB] = {}


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user
    
    Creates a new user account and returns access/refresh tokens
    """
    try:
        # Check if user already exists
        existing_user = next(
            (u for u in users_db.values() if u.email == user_data.email),
            None
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user_id = str(uuid.uuid4())
        hashed_password = auth_service.get_password_hash(user_data.password)
        
        new_user = UserInDB(
            id=user_id,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role,
            created_at=datetime.utcnow()
        )
        
        users_db[user_id] = new_user
        
        logger.info(f"New user registered: {user_data.email}")
        
        # Create tokens
        tokens = auth_service.create_tokens(new_user)
        return tokens
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login user
    
    Authenticates user and returns access/refresh tokens
    """
    try:
        # Find user by email
        user = next(
            (u for u in users_db.values() if u.email == credentials.email),
            None
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not auth_service.verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        logger.info(f"User logged in: {credentials.email}")
        
        # Create tokens
        tokens = auth_service.create_tokens(user)
        return tokens
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """
    Refresh access token
    
    Uses refresh token to generate new access token
    """
    try:
        # Verify refresh token
        token_data = auth_service.verify_token(refresh_token)
        
        # Find user
        user = users_db.get(token_data.user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Create new tokens
        tokens = auth_service.create_tokens(user)
        return tokens
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me")
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """
    Get current user information
    
    Returns information about the authenticated user
    """
    try:
        user = users_db.get(current_user.user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    """
    Logout user
    
    In a production app, you would invalidate the token here
    (e.g., add to blacklist in Redis)
    """
    logger.info(f"User logged out: {current_user.email}")
    
    return {
        "message": "Successfully logged out",
        "user_id": current_user.user_id
    }


# Initialize with a default admin user for testing
def initialize_default_users():
    """Create default users for testing"""
    if not users_db:
        admin_id = str(uuid.uuid4())
        admin_user = UserInDB(
            id=admin_id,
            email="admin@aicfo.com",
            hashed_password=auth_service.get_password_hash("admin123"),
            full_name="Admin User",
            role="admin",
            created_at=datetime.utcnow()
        )
        users_db[admin_id] = admin_user
        
        user_id = str(uuid.uuid4())
        regular_user = UserInDB(
            id=user_id,
            email="user@aicfo.com",
            hashed_password=auth_service.get_password_hash("user123"),
            full_name="Regular User",
            role="user",
            created_at=datetime.utcnow()
        )
        users_db[user_id] = regular_user
        
        logger.info("Default users initialized (admin@aicfo.com / admin123, user@aicfo.com / user123)")


# Initialize default users on module load
initialize_default_users()

