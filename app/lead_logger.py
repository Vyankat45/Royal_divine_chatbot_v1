import os
import json
import logging

from datetime import datetime

logger = logging.getLogger(__name__)

_sheet = None


def _get_sheet():
    global _sheet
    if _sheet is not None:
        return _sheet

    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        if os.path.exists("credentials.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "credentials.json", scope
            )
        else:
            google_creds = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                google_creds, scope
            )

        client = gspread.authorize(creds)
        _sheet = client.open("Royal_divine_lead").sheet1

    except Exception as e:
        logger.warning("Google Sheets unavailable for lead logging: %s", e)
        _sheet = None

    return _sheet


def save_lead(
    session_id,
    name,
    email,
    phone,
    product,
    quantity,
    country,
    question
):
    sheet = _get_sheet()
    if sheet is None:
        return

    try:
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            session_id,
            name,
            email,
            phone,
            product,
            quantity,
            country,
            question
        ])
    except Exception as e:
        logger.warning("Failed to log lead: %s", e)
