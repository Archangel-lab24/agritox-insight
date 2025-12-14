# fetch_echa.py
import httpx
from bs4 import BeautifulSoup
import re
import asyncio

ECHA_SEARCH = "https://echa.europa.eu/information-on-chemicals/cl-inventory-database/-/discli/search"

async def fetch_echa(name: str):
    params = {"searchCriteria": name}

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            headers={"User-Agent": "AgriToxInsight/1.0"},
            follow_redirects=True
        ) as client:
            # Step 1: search page
            r = await client.get(ECHA_SEARCH, params=params)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            # Step 2: get first search result link
            first_link = soup.select_one("table.search-results-table tbody tr td a")
            if not first_link:
                return {"source": "ECHA", "status": "ok", "note": "No detailed data found", "url": str(r.url)}

            detail_url = "https://echa.europa.eu" + first_link.get("href", "")

            # Step 3: fetch detailed substance page
            r_detail = await client.get(detail_url)
            r_detail.raise_for_status()
            soup_detail = BeautifulSoup(r_detail.text, "html.parser")

            hazard_statements = []
            precautionary_statements = []
            recommended_use = None

            # Parse tables and sections
            tables = soup_detail.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    th = row.find("th")
                    td = row.find("td")
                    if not th or not td:
                        continue
                    key = th.get_text(strip=True).lower()
                    val = td.get_text(strip=True)

                    if "hazard statement" in key:
                        hazard_statements.extend(re.findall(r'H\d{3}', val))
                    elif "precautionary statement" in key:
                        precautionary_statements.extend(re.findall(r'P\d{3}', val))
                    elif "use" in key or "application" in key:
                        recommended_use = val

            return {
                "source": "ECHA",
                "status": "ok",
                "product_name": name,
                "hazard_statements": hazard_statements,
                "precautionary_statements": precautionary_statements,
                "recommended_use": recommended_use,
                "url": detail_url
            }

    except Exception as e:
        return {
            "source": "ECHA",
            "status": "unavailable",
            "error": str(e)
        }
