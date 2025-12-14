import httpx
from bs4 import BeautifulSoup
import re

DUCKDUCKGO_SEARCH_URL = "https://html.duckduckgo.com/html/"

async def resolve_product_name(product_name: str):
    """
    Resolves the primary active ingredient of a commercial product via DuckDuckGo search.

    Returns:
        active_ingredient (str)
        resolution_info (dict)
    """
    query = f"{product_name} active ingredient pesticide"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AgriToxInsight/1.0; +https://example.com)"
    }

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.post(DUCKDUCKGO_SEARCH_URL, data={"q": query}, headers=headers)
            r.raise_for_status()
            html = r.text

        soup = BeautifulSoup(html, "html.parser")
        snippets = soup.find_all("a", class_="result__a")

        # Try to extract first plausible active ingredient
        for a in snippets:
            text = a.get_text().strip()
            # Look for "contains [chemical]" or "active ingredient is [chemical]"
            match = re.search(r"(contains|active ingredient is|active ingredient:)\s*([\w\s\-]+)", text, re.IGNORECASE)
            if match:
                active = match.group(2).strip()
                return active, {
                    "method": "internet_search",
                    "source": a.get("href", "unknown"),
                    "confidence": "medium"
                }

        # Fallback: use first snippet's text as best guess
        if snippets:
            first_text = snippets[0].get_text().strip()
            return first_text, {
                "method": "internet_search",
                "source": snippets[0].get("href", "unknown"),
                "confidence": "low"
            }

    except Exception as e:
        # Graceful failure
        return None, {
            "method": "internet_search",
            "error": str(e),
            "confidence": "none"
        }

    # If nothing found
    return None, {
        "method": "internet_search",
        "error": "No active ingredient found",
        "confidence": "none"
    }
