from telegram import Update
from telegram.ext import CallbackContext
from utils.helpers import is_admin, translate
from sheets import SheetsManager
import logging

logger = logging.getLogger(__name__)
sheets = SheetsManager()

def admin_panel(update: Update, context: CallbackContext):
    """Панель адміністратора"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("⛔ У вас немає доступу до адмін-панелі.")
        return

    keyboard = [["📥 Переглянути заявки", "📅 Події"], ["⬅️ Назад"]]
    update.message.reply_text(
        "🛠 Адмін-панель. Оберіть опцію:",
        reply_markup=reply_keyboard(keyboard)
    )

def admin_button_callback(update: Update, context: CallbackContext):
    """Обробка кнопок у адмін-панелі"""
    text = update.message.text
    if text == "📥 Переглянути заявки":
        handle_applications(update)
    elif text == "📅 Події":
        handle_event_overview(update)
    elif text == "⬅️ Назад":
        from handlers.user import handle_message
        return handle_message(update, context)
    else:
        update.message.reply_text("🤖 Невідома команда.")

def reply_keyboard(keyboard):
    from telegram import ReplyKeyboardMarkup
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def handle_applications(update):
    try:
        rows = sheets.get_all_records("applications")
        if not rows:
            update.message.reply_text("📭 Немає нових заявок.")
            return

        text = "📬 Заявки:\n\n"
        for row in rows:
            text += f"👤 {row.get('name')} — {row.get('time')}\n"
        update.message.reply_text(text)
    except Exception as e:
        logger.error(f"Помилка заявок: {e}")
        update.message.reply_text("⚠️ Сталася помилка при завантаженні заявок.")

def handle_event_overview(update):
    try:
        rows = sheets.get_all_records("events")
        if not rows:
            update.message.reply_text("📭 Немає подій.")
            return

        text = "📅 Події:\n\n"
        for row in rows:
            text += f"🗓 {row.get('date')} — {row.get('title')}\n"
        update.message.reply_text(text)
    except Exception as e:
        logger.error(f"Помилка при подіях: {e}")
        update.message.reply_text("⚠️ Не вдалося завантажити події.")
