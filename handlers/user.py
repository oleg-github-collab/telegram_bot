from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import logging
from sheets import SheetsManager

logger = logging.getLogger(__name__)
sheets = SheetsManager()

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(f'Привіт, {user.first_name}! Ласкаво просимо до бота.')

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Це допоміжне повідомлення. Ви можете використовувати наступні команди...')

def get_content(update: Update, context: CallbackContext) -> None:
    try:
        content = sheets.get_all_records("content")

        if not content:
            update.message.reply_text("Вибачте, зараз немає доступного контенту.")
            return

        first_item = content[0]
        title = first_item.get('title', 'Без назви')
        description = first_item.get('description', 'Без опису')

        keyboard = [
            [
                InlineKeyboardButton("Деталі", callback_data=f"content_details_{first_item.get('id', 0)}"),
                InlineKeyboardButton("Наступний", callback_data="next_content")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
            f"*{title}*\n\n{description}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Помилка в get_content: {e}")
        update.message.reply_text("Сталася помилка при отриманні контенту.")

def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    data = query.data

    if data.startswith("content_details_"):
        content_id = data.split("_")[-1]
        try:
            # У реальному додатку тут буде отримання контенту за ID
            query.edit_message_text(text=f"Детальна інформація для контенту #{content_id}")
        except Exception as e:
            logger.error(f"Помилка в button_callback: {e}")
            query.edit_message_text(text="Помилка при отриманні деталей.")

    elif data == "next_content":
        query.edit_message_text(text="Наступний елемент контенту буде тут")