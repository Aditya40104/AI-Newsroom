"""
Database models for the AI Newsroom application.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
import uuid

from app.database import Base


class UserRole(str, Enum):
    """User roles in the system"""
    WRITER = "writer"
    EDITOR = "editor"
    ADMIN = "admin"


class ArticleStatus(str, Enum):
    """Article publication status"""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class User(Base):
    """User model for authentication and profile management"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    
    # Profile information
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.WRITER, nullable=False)
    
    # OAuth information
    google_id = Column(String(100), nullable=True)
    github_id = Column(String(100), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    articles = relationship("Article", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    article_versions = relationship("ArticleVersion", back_populates="author", cascade="all, delete-orphan")


class Article(Base):
    """Main article model"""
    
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    slug = Column(String(500), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    
    # Metadata
    tags = Column(JSON, default=list)  # List of string tags
    category = Column(String(100), nullable=True)
    featured_image_url = Column(String(500), nullable=True)
    
    # Status and publication
    status = Column(SQLEnum(ArticleStatus), default=ArticleStatus.DRAFT, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # SEO and social media
    meta_description = Column(String(500), nullable=True)
    social_image_url = Column(String(500), nullable=True)
    
    # Analytics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    # AI generation metadata
    ai_generated = Column(Boolean, default=False)
    ai_model_used = Column(String(100), nullable=True)
    generation_prompt = Column(Text, nullable=True)
    
    # Fact-checking
    fact_check_status = Column(String(50), default="pending")  # pending, verified, disputed
    fact_check_score = Column(Integer, nullable=True)  # 0-100
    
    # Foreign keys
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("User", back_populates="articles")
    versions = relationship("ArticleVersion", back_populates="article", cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="article", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")
    images = relationship("ArticleImage", back_populates="article", cascade="all, delete-orphan")


class ArticleVersion(Base):
    """Article version history for change tracking"""
    
    __tablename__ = "article_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    version_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    
    # Change metadata
    change_summary = Column(String(500), nullable=True)
    is_major_revision = Column(Boolean, default=False)
    
    # Foreign keys
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    article = relationship("Article", back_populates="versions")
    author = relationship("User", back_populates="article_versions")


class Citation(Base):
    """Citations and sources for articles"""
    
    __tablename__ = "citations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    author = Column(String(255), nullable=True)
    publication_date = Column(DateTime, nullable=True)
    publisher = Column(String(255), nullable=True)
    
    # Citation metadata
    citation_style = Column(String(50), default="APA")  # APA, MLA, Chicago, etc.
    page_number = Column(String(50), nullable=True)
    access_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Credibility scoring
    credibility_score = Column(Integer, nullable=True)  # 0-100
    source_type = Column(String(100), nullable=True)  # news, academic, blog, etc.
    
    # Position in article
    position_in_text = Column(Integer, nullable=True)
    context_snippet = Column(Text, nullable=True)
    
    # Foreign keys
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    article = relationship("Article", back_populates="citations")


class Comment(Base):
    """Comments and feedback on articles"""
    
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    
    # Comment type
    comment_type = Column(String(50), default="comment")  # comment, suggestion, fact_check
    
    # Position reference (for inline comments)
    text_position = Column(Integer, nullable=True)
    selected_text = Column(Text, nullable=True)
    
    # Status
    is_resolved = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    
    # Foreign keys
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)  # For replies
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    article = relationship("Article", back_populates="comments")
    author = relationship("User", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side=[id])


class ArticleImage(Base):
    """Images associated with articles"""
    
    __tablename__ = "article_images"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(1000), nullable=False)
    alt_text = Column(String(500), nullable=True)
    caption = Column(Text, nullable=True)
    
    # Image metadata
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # AI generation metadata
    ai_generated = Column(Boolean, default=False)
    generation_prompt = Column(Text, nullable=True)
    generation_model = Column(String(100), nullable=True)
    
    # Position and usage
    position_in_article = Column(Integer, nullable=True)
    is_featured = Column(Boolean, default=False)
    
    # Foreign keys
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    article = relationship("Article", back_populates="images")


class NewsSource(Base):
    """Trusted news sources for fact-checking"""
    
    __tablename__ = "news_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    domain = Column(String(255), nullable=False, unique=True)
    
    # Source credibility
    credibility_rating = Column(Integer, default=50)  # 0-100
    bias_rating = Column(String(50), nullable=True)  # left, center, right
    factual_reporting = Column(String(50), nullable=True)  # high, mixed, low
    
    # API integration
    api_endpoint = Column(String(500), nullable=True)
    api_key_required = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AgentTask(Base):
    """Tasks for AI agents (research, writing, fact-checking, etc.)"""
    
    __tablename__ = "agent_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(50), nullable=False)  # research, writing, fact_check, edit
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    
    # Task data
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Progress tracking
    progress_percentage = Column(Integer, default=0)
    estimated_completion = Column(DateTime(timezone=True), nullable=True)
    
    # Agent information
    agent_name = Column(String(100), nullable=False)
    agent_version = Column(String(50), nullable=True)
    
    # Foreign keys (optional - task might not be associated with specific article)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")
    article = relationship("Article")