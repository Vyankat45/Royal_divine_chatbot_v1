import re

LEAD_KEYWORDS = [
    "buy",
    "purchase",
    "order",
    "quotation",
    "quote",
    "price",
    "pricing",
    "supplier",
    "bulk",
    "need",
    "require",
    "want",
    "import",
    "export",
    "shipping",
    "delivery",
    "cost",
    "rate",
    "quotation",
    "send",
    "supply",
    "procure",
    "selling"
]

LEAD_PHRASES = [
    "i want to buy",
    "i want to purchase",
    "i want to order",
    "i want to import",
    "i need to buy",
    "i need to purchase",
    "i need to order",
    "i would like to buy",
    "i would like to purchase",
    "i would like to order",
    "i would like to import",
    "can you supply",
    "can you provide",
    "can you send",
    "need quotation",
    "need quote",
    "looking for",
    "interested in",
    "please quote",
    "send quotation",
    "send quote",
    "quote for",
    "price for",
    "quotation for",
    "supply of",
    "bulk order",
    "place order",
    "buying",
    "purchasing"
]


INFORMATIONAL_PATTERNS = [
    r"^(what|which|tell me|show me|list|describe|explain)",
    r"^how (much|many|does|do|can)",
    r"^(do you|can you|does your|could you)",
    r"(tell me about|information about|details about|info about)",
    r"(what is|what are|what do|what does)",
]


def is_lead(question):
    question_lower = question.lower()

    has_quantity = bool(extract_quantity(question))

    # If purely informational (no quantity, no purchase phrase), not a lead
    is_info = any(re.search(p, question_lower) for p in INFORMATIONAL_PATTERNS)

    for phrase in LEAD_PHRASES:
        if phrase in question_lower:
            if not is_info or has_quantity:
                return True

    if any(keyword in question_lower for keyword in LEAD_KEYWORDS):
        if not is_info or has_quantity:
            return True

    if has_quantity:
        return True

    return False


def extract_quantity(question):
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(kg|kgs|kilo|kilos|kilogram|kilograms|ton|tons|tonne|g|gram|grams|mt)\b",
        question.lower()
    )
    if match:
        return match.group(0)
    return ""


def extract_country(question):
    countries = [
        "india",
        "uae",
        "dubai",
        "saudi arabia",
        "saudi",
        "oman",
        "qatar",
        "kuwait",
        "bahrain",
        "usa",
        "united states",
        "canada",
        "uk",
        "united kingdom",
        "australia",
        "germany",
        "france",
        "italy",
        "spain",
        "netherlands",
        "singapore",
        "malaysia",
        "indonesia",
        "japan",
        "china",
        "south korea",
        "brazil",
        "south africa",
        "nigeria",
        "kenya",
        "egypt",
        "turkey",
        "bangladesh",
        "sri lanka",
        "nepal"
    ]

    question_lower = question.lower()

    for country in countries:
        if country in question_lower:
            return country.title()

    return ""
