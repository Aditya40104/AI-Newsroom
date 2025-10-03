"""
Clean AI service using ONLY Groq API - no templates
"""
import os
import requests
import json
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

class ArticleRequest(BaseModel):
    topic: str
    keywords: List[str] = []
    tone: str = "professional"
    length: str = "medium"

class ArticleResponse(BaseModel):
    title: str
    content: str
    summary: str
    suggested_tags: List[str]
    suggested_images: List[dict] = []

class RewriteRequest(BaseModel):
    content: str
    style: str = "improve"

class HeadlineRequest(BaseModel):
    content: str
    count: int = 5

def call_groq_api(prompt: str, max_tokens: int = 800) -> str:
    """Call Groq API - REAL AI ONLY"""
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="Groq API key not configured")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        print(f"🔄 Calling Groq API...")
        response = requests.post(url, headers=headers, json=payload, timeout=45)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print("✅ REAL AI CONTENT GENERATED!")
            return content.strip()
        else:
            error_text = response.text
            print(f"❌ Groq API Error {response.status_code}: {error_text}")
            raise HTTPException(status_code=500, detail=f"Groq API failed: {error_text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/generate_article", response_model=ArticleResponse)
async def generate_article(request: ArticleRequest):
    """Generate article using ONLY Groq AI"""
    
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")
    
    keywords_text = f" focusing on: {', '.join(request.keywords)}" if request.keywords else ""
    
    prompt = f"""You are a professional journalist. Write a complete news article about: {request.topic}{keywords_text}

Requirements:
- Write in {request.tone} tone
- Length: {request.length} (short=2-3 paragraphs, medium=4-5 paragraphs, long=6-8 paragraphs)
- Include an engaging headline as the first line
- Write informative, well-structured content
- Use proper journalistic style

Format your response as:
HEADLINE: [Your headline here]

[Article content with proper paragraphs]"""

    ai_content = call_groq_api(prompt, max_tokens=1000)
    
    # Parse response
    lines = [line.strip() for line in ai_content.split('\n') if line.strip()]
    
    title = request.topic.title()  # Default
    content = ai_content
    
    # Extract headline if formatted correctly
    if lines and lines[0].startswith('HEADLINE:'):
        title = lines[0].replace('HEADLINE:', '').strip()
        content = '\n\n'.join(lines[1:])
    elif lines and len(lines[0]) < 100:  # First line looks like a title
        title = lines[0]
        content = '\n\n'.join(lines[1:])
    
    # Generate summary
    summary_prompt = f"Write a 1-sentence summary of this article: {content[:500]}"
    summary = call_groq_api(summary_prompt, max_tokens=100)
    
    # Generate tags
    tags = [request.topic.lower().replace(" ", "-")]
    if request.keywords:
        tags.extend([kw.lower().replace(" ", "-") for kw in request.keywords[:3]])
    tags.extend(["news", "ai-generated"])
    
    # Auto-generate images
    suggested_images = []
    try:
        from app.image_gen import search_unsplash_images
        
        # Use topic + first keyword for image search
        image_query = request.topic
        if request.keywords:
            image_query = f"{request.topic} {request.keywords[0]}"
        
        print(f"🖼️  Auto-generating images for: {image_query}")
        images = search_unsplash_images(image_query, 3)
        suggested_images = images
        
        print(f"✅ Auto-generated {len(suggested_images)} images")
    except Exception as e:
        print(f"⚠️  Image generation failed: {e}")
    
    return ArticleResponse(
        title=title,
        content=content,
        summary=summary,
        suggested_tags=list(set(tags)),
        suggested_images=suggested_images
    )

@router.post("/rewrite_content")
async def rewrite_content(request: RewriteRequest):
    """Rewrite content using ONLY Groq AI"""
    
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Content is required")
    
    style_prompts = {
        "improve": "Improve this text for better clarity, flow, and engagement:",
        "formal": "Rewrite this text in a formal, professional style:",
        "casual": "Rewrite this text in a casual, conversational style:",
        "concise": "Make this text more concise while keeping key information:"
    }
    
    instruction = style_prompts.get(request.style, "Improve this text:")
    prompt = f"{instruction}\n\n{request.content}\n\nRewritten version:"
    
    rewritten = call_groq_api(prompt, max_tokens=800)
    
    return {"rewritten_content": rewritten}

@router.post("/generate_headlines")
async def generate_headlines(request: HeadlineRequest):
    """Generate headlines using ONLY Groq AI"""
    
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Content is required")
    
    prompt = f"""Generate {request.count} engaging, attention-grabbing headlines for this article:

{request.content[:400]}...

Requirements:
- Make them news-style headlines
- Each should be compelling and accurate
- Vary the style and approach
- Keep under 100 characters each

Format as a numbered list:
1. [Headline 1]
2. [Headline 2]
etc."""

    ai_response = call_groq_api(prompt, max_tokens=400)
    
    # Parse headlines
    headlines = []
    for line in ai_response.split('\n'):
        line = line.strip()
        if line and any(line.startswith(f"{i}.") for i in range(1, 10)):
            # Remove numbering
            headline = line.split('.', 1)[1].strip()
            if headline:
                headlines.append(headline)
    
    # Ensure we have at least some headlines
    if not headlines:
        headlines = [f"Breaking News: Latest Developments"]
    
    return {"headlines": headlines[:request.count]}

print("🤖 AI service initialized - Groq API ONLY mode")