# fetch_echa.py
import httpx
from bs4 import BeautifulSoup
import re

ECHA_SEARCH = "https://echa.europa.eu/information-on-chemicals/cl-inventory-database/-/discli/search"

H_CODE_REGEX = re.compile(r"\bH\d{3}\b")
P_CODE_REGEX = re.compile(r"\bP\d{3}\b")

async def fetch_echa(name: str):
    try:
        async with httpx.AsyncClient(
            timeout=15.0,
            headers={"User-Agent": "Mozilla/5.0 (AgriTox Insight)"},
            follow_redirects=True
        ) as client:

            # 1️⃣ Search
            r = await client.get(ECHA_SEARCH, params={"searchCriteria": name})
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            # 2️⃣ Find first substance link
            link = soup.select_one("a[href*='/cl-inventory-database/-/discli/details/']")
            if not link:
                return {
                    "source": "ECHA",
                    "status": "ok",
                    "note": "No substance page found",
                    "hazard_statements": [],
                    "precautionary_statements": [],
                }

            detail_url = "https://echa.europa.eu" + link["href"]

            # 3️⃣ Fetch substance page
            r2 = await client.get(detail_url)
            r2.raise_for_status()
            soup2 = BeautifulSoup(r2.text, "html.parser")

            page_text = soup2.get_text(" ", strip=True)

            # 4️⃣ Extract ALL H / P codes anywhere on page
            hazard_statements = sorted(set(H_CODE_REGEX.findall(page_text)))
            precautionary_statements = sorted(set(P_CODE_REGEX.findall(page_text)))

            # 5️⃣ Extract crude recommended use (best-effort)
            recommended_use = None
            for h in soup2.find_all(["h2", "h3"]):
                if "use" in h.get_text(strip=True).lower():
                    p = h.find_next("p")
                    if p:
                        recommended_use = p.get_text(strip=True)
                        break

            return {
                "source": "ECHA",
                "status": "ok",
                "product_name": name,
                "hazard_statements": hazard_statements,
                "precautionary_statements": precautionary_statements,
                "recommended_use": recommended_use,
                "url": detail_url,
            }

    except Exception as e:
        return {
            "source": "ECHA",
            "status": "unavailable",
            "error": str(e),
            "hazard_statements": [],
            "precautionary_statements": [],
        }
