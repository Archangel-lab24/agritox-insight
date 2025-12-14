# fetch_echa.py

async def fetch_echa(name: str):
    name_lc = name.lower()

    # --- Static reference profiles (simulated ECHA output) ---
    STATIC_DB = {
        "glyphosate": {
            "product_name": "Glyphosate",
            "hazard_statements": ["H302", "H411"],
            "precautionary_statements": ["P264", "P273", "P280"],
            "recommended_use": "Non-selective systemic herbicide for post-emergence weed control.",
        },
        "chlorpyrifos": {
            "product_name": "Chlorpyrifos",
            "hazard_statements": ["H301", "H331", "H410"],
            "precautionary_statements": ["P260", "P273", "P391", "P501"],
            "recommended_use": "Broad-spectrum organophosphate insecticide for agricultural crops.",
        },
        "2,4-d": {
            "product_name": "2,4-D",
            "hazard_statements": ["H302", "H312", "H412"],
            "precautionary_statements": ["P270", "P280", "P301"],
            "recommended_use": "Selective systemic herbicide for control of broadleaf weeds.",
        },
    }

    for key, data in STATIC_DB.items():
        if key in name_lc:
            return {
                "source": "ECHA (static)",
                "status": "ok",
                "product_name": data["product_name"],
                "hazard_statements": data["hazard_statements"],
                "precautionary_statements": data["precautionary_statements"],
                "recommended_use": data["recommended_use"],
                "url": "https://echa.europa.eu/",
            }

    # --- Default fallback ---
    return {
        "source": "ECHA (static)",
        "status": "ok",
        "product_name": name,
        "hazard_statements": [],
        "precautionary_statements": [],
        "recommended_use": "No specific use information available.",
        "url": "https://echa.europa.eu/",
    }
