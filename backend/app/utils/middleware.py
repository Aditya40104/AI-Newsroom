"""
Middleware for role-based access control and request processing.
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Optional
import logging
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, get_db
from app.models import User

logger = logging.getLogger(__name__)

class RoleBasedAccessMiddleware:
    """Middleware for role-based access control"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        # Only process HTTP requests
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        # Create request object
        request = Request(scope, receive)
        
        # Check if route requires authentication
        path = request.url.path
        method = request.method
        
        # Define protected routes and required roles
        protected_routes = {
            "/admin": "admin",
            "/articles": "writer",  # Create/update articles
            "/ai": "writer",        # AI services
        }
        
        # Check if route is protected
        requires_role = None
        for route_prefix, role in protected_routes.items():
            if path.startswith(route_prefix) and method in ["POST", "PUT", "DELETE"]:
                requires_role = role
                break
        
        if requires_role:
            # Get authorization header
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                await self._send_unauthorized(send)
                return
            
            # Extract token
            token = auth_header.split(" ")[1]
            
            try:
                # Verify token
                payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
                user_id = payload.get("sub")
                
                if not user_id:
                    await self._send_unauthorized(send)
                    return
                
                # Get user from database
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == int(user_id)).first()
                    if not user or not user.is_active:
                        await self._send_unauthorized(send)
                        return
                    
                    # Check role
                    if requires_role == "admin" and user.role != "admin":
                        await self._send_forbidden(send)
                        return
                    elif requires_role == "editor" and user.role not in ["editor", "admin"]:
                        await self._send_forbidden(send)
                        return
                    
                    # Add user to request state
                    scope["user"] = user
                    
                finally:
                    db.close()
                    
            except (JWTError, ValueError):
                await self._send_unauthorized(send)
                return
        
        # Continue to the application
        await self.app(scope, receive, send)
    
    async def _send_unauthorized(self, send):
        """Send 401 Unauthorized response"""
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                [b"content-type", b"application/json"],
                [b"www-authenticate", b"Bearer"],
            ],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"detail": "Not authenticated"}',
        })
    
    async def _send_forbidden(self, send):
        """Send 403 Forbidden response"""
        await send({
            "type": "http.response.start",
            "status": 403,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"detail": "Insufficient permissions"}',
        })


def get_current_user_from_request(request: Request) -> Optional[User]:
    """Get current user from request state (set by middleware)"""
    return getattr(request.state, "user", None)