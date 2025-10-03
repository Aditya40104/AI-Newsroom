"""
Article and related models for the AI Newsroom platform.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), default="writer")  # writer, editor, admin
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String(500))
    bio = Column(Text)
    website_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    articles = relationship("Article", back_populates="author", cascade="all, delete-orphan")
    article_versions = relationship("ArticleVersion", back_populates="author")
    comments = relationship("Comment", back_populates="author")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    slug = Column(String(500), unique=True, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    
    # Article metadata
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="draft", index=True)  # draft, published, archived
    featured_image_url = Column(String(500))
    meta_description = Column(String(500))
    
    # SEO and content metrics
    word_count = Column(Integer, default=0)
    read_time = Column(Integer, default=0)  # in minutes
    views = Column(Integer, default=0)
    
    # Versioning
    version = Column(Integer, default=1)
    
    # Tags as JSON string for simplicity
    tags_json = Column(Text)  # JSON array of tags
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, index=True)
    
    # Relationships
    author = relationship("User", back_populates="articles")
    versions = relationship("ArticleVersion", back_populates="article", cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="article", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_article_author_status', 'author_id', 'status'),
        Index('idx_article_status_published', 'status', 'published_at'),
    )

    @property
    def tags(self):
        """Parse tags from JSON string."""
        if self.tags_json:
            try:
                return json.loads(self.tags_json)
            except json.JSONDecodeError:
                return []
        return []
    
    @tags.setter
    def tags(self, value):
        """Store tags as JSON string."""
        if value:
            self.tags_json = json.dumps(value)
        else:
            self.tags_json = None

    @property
    def author_name(self):
        """Get author's full name."""
        return self.author.full_name if self.author else "Unknown"


class ArticleVersion(Base):
    __tablename__ = "article_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    
    # Version content
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    tags_json = Column(Text)
    
    # Version metadata
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_summary = Column(String(500))  # Brief description of changes
    word_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    article = relationship("Article", back_populates="versions")
    author = relationship("User", back_populates="article_versions")
    
    # Indexes
    __table_args__ = (
        Index('idx_version_article_number', 'article_id', 'version_number'),
    )

    @property
    def tags(self):
        """Parse tags from JSON string."""
        if self.tags_json:
            try:
                return json.loads(self.tags_json)
            except json.JSONDecodeError:
                return []
        return []


class Citation(Base):
    __tablename__ = "citations"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    
    # Citation details
    title = Column(String(500))
    url = Column(String(1000), nullable=False)
    source_name = Column(String(200))
    author_name = Column(String(200))
    publication_date = Column(DateTime)
    access_date = Column(DateTime, default=datetime.utcnow)
    
    # Citation context
    quote = Column(Text)  # Direct quote if any
    context = Column(Text)  # Context within the article
    
    # Metadata
    citation_type = Column(String(50))  # web, book, journal, interview, etc.
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    article = relationship("Article", back_populates="citations")


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Comment content
    content = Column(Text, nullable=False)
    
    # Comment threading
    parent_id = Column(Integer, ForeignKey("comments.id"))
    
    # Moderation
    is_approved = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    article = relationship("Article", back_populates="comments")
    author = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")
    
    # Indexes
    __table_args__ = (
        Index('idx_comment_article_created', 'article_id', 'created_at'),
    )