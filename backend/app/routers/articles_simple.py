"""
Simple article management API routes for testing.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import re

router = APIRouter()

# Mock data for testing
mock_articles = []
next_article_id = 1

# Utility functions
def slugify(text: str) -> str:
    """Create URL-friendly slug from text."""
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text[:100]

def calculate_read_time(content: str) -> int:
    """Calculate estimated read time in minutes."""
    words = len(content.split())
    return max(1, words // 200)

def count_words(content: str) -> int:
    """Count words in HTML content."""
    clean_text = re.sub(r'<[^>]+>', '', content)
    return len(clean_text.split())

# Pydantic schemas
class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = None
    tags: List[str] = []
    status: str = Field(default="draft")
    featured_image_url: Optional[str] = None
    meta_description: Optional[str] = None

class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    featured_image_url: Optional[str] = None
    meta_description: Optional[str] = None

class ArticleResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    summary: Optional[str]
    author_id: int
    author_name: str
    status: str
    featured_image_url: Optional[str]
    meta_description: Optional[str]
    word_count: int
    read_time: int
    views: int
    version: int
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]

# Mock current user function
def get_current_user():
    return {
        "id": 1,
        "username": "testuser",
        "full_name": "Test User",
        "role": "writer"
    }

@router.get("/")
async def get_articles():
    """Get all articles."""
    return mock_articles

@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(article_data: ArticleCreate):
    """Create a new article."""
    global next_article_id
    current_user = get_current_user()
    
    # Create slug from title
    slug = slugify(article_data.title)
    word_count = count_words(article_data.content)
    read_time = calculate_read_time(article_data.content)
    
    now = datetime.utcnow()
    published_at = now if article_data.status == "published" else None
    
    new_article = {
        "id": next_article_id,
        "title": article_data.title,
        "slug": slug,
        "content": article_data.content,
        "summary": article_data.summary,
        "author_id": current_user["id"],
        "author_name": current_user["full_name"],
        "status": article_data.status,
        "featured_image_url": article_data.featured_image_url,
        "meta_description": article_data.meta_description,
        "word_count": word_count,
        "read_time": read_time,
        "views": 0,
        "version": 1,
        "tags": article_data.tags or [],
        "created_at": now,
        "updated_at": now,
        "published_at": published_at
    }
    
    mock_articles.append(new_article)
    next_article_id += 1
    
    return ArticleResponse(**new_article)

@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int):
    """Get a specific article by ID."""
    article = next((a for a in mock_articles if a["id"] == article_id), None)
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Increment view count
    article["views"] += 1
    
    return ArticleResponse(**article)

@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(article_id: int, article_update: ArticleUpdate):
    """Update an existing article."""
    current_user = get_current_user()
    
    article = next((a for a in mock_articles if a["id"] == article_id), None)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Update fields
    if article_update.title is not None:
        article["title"] = article_update.title
        article["slug"] = slugify(article_update.title)
    
    if article_update.content is not None:
        article["content"] = article_update.content
        article["word_count"] = count_words(article_update.content)
        article["read_time"] = calculate_read_time(article_update.content)
    
    if article_update.summary is not None:
        article["summary"] = article_update.summary
    
    if article_update.tags is not None:
        article["tags"] = article_update.tags
    
    if article_update.status is not None:
        old_status = article["status"]
        article["status"] = article_update.status
        
        # Set published_at if publishing for the first time
        if article_update.status == "published" and old_status != "published":
            article["published_at"] = datetime.utcnow()
    
    if article_update.featured_image_url is not None:
        article["featured_image_url"] = article_update.featured_image_url
    
    if article_update.meta_description is not None:
        article["meta_description"] = article_update.meta_description
    
    # Update version and timestamp
    article["version"] += 1
    article["updated_at"] = datetime.utcnow()
    
    return ArticleResponse(**article)

@router.put("/{article_id}/publish", response_model=ArticleResponse)
async def publish_article(article_id: int):
    """Publish an article."""
    article = next((a for a in mock_articles if a["id"] == article_id), None)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Change status to published
    old_status = article["status"]
    article["status"] = "published"
    article["updated_at"] = datetime.utcnow()
    
    # Set published_at if publishing for the first time
    if old_status != "published":
        article["published_at"] = datetime.utcnow()
    
    return ArticleResponse(**article)

@router.put("/{article_id}/unpublish", response_model=ArticleResponse)
async def unpublish_article(article_id: int):
    """Unpublish an article (set to draft)."""
    article = next((a for a in mock_articles if a["id"] == article_id), None)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Change status to draft
    article["status"] = "draft"
    article["updated_at"] = datetime.utcnow()
    
    return ArticleResponse(**article)

@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: int):
    """Delete an article."""
    article_index = next((i for i, a in enumerate(mock_articles) if a["id"] == article_id), None)
    if article_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    mock_articles.pop(article_index)

@router.get("/{article_id}/versions")
async def get_article_versions(article_id: int):
    """Get all versions of an article - placeholder."""
    return {"message": f"Versions for article {article_id} - to be implemented"}

# Initialize with sample data
def init_sample_data():
    """Initialize with sample articles for testing."""
    global next_article_id
    
    sample_articles = [
        {
            "title": "The Future of AI in Journalism",
            "content": "<h1>The Future of AI in Journalism</h1><p>Artificial intelligence is revolutionizing the way we create, distribute, and consume news content.</p><p>From automated fact-checking to personalized news feeds, AI technologies are reshaping the journalism landscape.</p>",
            "summary": "Exploring how AI is transforming journalism and the implications for the future of news media.",
            "status": "published",
            "tags": ["AI", "journalism", "technology"]
        },
        {
            "title": "Understanding Climate Change Data",
            "content": "<h1>Understanding Climate Change Data</h1><p>Climate change data can be overwhelming, but understanding the key metrics is crucial for informed reporting.</p>",
            "summary": "A guide to interpreting climate data for accurate journalism.",
            "status": "draft",
            "tags": ["climate", "data", "environment"]
        }
    ]
    
    current_user = get_current_user()
    
    for sample in sample_articles:
        slug = slugify(sample["title"])
        word_count = count_words(sample["content"])
        read_time = calculate_read_time(sample["content"])
        now = datetime.utcnow()
        published_at = now if sample["status"] == "published" else None
        
        new_article = {
            "id": next_article_id,
            "title": sample["title"],
            "slug": slug,
            "content": sample["content"],
            "summary": sample["summary"],
            "author_id": current_user["id"],
            "author_name": current_user["full_name"],
            "status": sample["status"],
            "featured_image_url": None,
            "meta_description": None,
            "word_count": word_count,
            "read_time": read_time,
            "views": 0,
            "version": 1,
            "tags": sample["tags"],
            "created_at": now,
            "updated_at": now,
            "published_at": published_at
        }
        
        mock_articles.append(new_article)
        next_article_id += 1

# Initialize sample data
init_sample_data()