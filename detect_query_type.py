
def detect_query_type(query: str) -> str:
    keywords = ["roundup", "max", "gold", "ultra"]
    if any(k in query.lower() for k in keywords):
        return "product"
    return "active_ingredient"
