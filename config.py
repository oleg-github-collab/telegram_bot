import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USER_IDS = list(map(int, os.getenv('ADMIN_USER_IDS', '').split(',')))
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE', 'credentials.json')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

LANGUAGES = {
    'ua': 'Українська 🇺🇦',
    'en': 'English 🇬🇧',
    'de': 'Deutsch 🇩🇪'
}
DEFAULT_LANGUAGE = 'ua'
