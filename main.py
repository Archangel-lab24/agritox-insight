import httpx
import os
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from detect_query_type import detect_query_type
from resolve_product import resolve_product_name
from fetch_pubchem import fetch_pubchem
from fetch_echa import fetch_echa
from summarizer import summarize
from exporter import export_markdown

app = FastAPI(title="AgriTox Insight")

@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join("frontend_build", "index.html"))

API_TESTS = {
    "Google": "https://www.google.com",
    "PubChem": "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/glyphosate/JSON",
    "ECHA": "https://echa.europa.eu/information-on-chemicals"
}

@app.get("/test-apis")
async def test_apis():
    results = {}
    async with httpx.AsyncClient(timeout=5) as client:
        for name, url in API_TESTS.items():
            try:
                r = await client.get(url)
                results[name] = {"status": "reachable", "status_code": r.status_code}
            except Exception as e:
                results[name] = {"status": "failed", "error": str(e)}
    return results
    
@app.get("/analyze")
async def analyze(query: str = Query(..., description="Product or active ingredient name")):
    qtype = detect_query_type(query)
    active = query
    resolution = None

    if qtype == "product":
        active, resolution = await resolve_product_name(query)

    pubchem = await fetch_pubchem(active)
    echa = await fetch_echa(active)

    summary = summarize(pubchem, echa)

    return {
        "query": query,
        "query_type": qtype,
        "active_ingredient": active,
        "resolution": resolution,
        "summary": summary
    }

@app.get("/export/markdown")
async def export_md(query: str):
    return export_markdown(query)
