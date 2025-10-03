-- Initialize AI Newsroom database
CREATE DATABASE IF NOT EXISTS newsroom_db;
USE newsroom_db;

-- Create extension for UUID generation (PostgreSQL)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users will be created by SQLAlchemy models
-- This file is mainly for any initial data or manual setup

-- Insert default admin user (optional - can be done through registration)
-- INSERT INTO users (email, username, full_name, hashed_password, role, is_active, is_verified, created_at)
-- VALUES (
--   'admin@newsroom.com',
--   'admin',
--   'System Administrator',
--   '$2b$12$LQv3c1yqBWVHxkd0LQ4YCOdtnCXMwrODvYGpGpxrde8YQwMjNLvlO', -- password: "admin123"
--   'admin',
--   true,
--   true,
--   NOW()
-- );

-- Create indexes for better performance (will be handled by SQLAlchemy)
-- CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
-- CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
-- CREATE INDEX IF NOT EXISTS idx_articles_author ON articles(author_id);
-- CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
-- CREATE INDEX IF NOT EXISTS idx_articles_created ON articles(created_at);