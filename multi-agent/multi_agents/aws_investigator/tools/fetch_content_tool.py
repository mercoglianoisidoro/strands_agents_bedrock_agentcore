"""Fetch full webpage content tool."""

from strands import tool
import requests


@tool
def fetch_webpage(url: str, max_length: int = 100000) -> str:
    """
    Fetch and convert webpage content to markdown format.

    Use this for reading documentation, articles, or any webpage content.

    Args:
        url: The URL of the webpage to fetch
        max_length: Maximum content length (default: 100000 characters)

    Returns:
        Webpage content converted to markdown format
    """
    try:
        import html2text

        response = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (compatible; WebSearchAgent/1.0)"}
        )
        response.raise_for_status()

        # Convert HTML to markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.ignore_emphasis = False
        h.body_width = 0  # Don't wrap lines

        markdown = h.handle(response.text).strip()

        # Truncate if needed
        if len(markdown) > max_length:
            markdown = markdown[:max_length] + "\n\n[Content truncated]"

        return f"# Content from {url}\n\n{markdown}"

    except ImportError:
        return "Error: html2text library not installed. Run: pip install html2text"
    except requests.Timeout:
        return f"Error: Request to {url} timed out"
    except requests.RequestException as e:
        return f"Error: Failed to fetch {url} - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
