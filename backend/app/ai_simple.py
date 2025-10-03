"""
AI service for article generation using free APIs
"""
import os
import requests
import json
from typing import Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Free AI API configuration
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Initialize API clients
huggingface_headers = {
    "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"
}

def query_free_ai(prompt: str, max_length: int = 500) -> str:
    """Query Groq API for real AI content generation - NO FALLBACKS"""
    
    groq_api_key = os.getenv('GROQ_API_KEY')
    
    if not groq_api_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        return None
    
    try:
        groq_url = "https://api.groq.com/openai/v1/chat/completions"
        groq_headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }
        
        # Use the best available Groq model
        groq_payload = {
            "model": "llama3-8b-8192",  # Fast and good quality
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a professional journalist and content writer. Create engaging, original, and well-structured content."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": max_length,
            "temperature": 0.8,  # Good balance of creativity and coherence
            "top_p": 0.9,
            "stream": False
        }
        
        print(f"🚀 Sending request to Groq API...")
        response = requests.post(groq_url, headers=groq_headers, json=groq_payload, timeout=30)
        
        print(f"📡 Groq API response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                
                if content and len(content.strip()) > 50:
                    print(f"✅ Successfully generated {len(content)} characters using Groq Llama3")
                    return content.strip()
                else:
                    print("❌ Groq returned empty or very short content")
                    return None
            else:
                print("❌ Groq response missing 'choices' field")
                return None
                
        elif response.status_code == 401:
            print("❌ Groq API authentication failed - check your API key")
            return None
        elif response.status_code == 429:
            print("❌ Groq API rate limit exceeded - please wait and try again")
            return None
        else:
            print(f"❌ Groq API error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Groq API request timed out")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to Groq API - check internet connection")
        return None
    except Exception as e:
        print(f"❌ Unexpected Groq API error: {str(e)}")
        return None

class ArticleRequest(BaseModel):
    topic: str
    keywords: List[str] = []
    tone: str = "professional"  # professional, casual, formal
    length: str = "medium"  # short, medium, long

class ArticleResponse(BaseModel):
    title: str
    content: str
    summary: str
    suggested_tags: List[str]

class RewriteRequest(BaseModel):
    content: str
    style: str = "improve"  # improve, formal, casual, concise

class HeadlineRequest(BaseModel):
    content: str
    count: int = 5

def initialize_free_ai():
    """Initialize free AI services"""
    try:
        # Test Hugging Face API
        test_response = requests.get("https://api-inference.huggingface.co/models/gpt2", timeout=5)
        if test_response.status_code in [200, 503]:  # 503 means model is loading
            print("Free AI services initialized successfully")
            return True
    except Exception as e:
        print(f"Free AI initialization warning: {e}")
    
    return True  # Always return True as we have fallbacks

# Mock article generation removed - using ONLY Groq API

@router.post("/generate_article", response_model=ArticleResponse)
async def generate_article(request: ArticleRequest):
    """Generate an article using ONLY Groq AI - no templates or fallbacks"""
    
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")
    
    # Prepare keywords text
    keywords_text = f"Focus on these key aspects: {', '.join(request.keywords)}." if request.keywords else ""
    
    # Length instructions
    length_instruction = {
        "short": "Write a concise 2-3 paragraph news article",
        "medium": "Write a comprehensive 4-5 paragraph news article", 
        "long": "Write a detailed 6-8 paragraph investigative article"
    }.get(request.length, "Write a comprehensive 4-5 paragraph news article")
    
    # Tone instructions
    tone_instruction = {
        "professional": "Use professional, authoritative journalism style with credible sources and balanced reporting",
        "casual": "Use conversational, accessible language that engages general readers while maintaining journalistic integrity",
        "formal": "Use formal, academic writing style with precise terminology and scholarly approach"
    }.get(request.tone, "Use professional journalism style")
    
    # Create sophisticated prompt for Groq API
    prompt = f"""You are an award-winning journalist writing for a major international news publication. Create an original, engaging news article about: {request.topic}

{keywords_text}

Article Requirements:
- {length_instruction}
- {tone_instruction}
- Create a compelling, clickable headline
- Start with a strong lead paragraph that captures the essence of the story
- Include specific details, quotes, and context where appropriate
- Use proper journalistic structure with smooth transitions between paragraphs
- Make it informative, engaging, and newsworthy
- Ensure the content is original and not repetitive

Format: Start with the headline on the first line, then the article body.

Write the complete article now:"""
    
    # Query Groq API ONLY
    ai_response = query_free_ai(prompt, max_length=1000)
    
    if ai_response and len(ai_response.strip()) > 100:
        print("✅ Successfully generated article using Groq AI")
        
        # Parse the AI response
        lines = [line.strip() for line in ai_response.strip().split('\n') if line.strip()]
        
        if not lines:
            raise HTTPException(status_code=500, detail="AI generated empty response")
        
        # Extract headline (first substantial line)
        title = lines[0] if lines else f"Breaking News: {request.topic}"
        
        # Extract content (remaining lines)
        content_lines = lines[1:] if len(lines) > 1 else lines
        content = '\n\n'.join(content_lines) if content_lines else ai_response
        
        # Ensure we have substantial content
        if len(content.strip()) < 100:
            content = ai_response  # Use full response if parsing failed
        
        # Generate intelligent summary from AI content
        first_sentence = content.split('.')[0] + '.' if '.' in content else content[:100] + '...'
        summary = first_sentence
        
        # Generate contextual tags
        topic_words = request.topic.lower().split()
        tags = [word.replace(" ", "-") for word in topic_words if len(word) > 3]
        
        if request.keywords:
            tags.extend([kw.lower().replace(" ", "-") for kw in request.keywords[:3]])
        
        # Add appropriate news tags
        tags.extend(["breaking-news", "latest-updates", "analysis"])
        
        return ArticleResponse(
            title=title.strip(),
            content=content.strip(),
            summary=summary.strip(),
            suggested_tags=list(set(tags))  # Remove duplicates
        )
    
    # If Groq API fails completely, return error instead of template
    raise HTTPException(
        status_code=503, 
        detail="AI content generation service is currently unavailable. Please ensure your Groq API key is valid and try again."
    )


@router.post("/rewrite_content")
async def rewrite_content(request: RewriteRequest):
    """Rewrite existing content with different style using free AI"""
    
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Content is required")
    
    # Try free AI rewriting
    try:
        style_instructions = {
            "improve": "Improve this text for better clarity, flow, and engagement:",
            "formal": "Rewrite this text in a formal, professional style:",
            "casual": "Rewrite this text in a casual, conversational style:",
            "concise": "Make this text more concise while keeping the key information:"
        }
        
        instruction = style_instructions.get(request.style, "Improve this text:")
        prompt = f"{instruction}\n\n{request.content}\n\nRewritten version:"
        
        # Query free AI
        ai_response = query_free_ai(prompt, max_length=600)
        
        if ai_response and len(ai_response.strip()) > 20:
            # Clean up the response
            rewritten = ai_response.replace(prompt, '').strip()
            if rewritten:
                return {"rewritten_content": rewritten}
                
    except Exception as e:
        print(f"Free AI rewrite error: {e}")
    
    # If Groq API fails, return error instead of simple fallbacks
    raise HTTPException(
        status_code=503,
        detail="AI rewriting service is currently unavailable. Please ensure your Groq API key is valid and try again."
    )
    
    try:
        style_instructions = {
            "improve": "Improve the writing quality, clarity, and flow",
            "formal": "Rewrite in a formal, professional style",
            "casual": "Rewrite in a casual, conversational style", 
            "concise": "Make the content more concise while preserving key information"
        }
        
        instruction = style_instructions.get(request.style, "Improve the writing quality")
        
        prompt = f"""
        {instruction} of the following content:
        
        {request.content}
        
        Return only the rewritten content without additional commentary.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert editor and writing coach. Rewrite content according to the specified style while maintaining the core message."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        return {"rewritten_content": response.choices[0].message.content}
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return {"rewritten_content": request.content}

@router.post("/generate_headlines")
async def generate_headlines(request: HeadlineRequest):
    """Generate multiple headline suggestions for content using free AI"""
    
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Content is required")
    
    # Try free AI for headlines
    try:
        prompt = f"Generate 5 engaging news headlines for this article:\n\n{request.content[:300]}...\n\nHeadlines:"
        
        ai_response = query_free_ai(prompt, max_length=300)
        
        if ai_response:
            # Parse headlines from response
            lines = [line.strip() for line in ai_response.split('\n') if line.strip()]
            headlines = []
            
            for line in lines:
                # Clean up headline format
                if line and not line.startswith('Headlines:') and len(line) > 10:
                    # Remove numbering, bullets, etc.
                    clean_line = line.lstrip('0123456789.-•* ').strip()
                    if clean_line and len(clean_line) < 150:  # Reasonable headline length
                        headlines.append(clean_line)
            
            if len(headlines) >= 3:
                return {"headlines": headlines[:request.count]}
                
    except Exception as e:
        print(f"Free AI headlines error: {e}")
    
    # If Groq API fails, return error instead of fallback templates
    raise HTTPException(
        status_code=503,
        detail="AI headline generation service is currently unavailable. Please ensure your Groq API key is valid and try again."
    )

# Initialize free AI services on startup
initialize_free_ai()