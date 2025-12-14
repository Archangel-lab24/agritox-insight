# summarizer.py
import re

# Mapping of hazard codes/statements to readable toxicity levels
MAMMALIAN_TOXICITY_MAP = {
    "H300": "Fatal if swallowed",
    "H301": "Toxic if swallowed",
    "H302": "Harmful if swallowed",
    "H310": "Fatal in contact with skin",
    "H311": "Toxic in contact with skin",
    "H312": "Harmful in contact with skin",
    "H330": "Fatal if inhaled",
    "H331": "Toxic if inhaled",
    "H332": "Harmful if inhaled",
}

ENVIRONMENTAL_TOXICITY_MAP = {
    "H400": "Very toxic to aquatic life",
    "H401": "Toxic to aquatic life",
    "H402": "Harmful to aquatic life",
    "H410": "Very toxic to aquatic life with long lasting effects",
    "H411": "Toxic to aquatic life with long lasting effects",
    "H412": "Harmful to aquatic life with long lasting effects",
    "H420": "Harms bees",
}

# Default risk levels for interpretation
RISK_LEVELS = {
    "low": ["H302", "H312", "H332"],
    "moderate": ["H311", "H331", "H401", "H412"],
    "high": ["H300", "H301", "H310", "H330", "H400", "H410"]
}


def map_toxicity_statements(statements):
    mammalian = []
    environmental = []

    for code in statements:
        if code in MAMMALIAN_TOXICITY_MAP:
            mammalian.append(MAMMALIAN_TOXICITY_MAP[code])
        if code in ENVIRONMENTAL_TOXICITY_MAP:
            environmental.append(ENVIRONMENTAL_TOXICITY_MAP[code])

    # Determine summary level for mammalian toxicity
    mammalian_level = "Unknown"
    for level, codes in RISK_LEVELS.items():
        if any(code in statements for code in codes):
            mammalian_level = level.capitalize()
            break

    return {
        "mammalian": mammalian_level if mammalian_level != "Unknown" else "Low to moderate",
        "mammalian_details": mammalian,
        "environmental": environmental or ["Low to moderate"],
    }


def extract_precautions(echa_data):
    """
    Extract precautionary statements (P-statements) from ECHA JSON
    """
    precautions = []

    statements = echa_data.get("precautionary_statements", [])
    for stmt in statements:
        text = stmt.get("text", "").strip()
        if text:
            precautions.append(text)

    return precautions


def extract_recommended_use(echa_data):
    """
    Extract recommended application / usage instructions if available
    """
    usage = echa_data.get("recommended_use", None)
    if usage:
        return usage
    return "Unknown"


def extract_regulatory_status(echa_data):
    """
    Extract regulatory / CLP info
    """
    status = {
        "ECHA": echa_data.get("status", "Unknown"),
        "CLP": echa_data.get("hazard_statements", [])
    }
    return status


def summarize(pubchem_data, echa_data):
    """
    Generate a structured summary for a chemical/product
    """
    product_name = echa_data.get("product_name", "Unknown")
    active_ingredient = echa_data.get("active_ingredient", pubchem_data.get("title", "Unknown"))

    hazard_codes = echa_data.get("hazard_statements", [])
    toxicity = map_toxicity_statements(hazard_codes)
    precautions = extract_precautions(echa_data)
    recommended_use = extract_recommended_use(echa_data)
    regulatory_status = extract_regulatory_status(echa_data)

    notes = []
    if "High" in toxicity["mammalian"]:
        notes.append("Handle with extreme care; use appropriate PPE.")
    if any("aquatic" in env.lower() for env in toxicity["environmental"]):
        notes.append("Avoid contamination of water sources.")

    summary = {
        "product": product_name,
        "active_ingredient": active_ingredient,
        "recommended_use": recommended_use,
        "toxicity": toxicity,
        "precautions": precautions,
        "regulatory_status": regulatory_status,
        "notes": notes or ["No special notes."]
    }

    return summary
