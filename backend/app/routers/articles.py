"""
Article management API routes.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import re

router = APIRouter()

# Simple response models for basic functionality
class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class ArticleCreate(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    id: int
    title: str
    slug: str
    summary: Optional[str]
    tags: List[str]
    category: Optional[str]
    status: str
    featured_image_url: Optional[str]
    view_count: int
    like_count: int
    ai_generated: bool
    fact_check_status: str
    author: dict
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CitationCreate(BaseModel):
    title: str
    url: str
    author: Optional[str] = None
    publication_date: Optional[datetime] = None
    publisher: Optional[str] = None
    citation_style: str = "APA"
    page_number: Optional[str] = None
    context_snippet: Optional[str] = None
    position_in_text: Optional[int] = None


class CommentCreate(BaseModel):
    content: str
    comment_type: str = "comment"
    text_position: Optional[int] = None
    selected_text: Optional[str] = None
    parent_id: Optional[int] = None


def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    slug = title.lower()
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return slug.strip('-')


def ensure_unique_slug(db: Session, slug: str, article_id: Optional[int] = None) -> str:
    """Ensure slug is unique by appending number if needed"""
    base_slug = slug
    counter = 1
    
    while True:
        query = db.query(Article).filter(Article.slug == slug)
        if article_id:
            query = query.filter(Article.id != article_id)
        
        if not query.first():
            return slug
        
        slug = f"{base_slug}-{counter}"
        counter += 1


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_data: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new article.
    
    Args:
        article_data: Article creation data
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Created article
    """
    try:
        # Generate unique slug
        slug = generate_slug(article_data.title)
        slug = ensure_unique_slug(db, slug)
        
        # Create article
        db_article = Article(
            title=article_data.title,
            slug=slug,
            content=article_data.content,
            summary=article_data.summary,
            tags=article_data.tags,
            category=article_data.category,
            featured_image_url=article_data.featured_image_url,
            meta_description=article_data.meta_description,
            status=ArticleStatus.DRAFT,
            author_id=current_user.id,
            ai_generated=False
        )
        
        db.add(db_article)
        db.commit()
        db.refresh(db_article)
        
        # Create initial version
        version = ArticleVersion(
            version_number=1,
            title=db_article.title,
            content=db_article.content,
            summary=db_article.summary,
            change_summary="Initial version",
            article_id=db_article.id,
            author_id=current_user.id
        )
        
        db.add(version)
        db.commit()
        
        logger.info(f"Article created: {db_article.id} by user {current_user.id}")
        
        # Load article with author info
        article = db.query(Article).options(
            joinedload(Article.author)
        ).filter(Article.id == db_article.id).first()
        
        # Format response
        article_dict = {
            **article.__dict__,
            "author": {
                "id": article.author.id,
                "username": article.author.username,
                "full_name": article.author.full_name
            }
        }
        
        return article_dict
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating article: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create article"
        )


