"""Fetch full webpage content tool."""

from strands import tool
import requests
import os


@tool
def fetch_webpage(url: str) -> str:
    """
    Fetch and extract full content from a webpage.
    
    Args:
        url: The URL of the webpage to fetch
        
    Returns:
        Full webpage content converted to markdown format
    """
    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; WebSearchAgent/1.0)"
            }
        )
        response.raise_for_status()
        
        # Try to convert HTML to markdown using basic conversion
        from html import unescape
        import re
        
        content = response.text
        
        # Remove script and style tags
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags but keep text
        content = re.sub(r'<[^>]+>', ' ', content)
        
        # Clean up whitespace
        content = re.sub(r'\s+', ' ', content)
        content = unescape(content).strip()
        
        # Limit to reasonable size (first 10000 chars)
        if len(content) > 10000:
            content = content[:10000] + "\n\n[Content truncated - showing first 10000 characters]"
        
        return f"Content from {url}:\n\n{content}"
        
    except requests.Timeout:
        return f"Error: Request to {url} timed out. The page took too long to respond."
    except requests.RequestException as e:
        return f"Error: Failed to fetch {url} - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error fetching {url} - {str(e)}"
