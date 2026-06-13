import re


def extract_quantity_value(question):
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(kg|kgs|kilogram|kilograms|ton|tons|tonne|mt|g|gram|grams)",
        question.lower()
    )
    if not match:
        return None, None

    quantity = float(match.group(1))
    unit = match.group(2)

    return quantity, unit


def _is_domestic_india(question):
    q = question.lower()
    return any(kw in q for kw in ["india", "indian", "domestic", "mumbai", "delhi", "gujarat", "maharashtra"])


def is_below_moq(question, country=None):
    quantity, unit = extract_quantity_value(question)

    if quantity is None:
        return False

    domestic = _is_domestic_india(question)
    if country and country.lower() == "india":
        domestic = True

    # Convert everything to KG for comparison
    if unit in ["ton", "tons", "tonne", "mt"]:
        quantity_kg = quantity * 1000
    elif unit in ["g", "gram", "grams"]:
        quantity_kg = quantity / 1000
    else:
        quantity_kg = quantity

    if domestic:
        # India MOQ = 1 Ton (1000 KG)
        return quantity_kg < 1000
    else:
        # Export MOQ = 5 Tons (5000 KG)
        return quantity_kg < 5000
