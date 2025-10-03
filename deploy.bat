@echo off
echo 🚀 AI Newsroom Deployment Script
echo ================================

REM Check if git is initialized
if not exist ".git" (
    echo 📁 Initializing Git repository...
    git init
    git branch -M main
)

REM Add remote origin
echo 🔗 Setting up remote origin...
git remote remove origin 2>nul
git remote add origin https://github.com/Aditya40104/AI-Newsroom.git

REM Stage all files
echo 📦 Staging files...
git add .

REM Create .gitignore if it doesn't exist
if not exist ".gitignore" (
    echo 📝 Creating .gitignore...
    (
        echo # Dependencies
        echo node_modules/
        echo __pycache__/
        echo *.pyc
        echo *.pyo
        echo *.pyd
        echo .Python
        echo env/
        echo venv/
        echo ENV/
        echo .venv/
        echo.
        echo # Environment variables
        echo .env
        echo .env.local
        echo .env.development.local
        echo .env.test.local
        echo .env.production.local
        echo.
        echo # Build outputs
        echo /frontend/build
        echo /frontend/dist
        echo *.log
        echo.
        echo # Database
        echo *.db
        echo *.sqlite
        echo *.sqlite3
        echo.
        echo # IDE
        echo .vscode/
        echo .idea/
        echo *.swp
        echo *.swo
        echo.
        echo # OS
        echo .DS_Store
        echo Thumbs.db
        echo.
        echo # Uploads
        echo uploads/
        echo *.jpg
        echo *.jpeg
        echo *.png
        echo *.gif
        echo.
        echo # Cache
        echo .cache/
        echo .pytest_cache/
        echo.
        echo # Distribution
        echo dist/
        echo build/
        echo *.egg-info/
    ) > .gitignore
    git add .gitignore
)

REM Commit changes
echo 💾 Committing changes...
git commit -m "🚀 Part 8: Complete deployment configuration - Added Railway deployment config (railway.toml) - Added Vercel deployment config (vercel.json) - Added GitHub Actions CI/CD pipeline - Added comprehensive deployment guide (DEPLOYMENT.md) - Updated Dockerfile with production optimizations - Added environment variable examples - Added health checks and monitoring - Ready for free cloud deployment on Railway + Vercel + Supabase"

REM Push to GitHub
echo 🌟 Pushing to GitHub...
git push -u origin main --force

echo.
echo ✅ Successfully pushed to GitHub!
echo.
echo 🎉 Next Steps:
echo 1. Go to https://github.com/Aditya40104/AI-Newsroom
echo 2. Follow the DEPLOYMENT.md guide to deploy to:
echo    - Supabase (Database)
echo    - Railway (Backend API)
echo    - Vercel (Frontend)
echo.
echo 💰 Total cost: $0/month (using free tiers)
echo 📚 Full deployment guide: ./DEPLOYMENT.md
echo.
echo 🚀 Your AI Newsroom will be live in ~10 minutes!
pause