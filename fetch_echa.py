# fetch_echa.py
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
            # Step 1: search
            search_res = await client.get(ECHA_SEARCH, params=params)
            search_res.raise_for_status()
        search_soup = BeautifulSoup(search_res.text, "html.parser")

        # Step 2: get first substance link
        result_table = search_soup.find("table", class_="search-results-table")
        if not result_table:
            return {"source": "ECHA", "status": "ok", "note": "No detailed data found", "url": str(search_res.url)}

        first_link = result_table.find("a", href=True)
        if not first_link:
            return {"source": "ECHA", "status": "ok", "note": "No detailed data found", "url": str(search_res.url)}

        detail_url = "https://echa.europa.eu" + first_link["href"]

        # Step 3: fetch detailed page
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            headers={"User-Agent": "AgriToxInsight/1.0"},
        ) as client:
            detail_res = await client.get(detail_url)
            detail_res.raise_for_status()
        detail_soup = BeautifulSoup(detail_res.text, "html.parser")

        # Step 4: parse hazard/precaution/recommended use
        hazard_statements = []
        precautionary_statements = []
        recommended_use = None

        tables = detail_soup.find_all("table")
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
