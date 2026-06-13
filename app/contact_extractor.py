import re


def extract_email(text):
    match = re.search(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        text
    )
    if match:
        return match.group(0)
    return ""


def extract_phone(text):
    match = re.search(
        r'\+?\d[\d\s\-\(\)]{8,15}',
        text
    )
    if match:
        return match.group(0).strip()
    return ""


def extract_name(text):
    text = text.strip()
    lines = text.split("\n")
    first_line = lines[0].strip()

    patterns = [
        r"(?:my name is|i am|i'm|name is|this is)\s+([A-Za-z\s\.]{2,40})",
        r"^(?:name\s*[:：]?\s*)([A-Za-z\s\.]{2,40})",
        r"^([A-Za-z\s\.]{3,40})$"
    ]

    for pattern in patterns:
        match = re.search(pattern, first_line, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            if len(candidate) >= 2:
                return candidate

    if len(first_line) >= 2 and len(first_line) <= 40:
        if not re.search(r'[@\d]', first_line):
            return first_line

    return ""
