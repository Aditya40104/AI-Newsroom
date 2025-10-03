from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from app.database import get_db
from app.models import User, Article

logger = logging.getLogger(__name__)

router = APIRouter()

# Mock user for testing - in production this would come from JWT token
class MockUser:
    def __init__(self):
        self.id = 1
        self.username = "admin"
        self.email = "admin@test.com"
        self.role = "admin"
        self.is_active = True

def get_current_user():
    """Mock current user for testing"""
    return MockUser()

def get_admin_user(current_user: MockUser = Depends(get_current_user)):
    """Ensure current user is admin"""
    if current_user.role not in ["admin", "editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Editor access required"
        )
    return current_user

def get_super_admin_user(current_user: MockUser = Depends(get_current_user)):
    """Ensure current user is super admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.get("/users")
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: MockUser = Depends(get_admin_user)
):
    """Get all users with their stats"""
    try:
        users = db.query(User).all()
        user_stats = []
        
        for user in users:
            # Count articles by status
            total_articles = db.query(Article).filter(Article.author_id == user.id).count()
            published_articles = db.query(Article).filter(
                Article.author_id == user.id,
                Article.status == "published"
            ).count()
            draft_articles = db.query(Article).filter(
                Article.author_id == user.id,
                Article.status == "draft"
            ).count()
            
            user_stats.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at,
                "is_active": user.is_active,
                "stats": {
                    "total_articles": total_articles,
                    "published_articles": published_articles,
                    "draft_articles": draft_articles
                }
            })
        
        return {"users": user_stats}
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: MockUser = Depends(get_super_admin_user)
):
    """Update user role (admin only)"""
    try:
        if role not in ["writer", "editor", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be writer, editor, or admin"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent demoting the last admin
        if user.role == "admin" and role != "admin":
            admin_count = db.query(User).filter(User.role == "admin").count()
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the last admin"
                )
        
        user.role = role
        db.commit()
        
        return {"message": f"User role updated to {role}", "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user role: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user role")

@router.get("/articles")
async def get_all_articles(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: MockUser = Depends(get_admin_user)
):
    """Get all articles with filtering"""
    try:
        query = db.query(Article).join(User)
        
        if status_filter:
            query = query.filter(Article.status == status_filter)
        
        articles = query.order_by(desc(Article.updated_at)).offset(offset).limit(limit).all()
        
        article_list = []
        for article in articles:
            author = db.query(User).filter(User.id == article.author_id).first()
            article_list.append({
                "id": article.id,
                "title": article.title,
                "content": article.content[:200] + "..." if len(article.content) > 200 else article.content,
                "status": article.status,
                "created_at": article.created_at,
                "updated_at": article.updated_at,
                "author": {
                    "id": author.id,
                    "username": author.username,
                    "role": author.role
                } if author else None,
                "tags": article.tags,
                "category": article.category
            })
        
        total = db.query(Article).count()
        
        return {
            "articles": article_list,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching articles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch articles")

@router.put("/articles/{article_id}/status")
async def update_article_status(
    article_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: MockUser = Depends(get_admin_user)
):
    """Approve, reject, or change article status"""
    try:
        if new_status not in ["draft", "published", "rejected", "under_review"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status"
            )
        
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        # Check permissions
        if current_user.role == "editor":
            # Editors can only approve articles from writers
            author = db.query(User).filter(User.id == article.author_id).first()
            if author and author.role not in ["writer"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Editors can only manage writer articles"
                )
        
        article.status = new_status
        article.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": f"Article status updated to {new_status}", "article_id": article_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating article status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update article status")

@router.delete("/articles/{article_id}")
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: MockUser = Depends(get_super_admin_user)
):
    """Delete article (admin only)"""
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        db.delete(article)
        db.commit()
        
        return {"message": "Article deleted successfully", "article_id": article_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting article: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete article")

@router.get("/analytics")
async def get_analytics(
    db: Session = Depends(get_db),
    current_user: MockUser = Depends(get_admin_user)
):
    """Get analytics data for dashboard"""
    try:
        # Basic counts
        total_users = db.query(User).count()
        total_articles = db.query(Article).count()
        published_articles = db.query(Article).filter(Article.status == "published").count()
        draft_articles = db.query(Article).filter(Article.status == "draft").count()
        
        # Articles by status
        status_counts = db.query(
            Article.status, func.count(Article.id)
        ).group_by(Article.status).all()
        
        # Articles by user
        user_article_counts = db.query(
            User.username, func.count(Article.id)
        ).join(Article).group_by(User.username).all()
        
        # Articles created in last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_articles = db.query(Article).filter(
            Article.created_at >= week_ago
        ).count()
        
        # Articles by category
        category_counts = db.query(
            Article.category, func.count(Article.id)
        ).filter(Article.category.isnot(None)).group_by(Article.category).all()
        
        # Role distribution
        role_counts = db.query(
            User.role, func.count(User.id)
        ).group_by(User.role).all()
        
        return {
            "overview": {
                "total_users": total_users,
                "total_articles": total_articles,
                "published_articles": published_articles,
                "draft_articles": draft_articles,
                "recent_articles": recent_articles
            },
            "charts": {
                "articles_by_status": [{"status": status, "count": count} for status, count in status_counts],
                "articles_by_user": [{"user": user, "count": count} for user, count in user_article_counts],
                "articles_by_category": [{"category": cat, "count": count} for cat, count in category_counts],
                "users_by_role": [{"role": role, "count": count} for role, count in role_counts]
            }
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

@router.post("/articles/bulk-action")
async def bulk_article_action(
    article_ids: List[int],
    action: str,
    new_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: MockUser = Depends(get_admin_user)
):
    """Perform bulk actions on articles"""
    try:
        if action not in ["delete", "update_status"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action"
            )
        
        if action == "update_status" and not new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="new_status required for update_status action"
            )
        
        articles = db.query(Article).filter(Article.id.in_(article_ids)).all()
        
        if action == "delete":
            if current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admins can delete articles"
                )
            for article in articles:
                db.delete(article)
        
        elif action == "update_status":
            for article in articles:
                article.status = new_status
                article.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": f"Bulk {action} completed",
            "affected_articles": len(articles)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing bulk action: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to perform bulk action")