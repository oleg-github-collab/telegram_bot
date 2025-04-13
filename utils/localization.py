import os
import logging
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

# Налаштування логування
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
numeric_level = getattr(logging, LOG_LEVEL.upper(), None)

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=numeric_level,
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Основні налаштування бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN не знайдено в .env файлі!")
    exit(1)

# Налаштування адміністраторів
ADMIN_USER_IDS = []
admin_ids_str = os.getenv('ADMIN_USER_IDS', '')
if admin_ids_str:
    try:
        ADMIN_USER_IDS = [int(user_id.strip()) for user_id in admin_ids_str.split(',') if user_id.strip().isdigit()]
        logger.info(f"Зареєстровані адміністратори: {ADMIN_USER_IDS}")
    except Exception as e:
        logger.error(f"Помилка при обробці ADMIN_USER_IDS: {e}")

# Налаштування Google Sheets
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE', 'credentials.json')

# Перевірка наявності credentials.json
if not os.path.exists(CREDENTIALS_FILE):
    logger.warning(f"Файл {CREDENTIALS_FILE} не знайдено! Google Sheets функціонал буде недоступний.")

# Режим бота
BOT_MODE = os.getenv('BOT_MODE', 'polling').lower()
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
PORT = int(os.getenv('PORT', '8443'))

# Підтримувані мови
LANGUAGES = ['uk', 'en', 'de']
DEFAULT_LANGUAGE = 'uk'