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


def is_lead(question):
    question_lower = question.lower()

    for phrase in LEAD_PHRASES:
        if phrase in question_lower:
            return True

    if any(keyword in question_lower for keyword in LEAD_KEYWORDS):
        return True

    quantity = extract_quantity(question)
    if quantity:
        return True

    return False


def extract_quantity(question):
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(kg|kgs|kilo|kilos|kilogram|kilograms|ton|tons|tonne|g|gram|grams|mt|k)",
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
