"""
Fact-checking and research API using free services
"""
import os
import re
import requests
import spacy
import wikipedia
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import with fallbacks for optional dependencies
try:
    import spacy
    print("✅ spaCy imported")
except ImportError:
    spacy = None
    print("❌ spaCy not available")

try:
    import wikipedia
    print("✅ Wikipedia imported")
except ImportError:
    wikipedia = None
    print("❌ Wikipedia not available")

try:
    from newsapi import NewsApiClient
    print("✅ NewsAPI imported")
except ImportError:
    NewsApiClient = None
    print("❌ NewsAPI not available")

try:
    from transformers import pipeline
    print("✅ Transformers imported")
except ImportError:
    pipeline = None
    print("❌ Transformers not available")

router = APIRouter()

# Initialize services
try:
    nlp = spacy.load("en_core_web_sm")
    print("✅ spaCy English model loaded")
except:
    nlp = None
    print("❌ spaCy model not found")

# Initialize summarizer (using free Hugging Face model)
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    print("✅ Summarization model loaded")
except:
    summarizer = None
    print("❌ Summarization model failed to load")

# News API (free tier: 100 requests/day)
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'demo_key')  # You can get free key from newsapi.org
newsapi = NewsApiClient(api_key=NEWS_API_KEY) if NEWS_API_KEY != 'demo_key' else None

class FactCheckRequest(BaseModel):
    content: str
    
class FactCheckResponse(BaseModel):
    flagged_claims: List[Dict[str, Any]]
    credible_sources: List[Dict[str, str]]
    overall_score: int  # 0-100 credibility score
    entities: List[Dict[str, str]]

class ResearchRequest(BaseModel):
    topic: str
    max_sources: int = 5

@router.post("/fact_check", response_model=FactCheckResponse)
async def fact_check_content(request: FactCheckRequest):
    """
    Fact-check article content using free APIs and NLP
    """
    if not nlp:
        raise HTTPException(status_code=500, detail="NLP model not available")
    
    content = request.content
    
    try:
        # Step 1: Extract named entities
        doc = nlp(content)
        entities = []
        
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE", "EVENT", "DATE"]:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "description": spacy.explain(ent.label_)
                })
        
        # Step 2: Extract key claims (sentences with factual statements)
        sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]
        factual_sentences = []
        
        for sentence in sentences:
            # Look for sentences with numbers, dates, or strong claims
            if re.search(r'\d+|said|reported|according|claimed|announced', sentence):
                factual_sentences.append(sentence)
        
        # Step 3: Check claims against Wikipedia and news
        flagged_claims = []
        credible_sources = []
        
        # Check each entity in Wikipedia
        entity_checks = []
        for entity in entities[:3]:  # Limit to avoid rate limits
            try:
                wiki_summary = wikipedia.summary(entity["text"], sentences=2, auto_suggest=True)
                entity_checks.append({
                    "entity": entity["text"],
                    "wikipedia_info": wiki_summary[:200] + "...",
                    "verified": True
                })
                
                credible_sources.append({
                    "title": f"Wikipedia: {entity['text']}",
                    "url": f"https://en.wikipedia.org/wiki/{entity['text'].replace(' ', '_')}",
                    "source": "Wikipedia",
                    "snippet": wiki_summary[:150] + "..."
                })
                
            except wikipedia.exceptions.DisambiguationError as e:
                # Use first option if multiple matches
                try:
                    wiki_summary = wikipedia.summary(e.options[0], sentences=2)
                    entity_checks.append({
                        "entity": entity["text"],
                        "wikipedia_info": wiki_summary[:200] + "...",
                        "verified": True
                    })
                except:
                    pass
            except:
                entity_checks.append({
                    "entity": entity["text"],
                    "wikipedia_info": "No information found",
                    "verified": False
                })
        
        # Step 4: Analyze factual sentences for potential issues
        for sentence in factual_sentences[:5]:  # Limit analysis
            # Simple heuristics for potentially questionable claims
            confidence = 100
            issues = []
            
            # Check for absolute statements
            if re.search(r'\ball\b|\bevery\b|\bnever\b|\balways\b', sentence, re.IGNORECASE):
                confidence -= 15
                issues.append("Contains absolute statement")
            
            # Check for vague numbers
            if re.search(r'\bmany\b|\bfew\b|\bseveral\b|\bsome\b', sentence, re.IGNORECASE):
                confidence -= 10
                issues.append("Contains vague quantifiers")
            
            # Check for unsourced claims
            if not re.search(r'according to|said|reported|study|research', sentence, re.IGNORECASE):
                confidence -= 20
                issues.append("No clear source attribution")
            
            if confidence < 80 or issues:
                flagged_claims.append({
                    "text": sentence,
                    "issues": issues,
                    "confidence": max(confidence, 20),
                    "suggestion": "Consider adding sources or qualifying statements"
                })
        
        # Step 5: Try to get recent news for fact-checking
        if newsapi and entities:
            try:
                # Search for news about main entities
                main_entity = entities[0]["text"] if entities else ""
                if main_entity:
                    articles = newsapi.get_everything(
                        q=main_entity,
                        sort_by='relevancy',
                        page_size=3,
                        language='en'
                    )
                    
                    for article in articles.get('articles', [])[:2]:
                        credible_sources.append({
                            "title": article['title'],
                            "url": article['url'],
                            "source": article['source']['name'],
                            "snippet": article['description'] or article['title']
                        })
            except:
                pass  # Continue without news API if it fails
        
        # Step 6: Calculate overall credibility score
        total_claims = len(factual_sentences) if factual_sentences else 1
        flagged_count = len(flagged_claims)
        entity_verified_count = sum(1 for check in entity_checks if check.get('verified', False))
        entity_total = len(entity_checks) if entity_checks else 1
        
        # Score based on flagged claims and verified entities
        claim_score = max(0, 100 - (flagged_count / total_claims * 60))
        entity_score = (entity_verified_count / entity_total) * 40
        overall_score = int(min(100, max(20, claim_score + entity_score)))
        
        return FactCheckResponse(
            flagged_claims=flagged_claims,
            credible_sources=credible_sources,
            overall_score=overall_score,
            entities=entities
        )
        
    except Exception as e:
        print(f"❌ Fact-checking error: {e}")
        raise HTTPException(status_code=500, detail=f"Fact-checking failed: {str(e)}")

