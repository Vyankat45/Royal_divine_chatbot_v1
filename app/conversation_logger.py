import os
import json
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

if os.path.exists("credentials.json"):
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json",
        scope
    )
else:
    google_creds = json.loads(
        os.getenv("GOOGLE_CREDENTIALS")
    )
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        google_creds,
        scope
    )

client = gspread.authorize(creds)

sheet = client.open(
    "Royal Divine Chat Logs"
).sheet1


def log_conversation(session_id, question, answer):
    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        session_id,
        question,
        answer
    ])
