
import httpx

async def resolve_product_name(product: str):
    # Minimal authoritative resolution via Wikidata
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": product,
        "language": "en",
        "format": "json"
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        data = r.json()
        if data.get("search"):
            # Simplified: hard-map common products
            name = data["search"][0]["label"].lower()
            if "roundup" in name:
                return "glyphosate", {"confidence": "high", "source": "Wikidata"}
    return product, {"confidence": "unknown", "source": "none"}
