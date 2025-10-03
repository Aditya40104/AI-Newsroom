"""
User management API routes.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/profile")
async def get_user_profile():
    """Get user profile - placeholder"""
    return {"message": "User profile endpoint - to be implemented"}

@router.put("/profile")
async def update_user_profile():
    """Update user profile - placeholder"""
    return {"message": "Profile update endpoint - to be implemented"}