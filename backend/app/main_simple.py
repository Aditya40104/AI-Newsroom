"""
FastAPI application entry point - Simplified for testing.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI application
app = FastAPI(
    title="AI Newsroom Collaboration Tool",
    description="A collaborative platform for AI-powered journalism",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Newsroom API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is operational"}

# Include routers
from app.routers.auth_simple import router as auth_router
from app.routers.articles_simple import router as articles_router
from app.ai_clean import router as ai_router
from app.fact_check import router as fact_check_router
from app.image_gen import router as image_router
from app.admin import router as admin_router

app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(articles_router, prefix="/api/articles", tags=["articles"])
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
app.include_router(fact_check_router, prefix="/api/fact-check", tags=["fact-check"])
app.include_router(image_router, prefix="/api/ai", tags=["images"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)