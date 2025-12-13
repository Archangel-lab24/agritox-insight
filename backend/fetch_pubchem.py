
import httpx

BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

async def fetch_pubchem(name: str):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{BASE}/compound/name/{name}/cids/JSON")
        if r.status_code != 200:
            return {}
        cid = r.json().get("IdentifierList", {}).get("CID", [None])[0]
        if not cid:
            return {}
        r2 = await client.get(f"{BASE}/compound/cid/{cid}/JSON")
        return r2.json()
