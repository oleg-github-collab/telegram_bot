from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from sheets import SheetsManager
import logging

logger = logging.getLogger(__name__)
sheets = SheetsManager()

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(f"Привіт, {user.first_name}! Ласкаво просимо до бота.")

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Доступні команди: /start /help /content")

def get_content(update: Update, context: CallbackContext) -> None:
    try:
        records = sheets.get_all_records("content")
        if not records:
            update.message.reply_text("Немає контенту.")
            return

        item = records[0]
        title = item.get("title", "Без назви")
        description = item.get("description", "Без опису")

        buttons = [[
            InlineKeyboardButton("Деталі", callback_data=f"content_details_{item.get('id', 0)}"),
            InlineKeyboardButton("Наступний", callback_data="next_content")
        ]]
        update.message.reply_text(f"*{title}*\n\n{description}", reply_markup=InlineKeyboardMarkup(buttons), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Помилка отримання контенту: {e}")
        update.message.reply_text("Сталася помилка.")

def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    query.answer()

    if data.startswith("content_details_"):
        content_id = data.split("_")[-1]
        query.edit_message_text(f"Деталі для контенту #{content_id}")
    elif data == "next_content":
        query.edit_message_text("Поки що функція недоступна.")
