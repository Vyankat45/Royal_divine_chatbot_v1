import re


REMOVE_PHRASES = [
    "Home",
    "Follow Us",
    "next",
    "prev",
    "Shop Organic",
    "Enquiry Now"
]


def clean_text(text: str) -> str:

    for phrase in REMOVE_PHRASES:
        text = text.replace(phrase, "")

    text = re.sub(r"\s+", " ", text)

    return text.strip()