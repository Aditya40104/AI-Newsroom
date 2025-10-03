import requests
import json

def test_ai_api():
    url = "http://127.0.0.1:8000/api/ai/generate_article"
    
    payload = {
        "topic": "Artificial Intelligence in Healthcare",
        "keywords": ["AI", "healthcare", "technology"],
        "tone": "professional",
        "length": "short"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS! AI API is working!")
            print(f"Title: {data.get('title', 'No title')}")
            print(f"Content length: {len(data.get('content', ''))}")
            print(f"Summary: {data.get('summary', 'No summary')}")
            print(f"Tags: {data.get('suggested_tags', [])}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

if __name__ == "__main__":
    print("Testing AI API...")
    test_ai_api()