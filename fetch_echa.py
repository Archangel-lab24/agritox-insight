
import httpx

# ECHA public search endpoint (HTML, but structured enough)
ECHA_SEARCH = "https://echa.europa.eu/information-on-chemicals/cl-inventory-database/-/discli/search"

async def fetch_echa(name: str):
    params = {
        "searchCriteria": name
    }

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(5.0),
            headers={"User-Agent": "AgriToxInsight/1.0"},
            follow_redirects=True
        ) as client:
            r = await client.get(ECHA_SEARCH, params=params)
            r.raise_for_status()

            return {
                "source": "ECHA",
                "status": "ok",
                "note": "ECHA does not expose a formal JSON API. HTML retrieved successfully.",
                "url": str(r.url)
            }

    except Exception as e:
        return {
            "source": "ECHA",
            "status": "unavailable",
            "error": str(e)
        }

