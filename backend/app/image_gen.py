"""
Image generation and captioning service using Unsplash API
"""
import os
import requests
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ImageRequest(BaseModel):
    query: str
    count: int = 3

class ImageResult(BaseModel):
    url: str
    thumbnail_url: str
    caption: str
    alt_description: str
    photographer: str
    photographer_url: str

class ImageResponse(BaseModel):
    images: List[ImageResult]
    query: str

def search_unsplash_images(query: str, count: int = 3) -> List[Dict[str, Any]]:
    """Search Unsplash for relevant images"""
    
    # Unsplash API key
    api_key = os.getenv('UNSPLASH_ACCESS_KEY', 'Ql4_l5s9pLC0MkCPMEVDflelbLObhCOjSY8LJoMSaOg')
    
    if not api_key:
        return []
    
    try:
        url = "https://api.unsplash.com/search/photos"
        headers = {
            "Authorization": f"Client-ID {api_key}",
            "Accept-Version": "v1"
        }
        
        params = {
            "query": query,
            "per_page": count,
            "orientation": "landscape",  # Better for articles
            "content_filter": "high",   # Safe content only
            "order_by": "relevance"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            images = []
            
            for photo in data.get("results", []):
                # Generate smart caption
                caption = generate_smart_caption(photo, query)
                
                images.append({
                    "url": photo["urls"]["regular"],
                    "thumbnail_url": photo["urls"]["thumb"],
                    "caption": caption,
                    "alt_description": photo.get("alt_description", f"Image related to {query}"),
                    "photographer": photo["user"]["name"],
                    "photographer_url": photo["user"]["links"]["html"]
                })
            
            print(f"✅ Found {len(images)} images for '{query}'")
            return images
            
        else:
            print(f"❌ Unsplash API error {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error searching images for '{query}': {e}")
        return []

def generate_smart_caption(photo_data: Dict, query: str) -> str:
    """Generate intelligent caption for the image"""
    
    # Get description from Unsplash
    description = photo_data.get("alt_description", "")
    photo_description = photo_data.get("description", "")
    
    # Use the best available description
    if photo_description:
        base_caption = photo_description
    elif description:
        base_caption = description
    else:
        base_caption = f"Image depicting {query}"
    
    # Make it news-appropriate
    if len(base_caption) > 100:
        base_caption = base_caption[:97] + "..."
    
    # Add photographer credit
    photographer = photo_data["user"]["name"]
    
    return f"{base_caption}. Photo by {photographer} on Unsplash."

def extract_image_keywords_from_content(content: str) -> str:
    """Extract the best keywords for image search from article content"""
    
    # Get the title or first sentence as main topic
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('<'):
            # Clean up HTML if present
            import re
            clean_line = re.sub(r'<[^>]+>', '', line)
            if len(clean_line) > 10:
                return clean_line[:50]  # Use first meaningful line
    
    return "news article"

@router.post("/generate_image", response_model=ImageResponse)
async def generate_image(request: ImageRequest):
    """Generate relevant images for article content"""
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query is required")
    
    print(f"🖼️  Searching images for: '{request.query}'")
    
    # Search for images
    images = search_unsplash_images(request.query, request.count)
    
    if not images:
        # Fallback to generic terms if specific search fails
        fallback_terms = ["news", "journalism", "article", "information"]
        for term in fallback_terms:
            images = search_unsplash_images(term, request.count)
            if images:
                print(f"📸 Using fallback images for '{term}'")
                break
    
    # Convert to response format
    image_results = [
        ImageResult(
            url=img["url"],
            thumbnail_url=img["thumbnail_url"],
            caption=img["caption"],
            alt_description=img["alt_description"],
            photographer=img["photographer"],
            photographer_url=img["photographer_url"]
        )
        for img in images
    ]
    
    return ImageResponse(
        images=image_results,
        query=request.query
    )

print("🖼️  Image generation service initialized (Unsplash)")