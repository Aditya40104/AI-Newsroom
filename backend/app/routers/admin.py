"""
Admin API routes.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/stats")
async def get_admin_stats():
    """Get admin statistics - placeholder"""
    return {"message": "Admin stats endpoint - to be implemented"}

@router.get("/users")
async def get_all_users():
    """Get all users - placeholder"""
    return {"message": "Admin users endpoint - to be implemented"}