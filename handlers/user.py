from telegram import Update
from telegram.ext import CallbackContext
from utils.helpers import get_main_keyboard, translate
from sheets import SheetsManager
import logging

logger = logging.getLogger(__name__)
sheets = SheetsManager()

# Словник для збереження мов користувачів
user_languages = {}

def start(update: Update, context: CallbackContext):
    """Привітання + вибір мови."""
    keyboard = [["Українська", "English", "Deutsch"]]
    update.message.reply_text(
        "🌐 Please choose your language:\n🌐 Будь ласка, оберіть мову:\n🌐 Bitte wählen Sie Ihre Sprache:",
        reply_markup=get_lang_keyboard(keyboard)
    )

def get_lang_keyboard(keyboard):
    from telegram import ReplyKeyboardMarkup
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def set_language(update: Update, context: CallbackContext):
    """Фіксує обрану мову."""
    lang_text = update.message.text
    user_id = update.effective_user.id

    lang_map = {
        "Українська": "uk",
        "English": "en",
        "Deutsch": "de"
    }

    lang = lang_map.get(lang_text, "uk")
    user_languages[user_id] = lang

    update.message.reply_text(
        f"✅ Мову встановлено: {lang_text}",
        reply_markup=get_main_keyboard(lang)
    )

def handle_message(update: Update, context: CallbackContext):
    """Головна логіка кнопок."""
    user_id = update.effective_user.id
    lang = user_languages.get(user_id, "uk")
    text = update.message.text

    if text == translate("events", lang):
        handle_events(update, lang)
    elif text == translate("yoga", lang):
        handle_yoga(update, lang)
    elif text == translate("schedule", lang):
        handle_schedule(update, lang)
    elif text == translate("shop", lang):
        handle_shop(update, lang)
    elif text == translate("about", lang):
        handle_about(update, lang)
    elif text == translate("lang", lang):
        start(update, context)  # Повторно вибрати мову
    else:
        update.message.reply_text("🤖 Не зрозумів запит. Спробуйте ще раз.", reply_markup=get_main_keyboard(lang))

def handle_events(update, lang):
    try:
        rows = sheets.get_all_records("events")
        if not rows:
            update.message.reply_text("📭 Немає запланованих подій.")
            return

        response = "📅 Події:\n\n"
        for r in rows:
            response += f"🗓 {r.get('date')} — {r.get('title')}\n{r.get('description')}\n\n"
        update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Помилка подій: {e}")
        update.message.reply_text("⚠️ Помилка при завантаженні подій.")

def handle_yoga(update, lang):
    update.message.reply_text(
        "🧘 Для запису на заняття надішліть своє ім’я, бажаний день та час.",
    )

def handle_schedule(update, lang):
    try:
        rows = sheets.get_all_records("schedule")
        if not rows:
            update.message.reply_text("📭 Розклад поки відсутній.")
            return

        response = "🗓 Розклад:\n\n"
        for r in rows:
            response += f"📌 {r.get('day')} — {r.get('time')} — {r.get('activity')}\n"
        update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Помилка розкладу: {e}")
        update.message.reply_text("⚠️ Помилка при завантаженні розкладу.")

def handle_shop(update, lang):
    update.message.reply_text(
        "🛒 Перейдіть до інтернет-магазину 👇\nhttps://www.instagram.com/marina.art.store/"
    )

def handle_about(update, lang):
    update.message.reply_text(
        "👩‍🎨 Я — Марина Камінська, художниця та викладачка йоги з понад 10 роками досвіду.\n"
        "🎨 Мої роботи виставлялись в Європі.\n"
        "🧘 Я веду регулярні класи йоги, що поєднують тіло, дихання і свідомість."
    )
