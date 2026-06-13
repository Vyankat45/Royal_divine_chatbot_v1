def get_search_filter(question: str):
    q = question.lower()

    CATEGORIES = {
        "dry fruit": "dryfruits",
        "dryfruits": "dryfruits",
        "dry fruits": "dryfruits",
        "nuts": "dryfruits",
        "spice": "spices",
        "spices": "spices",
        "fruit": "fruits",
        "fruits": "fruits",
        "vegetable": "vegetables",
        "vegetables": "vegetables",
        "grain": "grains",
        "grains": "grains",
    }

    for phrase, cat_value in CATEGORIES.items():
        if phrase in q:
            return {"category": cat_value}

    PRODUCTS = [
        "almond",
        "cashew",
        "dates",
        "pistachio",
        "walnuts",
        "peanuts",
        "turmeric",
        "cinnamon",
        "apple",
        "barley",
    ]
    for product in PRODUCTS:
        if product in q:
            return {"product_name": product}

    return None