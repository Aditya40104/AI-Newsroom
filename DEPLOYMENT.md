# 🚀 AI Newsroom Deployment Guide

This guide will help you deploy your AI Newsroom to the cloud using **100% FREE** services!

## 📋 Prerequisites

1. GitHub account
2. Vercel account (free)
3. Railway account (free)
4. Supabase account (free)

## 🏗️ Architecture

- **Frontend**: Vercel (React app)
- **Backend**: Railway (FastAPI)
- **Database**: Supabase (PostgreSQL)
- **CI/CD**: GitHub Actions

## 🛠️ Step-by-Step Deployment

### 1. Setup Supabase Database

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Go to Settings → Database and copy your connection string
4. In the SQL Editor, run these commands to create tables:

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'writer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Articles table
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    summary VARCHAR(1000),
    author_id INTEGER REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP
);

-- Fact checks table
CREATE TABLE fact_checks (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    claim TEXT NOT NULL,
    verdict VARCHAR(100),
    confidence_score FLOAT,
    sources TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Deploy Backend to Railway

1. Go to [railway.app](https://railway.app) and sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub account and select this repository
4. Railway will auto-detect the `railway.toml` configuration
5. Add these environment variables in Railway dashboard:
   - `DATABASE_URL`: Your Supabase connection string
   - `GROQ_API_KEY`: Your Groq API key
   - `UNSPLASH_ACCESS_KEY`: Your Unsplash API key
   - `JWT_SECRET_KEY`: Generate a random secret key
   - `FRONTEND_URL`: Will be your Vercel URL (add later)

### 3. Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and sign up with GitHub
2. Click "New Project" → Import your GitHub repository
3. Set the root directory to `frontend`
4. Add environment variables:
   - `REACT_APP_API_URL`: Your Railway backend URL
5. Deploy!

### 4. Configure Domain and CORS

1. Copy your Vercel frontend URL
2. Go back to Railway and update the `FRONTEND_URL` environment variable
3. Redeploy the backend

### 5. Setup CI/CD (Optional)

1. In your GitHub repository, go to Settings → Secrets and variables → Actions
2. Add these secrets:
   - `RAILWAY_TOKEN`: Get from Railway dashboard
   - `VERCEL_TOKEN`: Get from Vercel dashboard
   - `ORG_ID`: Your Vercel organization ID
   - `PROJECT_ID`: Your Vercel project ID

## 🔑 API Keys Setup

### Groq API Key
1. Go to [console.groq.com](https://console.groq.com)
2. Create account and generate API key
3. **Free tier**: 100 requests/day

### Unsplash API Key
1. Go to [unsplash.com/developers](https://unsplash.com/developers)
2. Create new application
3. **Free tier**: 50 requests/hour

## 💰 Cost Breakdown

| Service | Free Tier | Paid Starts At |
|---------|-----------|----------------|
| Vercel | 100GB bandwidth/month | $20/month |
| Railway | 512MB RAM, 1GB disk | $5/month |
| Supabase | 500MB database, 2GB bandwidth | $25/month |
| **Total** | **$0/month** | **$50/month** |

## 🔧 Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend  
cd frontend
npm install
npm start
```

## 🐛 Troubleshooting

### Common Issues:

1. **CORS Errors**: Make sure `FRONTEND_URL` is set correctly in Railway
2. **Database Connection**: Check Supabase connection string format
3. **API Keys**: Verify all API keys are active and have correct permissions
4. **Build Failures**: Check logs in Railway/Vercel dashboards

### Debug Commands:

```bash
# Check backend health
curl https://your-railway-app.railway.app/health

# Check database connection
curl https://your-railway-app.railway.app/api/auth/test
```

## 📱 Features Deployed

✅ User Authentication (Register/Login)  
✅ Role-based Access (Admin/Editor/Writer)  
✅ AI Article Generation (Groq)  
✅ Fact Checking (Wikipedia + spaCy)  
✅ Image Integration (Unsplash)  
✅ Admin Dashboard  
✅ Article Management  
✅ User Management  
✅ Analytics Dashboard  

## 🎉 Go Live!

Once deployed, your AI Newsroom will be live at:
- **Frontend**: `https://your-app.vercel.app`
- **Backend API**: `https://your-app.railway.app`

## 🔒 Security Notes

- Change default JWT secret in production
- Enable HTTPS only in production
- Set up proper CORS policies
- Monitor API usage to stay within free tiers

## 📈 Scaling

When you outgrow free tiers:
1. Upgrade Railway for more resources
2. Consider Vercel Pro for better performance
3. Upgrade Supabase for larger database
4. Add Redis for caching (Railway add-on)

---

**Need help?** Check the logs in Railway and Vercel dashboards for detailed error messages.

**Ready to scale?** The architecture supports easy upgrades to paid tiers when needed.