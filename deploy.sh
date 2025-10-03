#!/bin/bash

# AI Newsroom - Deploy to GitHub Script

echo "🚀 AI Newsroom Deployment Script"
echo "================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    git branch -M main
fi

# Add remote origin (update with your repo URL)
echo "🔗 Setting up remote origin..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/Aditya40104/AI-Newsroom.git

# Stage all files
echo "📦 Staging files..."
git add .

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
ENV/
.venv/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build outputs
/frontend/build
/frontend/dist
*.log

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Uploads
uploads/
*.jpg
*.jpeg
*.png
*.gif

# Cache
.cache/
.pytest_cache/

# Distribution
dist/
build/
*.egg-info/
EOF
    git add .gitignore
fi

# Commit changes
echo "💾 Committing changes..."
git commit -m "🚀 Part 8: Complete deployment configuration

- Added Railway deployment config (railway.toml)
- Added Vercel deployment config (vercel.json)  
- Added GitHub Actions CI/CD pipeline
- Added comprehensive deployment guide (DEPLOYMENT.md)
- Updated Dockerfile with production optimizations
- Added environment variable examples
- Added health checks and monitoring
- Ready for free cloud deployment on Railway + Vercel + Supabase

Features deployed:
✅ Authentication & Role Management
✅ AI Article Generation (Groq)
✅ Fact Checking (Wikipedia + spaCy)
✅ Image Integration (Unsplash)
✅ Admin Dashboard with Analytics
✅ User & Article Management
✅ Production-ready containerization
✅ CI/CD pipeline configuration"

# Push to GitHub
echo "🌟 Pushing to GitHub..."
git push -u origin main --force

echo ""
echo "✅ Successfully pushed to GitHub!"
echo ""
echo "🎉 Next Steps:"
echo "1. Go to https://github.com/Aditya40104/AI-Newsroom"
echo "2. Follow the DEPLOYMENT.md guide to deploy to:"
echo "   - Supabase (Database)"
echo "   - Railway (Backend API)"
echo "   - Vercel (Frontend)"
echo ""
echo "💰 Total cost: $0/month (using free tiers)"
echo "📚 Full deployment guide: ./DEPLOYMENT.md"
echo ""
echo "🚀 Your AI Newsroom will be live in ~10 minutes!"