@router.get("/", response_model=List[ArticleListResponse])
async def get_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, regex="^(draft|review|published|archived)$"),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    author_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = Query("created_at", regex="^(created_at|updated_at|title|view_count)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Get articles with filtering and pagination.
    
    Args:
        skip: Number of articles to skip
        limit: Maximum number of articles to return
        status_filter: Filter by article status
        category: Filter by category
        tag: Filter by tag
        author_id: Filter by author ID
        search: Search in title and content
        sort_by: Sort field
        sort_order: Sort order (asc/desc)
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        List of articles
    """
    try:
        # Build query
        query = db.query(Article).options(joinedload(Article.author))
        
        # Apply filters
        if status_filter:
            # Non-admin users can only see published articles and their own drafts
            if current_user and (current_user.role == "admin" or current_user.role == "editor"):
                query = query.filter(Article.status == status_filter)
            else:
                if status_filter == "published":
                    query = query.filter(Article.status == ArticleStatus.PUBLISHED)
                elif current_user and status_filter == "draft":
                    query = query.filter(
                        (Article.status == status_filter) & 
                        (Article.author_id == current_user.id)
                    )
                else:
                    query = query.filter(Article.status == ArticleStatus.PUBLISHED)
        else:
            # Default: show published articles and user's own drafts
            if current_user:
                query = query.filter(
                    (Article.status == ArticleStatus.PUBLISHED) |
                    ((Article.author_id == current_user.id) & (Article.status != ArticleStatus.ARCHIVED))
                )
            else:
                query = query.filter(Article.status == ArticleStatus.PUBLISHED)
        
        if category:
            query = query.filter(Article.category == category)
        
        if tag:
            query = query.filter(Article.tags.contains([tag]))
        
        if author_id:
            query = query.filter(Article.author_id == author_id)
        
        if search:
            query = query.filter(
                (Article.title.ilike(f"%{search}%")) |
                (Article.content.ilike(f"%{search}%")) |
                (Article.summary.ilike(f"%{search}%"))
            )
        
        # Apply sorting
        order_func = desc if sort_order == "desc" else asc
        if sort_by == "created_at":
            query = query.order_by(order_func(Article.created_at))
        elif sort_by == "updated_at":
            query = query.order_by(order_func(Article.updated_at))
        elif sort_by == "title":
            query = query.order_by(order_func(Article.title))
        elif sort_by == "view_count":
            query = query.order_by(order_func(Article.view_count))
        
        # Apply pagination
        articles = query.offset(skip).limit(limit).all()
        
        # Format response
        result = []
        for article in articles:
            article_dict = {
                **{k: v for k, v in article.__dict__.items() if not k.startswith('_')},
                "author": {
                    "id": article.author.id,
                    "username": article.author.username,
                    "full_name": article.author.full_name
                }
            }
            result.append(article_dict)
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch articles"
        )


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Get a specific article by ID.
    
    Args:
        article_id: Article ID
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Article details
    """
    try:
        article = db.query(Article).options(
            joinedload(Article.author)
        ).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        # Check access permissions
        if article.status != ArticleStatus.PUBLISHED:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Article not found"
                )
            
            # Only author, editors, and admins can see unpublished articles
            if (article.author_id != current_user.id and 
                current_user.role not in ["editor", "admin"]):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Article not found"
                )
        
        # Increment view count for published articles
        if article.status == ArticleStatus.PUBLISHED:
            article.view_count += 1
            db.commit()
        
        # Format response
        article_dict = {
            **{k: v for k, v in article.__dict__.items() if not k.startswith('_')},
            "author": {
                "id": article.author.id,
                "username": article.author.username,
                "full_name": article.author.full_name,
                "avatar_url": article.author.avatar_url
            }
        }
        
        return article_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch article"
        )


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing article.
    
    Args:
        article_id: Article ID
        article_data: Article update data
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated article
    """
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        # Check permissions
        if (article.author_id != current_user.id and 
            current_user.role not in ["editor", "admin"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to edit this article"
            )
        
        # Store original values for version tracking
        original_title = article.title
        original_content = article.content
        original_summary = article.summary
        
        # Update fields
        update_data = article_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "status":
                # Validate status change permissions
                if (value in ["published", "archived"] and 
                    current_user.role not in ["editor", "admin"]):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Not authorized to change article status"
                    )
                setattr(article, field, value)
            elif field == "title":
                article.title = value
                # Update slug if title changed
                new_slug = generate_slug(value)
                article.slug = ensure_unique_slug(db, new_slug, article_id)
            else:
                setattr(article, field, value)
        
        # Update timestamp
        article.updated_at = datetime.utcnow()
        
        # Set published_at if status changed to published
        if (article_data.status == "published" and 
            article.status == ArticleStatus.PUBLISHED and 
            not article.published_at):
            article.published_at = datetime.utcnow()
        
        db.commit()
        
        # Create version if content changed significantly
        content_changed = (
            original_title != article.title or
            original_content != article.content or
            original_summary != article.summary
        )
        
        if content_changed:
            # Get next version number
            last_version = db.query(ArticleVersion).filter(
                ArticleVersion.article_id == article_id
            ).order_by(desc(ArticleVersion.version_number)).first()
            
            next_version = (last_version.version_number + 1) if last_version else 1
            
            version = ArticleVersion(
                version_number=next_version,
                title=article.title,
                content=article.content,
                summary=article.summary,
                change_summary="Article updated",
                article_id=article.id,
                author_id=current_user.id
            )
            
            db.add(version)
            db.commit()
        
        # Reload article with author info
        article = db.query(Article).options(
            joinedload(Article.author)
        ).filter(Article.id == article_id).first()
        
        logger.info(f"Article updated: {article_id} by user {current_user.id}")
        
        # Format response
        article_dict = {
            **{k: v for k, v in article.__dict__.items() if not k.startswith('_')},
            "author": {
                "id": article.author.id,
                "username": article.author.username,
                "full_name": article.author.full_name
            }
        }
        
        return article_dict
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating article {article_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update article"
        )


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an article (only author or admin).
    
    Args:
        article_id: Article ID
        db: Database session
        current_user: Current authenticated user
    """
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        # Check permissions
        if (article.author_id != current_user.id and 
            current_user.role != "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this article"
            )
        
        db.delete(article)
        db.commit()
        
        logger.info(f"Article deleted: {article_id} by user {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting article {article_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete article"
        )