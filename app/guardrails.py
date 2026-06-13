ALLOWED_KEYWORDS = [
    "company",
    "about company",
    "about you",
    "who are you",
    "business",
    "royal divine",

    "product",
    "products",
    "dry fruit",
    "dry fruits",
    "almond",
    "almonds",
    "badam",
    "cashew",
    "cashews",
    "kaju",
    "peanut",
    "peanuts",
    "pistachio",
    "pista",
    "walnut",
    "walnuts",
    "dates",
    "raisins",
    "spice",
    "spices",
    "cumin",
    "jeera",
    "turmeric",
    "haldi",
    "cinnamon",
    "pepper",
    "coriander",
    "fruit",
    "fruits",
    "apple",
    "coconut",
    "vegetable",
    "vegetables",
    "corn",
    "grain",
    "grains",
    "barley",

    "export",
    "import",
    "supplier",
    "quotation",
    "quote",
    "price",
    "pricing",
    "moq",
    "minimum order",
    "packaging",
    "certificate",
    "certification",
    "quality",
    "contact",
    "address",
    "location",
    "phone",
    "email",
    "whatsapp",
    "delivery",
    "shipping",
    "payment",
    "order",
    "bulk",
    "wholesale",
    "retail",
    "organic",
    "natural",
    "manufacturer",
    "exporter"
]


def is_business_question(question):
    q = question.lower()

    if any(keyword in q for keyword in ALLOWED_KEYWORDS):
        return True

    # Check for product-related patterns
    product_patterns = [
        r"\b(?:sell|sold|available|have|offer|provide)\b",
        r"\b(?:what|which|tell|show|list)\b.*\b(?:product|item|category)\b",
        r"\b(?:how much|cost|rate|price)\b",
        r"\b(?:do you|does your|can you)\b",
    ]

    import re
    for pattern in product_patterns:
        if re.search(pattern, q):
            return True

    return False
