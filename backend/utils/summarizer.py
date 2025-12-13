
def summarize(pubchem, epa):
    risk = "Unknown"
    if pubchem:
        risk = "Low to moderate mammalian toxicity"
    return {
        "environmental_risk": risk,
        "note": "Rule-based summary (no ML)"
    }
