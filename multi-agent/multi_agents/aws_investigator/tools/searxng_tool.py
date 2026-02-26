"""SearxNG web search tool."""

from strands import tool
import requests
import os


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using SearxNG metasearch engine.

    Args:
        query: The search query
        max_results: Maximum number of results (default: 5)

    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    searxng_url = os.getenv("SEARXNG_URL", "http://localhost:8080")

    try:
        response = requests.get(
            f"{searxng_url}/search",
            params={"q": query, "format": "json"},
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; WebSearchAgent/1.0)"
            },
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])[:max_results]

        if not results:
            return f"No results found for: {query}"

        formatted = [f"Search results for: {query}\n"]
        for i, r in enumerate(results, 1):
            formatted.append(f"[{i}] {r.get('title', 'No title')}")
            formatted.append(f"URL: {r.get('url', 'No URL')}")
            content = r.get('content', '')
            if content:
                formatted.append(f"{content[:200]}...")
            formatted.append("")

        return "\n".join(formatted)

    except requests.Timeout:
        return "Error: Search request timed out. Please try again."
    except requests.RequestException as e:
        return f"Error: Failed to connect to search service - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error during search - {str(e)}"
