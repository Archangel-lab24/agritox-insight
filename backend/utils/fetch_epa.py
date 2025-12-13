
import httpx

BASE = "https://api-cctcd.epa.gov/v1/chemical/identifiers"

async def fetch_epa(name: str):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(BASE, params={"chemical_identifier": name})
        if r.status_code != 200:
            return {}
        return r.json()
