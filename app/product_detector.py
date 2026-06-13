from rapidfuzz import fuzz, process
from app.products import PRODUCTS

SKIP_WORDS = {
    "what", "which", "where", "when", "why", "how",
    "tell", "show", "list", "know", "about",
    "sell", "sold", "buy", "purchase", "order",
    "want", "need", "get", "have", "has",
    "can", "you", "your", "do", "does",
    "the", "and", "for", "are", "all",
    "price", "cost", "rate", "quote", "moq",
    "please", "some", "info", "information",
    "supply", "supplier", "product", "products",
    "available", "offer", "provide", "send",
}


def detect_product(question, history=None):
    question = question.lower()

    # Direct key match (priority to multi-word keys)
    for product_key in sorted(PRODUCTS, key=len, reverse=True):
        if product_key in question:
            return product_key

    keys = list(PRODUCTS.keys())

    # Fuzzy match entire question — skip if it's an information-seeking question
    if not _is_purchase_intent(question):
        return None

    result = process.extractOne(question, keys, scorer=fuzz.partial_ratio, score_cutoff=85)
    if result:
        return result[0]

    # Token-level fuzzy matching — skip generic/stop words
    words = question.split()
    for word in words:
        if len(word) < 4 or word in SKIP_WORDS:
            continue
        result = process.extractOne(word, keys, scorer=fuzz.ratio, score_cutoff=82)
        if result:
            return result[0]

    # Fallback: try to infer product from conversation history
    if history:
        product_from_history = _infer_product_from_history(history)
        if product_from_history:
            return product_from_history

    return None


def _infer_product_from_history(history):
    """Look through recent conversation to find the last mentioned product."""
    all_keys = list(PRODUCTS.keys())
    for msg in reversed(history):
        content = msg.get("content", "").lower()
        for key in sorted(all_keys, key=len, reverse=True):
            if key in content:
                return key
    return None


def suggest_products(question):
    """Return top 3 product suggestions when exact product not found."""
    from rapidfuzz import fuzz as fz
    keys = list(PRODUCTS.keys())
    scored = []
    words = question.lower().split()
    for word in words:
        if len(word) < 3:
            continue
        for key in keys:
            score = fz.ratio(word, key)
            if score >= 60:
                scored.append((score, key))
    scored.sort(reverse=True)
    seen = set()
    suggestions = []
    for score, key in scored:
        category = PRODUCTS.get(key)
        display_key = key.title()
        if display_key not in seen and len(suggestions) < 3:
            seen.add(display_key)
            suggestions.append(display_key)
    return suggestions


def _is_purchase_intent(question):
    """Returns True if the question has clear purchase intent (has quantities, specific product words)."""
    import re
    if re.search(r"(\d+\s*(kg|kgs|kilo|ton|g|mt))", question):
        return True
    purchase_markers = ["buy", "purchase", "order", "import", "procure"]
    if any(m in question for m in purchase_markers):
        return True
    return False