@router.post("/research")
async def research_topic(request: ResearchRequest):
    """
    Research a topic using Wikipedia and free sources
    """
    topic = request.topic
    max_sources = min(request.max_sources, 10)  # Limit to prevent abuse
    
    sources = []
    
    try:
        # Get Wikipedia summary
        wiki_summary = wikipedia.summary(topic, sentences=3)
        wiki_page = wikipedia.page(topic)
        
        sources.append({
            "title": f"Wikipedia: {topic}",
            "url": wiki_page.url,
            "source": "Wikipedia",
            "snippet": wiki_summary,
            "type": "encyclopedia"
        })
        
        # Get related Wikipedia pages
        for related in wiki_page.links[:3]:
            try:
                related_summary = wikipedia.summary(related, sentences=1)
                sources.append({
                    "title": f"Wikipedia: {related}",
                    "url": f"https://en.wikipedia.org/wiki/{related.replace(' ', '_')}",
                    "source": "Wikipedia",
                    "snippet": related_summary,
                    "type": "related"
                })
                
                if len(sources) >= max_sources:
                    break
            except:
                continue
                
    except wikipedia.exceptions.DisambiguationError as e:
        # Handle multiple matches
        for option in e.options[:2]:
            try:
                summary = wikipedia.summary(option, sentences=2)
                sources.append({
                    "title": f"Wikipedia: {option}",
                    "url": f"https://en.wikipedia.org/wiki/{option.replace(' ', '_')}",
                    "source": "Wikipedia", 
                    "snippet": summary,
                    "type": "alternative"
                })
            except:
                continue
                
    except wikipedia.exceptions.PageError:
        sources.append({
            "title": f"No Wikipedia page found for '{topic}'",
            "url": "",
            "source": "Wikipedia",
            "snippet": "Consider checking spelling or using alternative terms",
            "type": "error"
        })
    except Exception as e:
        print(f"Research error: {e}")
    
    # Add some general research sources
    if len(sources) < max_sources:
        general_sources = [
            {
                "title": f"Google Scholar: {topic}",
                "url": f"https://scholar.google.com/scholar?q={topic.replace(' ', '+')}",
                "source": "Google Scholar",
                "snippet": "Academic papers and research publications",
                "type": "academic"
            },
            {
                "title": f"BBC News: {topic}",
                "url": f"https://www.bbc.com/search?q={topic.replace(' ', '+')}",
                "source": "BBC News",
                "snippet": "Latest news and analysis",
                "type": "news"
            }
        ]
        
        sources.extend(general_sources[:max_sources - len(sources)])
    
    return {
        "topic": topic,
        "sources": sources[:max_sources],
        "total_found": len(sources)
    }

@router.get("/health")
async def fact_check_health():
    """Health check for fact-checking services"""
    return {
        "spacy_loaded": nlp is not None,
        "summarizer_loaded": summarizer is not None,
        "news_api_available": newsapi is not None,
        "wikipedia_available": True,
        "status": "operational"
    }

print("🔍 Fact-checking and research API initialized")