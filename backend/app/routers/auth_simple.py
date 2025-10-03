"""
Simple authentication routes for testing.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import json
import os

router = APIRouter()

# Simple file-based user storage for testing
USERS_FILE = "users_test.json"

def load_users():
    """Load users from file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_users(users):
    """Save users to file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def get_user_by_email(email):
    """Get user by email"""
    users = load_users()
    return users.get(email)

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = "writer"  # Default role

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register new user - simplified for testing."""
    # Validate role
    valid_roles = ["writer", "editor", "admin"]
    if request.role and request.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Check if user already exists
    users = load_users()
    if request.email in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    user_id = len(users) + 1
    user_data = {
        "id": user_id,
        "email": request.email,
        "username": request.username,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "role": request.role or "writer",
        "password": request.password,  # In production, hash this!
        "is_active": True
    }
    
    users[request.email] = user_data
    save_users(users)
    
    return AuthResponse(
        access_token=f"token_{user_id}_{request.email}",
        user={
            "id": user_id,
            "email": request.email,
            "username": request.username,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "role": request.role or "writer"
        }
    )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user - simplified for testing."""
    if not request.email or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    # Find user by email
    user = get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check password (in production, compare hashed passwords)
    if user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return AuthResponse(
        access_token=f"token_{user['id']}_{user['email']}",
        user={
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "role": user["role"]
        }
    )

@router.post("/logout")
async def logout():
    """Logout user."""
    return {"message": "Successfully logged out"}

@router.get("/me")
async def get_current_user():
    """Get current user profile - mock response."""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "role": "writer"
    }

@router.post("/create-test-users")
async def create_test_users():
    """Create test users for demonstration"""
    users = load_users()
    
    test_users = [
        {
            "email": "writer@test.com",
            "password": "password",
            "username": "writer",
            "first_name": "Test",
            "last_name": "Writer",
            "role": "writer"
        },
        {
            "email": "editor@test.com", 
            "password": "password",
            "username": "editor",
            "first_name": "Test", 
            "last_name": "Editor",
            "role": "editor"
        },
        {
            "email": "admin@test.com",
            "password": "password", 
            "username": "admin",
            "first_name": "Test",
            "last_name": "Admin", 
            "role": "admin"
        }
    ]
    
    created_users = []
    for user_data in test_users:
        if user_data["email"] not in users:
            user_id = len(users) + 1
            user_record = {
                "id": user_id,
                "email": user_data["email"],
                "username": user_data["username"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "role": user_data["role"],
                "password": user_data["password"],
                "is_active": True
            }
            users[user_data["email"]] = user_record
            created_users.append({
                "email": user_data["email"],
                "role": user_data["role"],
                "password": user_data["password"]
            })
    
    save_users(users)
    
    return {
        "message": "Test users created successfully",
        "users": created_users
    }