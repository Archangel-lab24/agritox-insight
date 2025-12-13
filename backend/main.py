
from fastapi import FastAPI, Query
from utils.detect_query_type import detect_query_type
from utils.resolve_product import resolve_product_name
from utils.fetch_pubchem import fetch_pubchem
from utils.fetch_epa import fetch_epa
from utils.summarizer import summarize
from utils.exporter import export_markdown

app = FastAPI(title="AgriTox Insight")

@app.get("/analyze")
async def analyze(query: str = Query(..., description="Product or active ingredient name")):
    qtype = detect_query_type(query)
    active = query
    resolution = None

    if qtype == "product":
        active, resolution = await resolve_product_name(query)

    pubchem = await fetch_pubchem(active)
    epa = await fetch_epa(active)

    summary = summarize(pubchem, epa)

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
