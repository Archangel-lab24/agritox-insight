import httpx
from bs4 import BeautifulSoup
import re

ECHA_SEARCH = "https://echa.europa.eu/information-on-chemicals/cl-inventory-database/-/discli/search"

async def fetch_echa(name: str):
    params = {"searchCriteria": name}

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            headers={"User-Agent": "AgriToxInsight/1.0"},
            follow_redirects=True
        ) as client:
            r = await client.get(ECHA_SEARCH, params=params)
            r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        # Look for the first search result table
        table = soup.find("table", class_="search-results-table")
        if not table:
            return {"source": "ECHA", "status": "ok", "note": "No detailed data found", "url": str(r.url)}

        rows = table.find_all("tr")
        hazard_statements = []
        precautionary_statements = []
        recommended_use = None

        for row in rows:
            th = row.find("th")
            td = row.find("td")
            if not th or not td:
                continue
            key = th.get_text(strip=True).lower()
            val = td.get_text(strip=True)

            # Extract hazard statements
            if "hazard statement" in key:
                hazard_statements.extend(re.findall(r'H\d{3}', val))

            # Extract precautionary statements
            elif "precautionary statement" in key:
                precautionary_statements.extend(re.findall(r'P\d{3}', val))

            # Extract recommended use
            elif "use" in key or "application" in key:
                recommended_use = val

        return {
            "source": "ECHA",
            "status": "ok",
            "product_name": name,
            "hazard_statements": hazard_statements,
            "precautionary_statements": precautionary_statements,
            "recommended_use": recommended_use,
            "url": str(r.url)
        }

    except Exception as e:
        return {
            "source": "ECHA",
            "status": "unavailable",
            "error": str(e)
        }
