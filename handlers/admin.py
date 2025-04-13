from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
import logging
from utils import is_admin
from sheets import SheetsManager

logger = logging.getLogger(__name__)
sheets = SheetsManager()

# Стани для додавання контенту
TITLE, DESCRIPTION, CONTENT, CONFIRMATION = range(4)

# Поточний контент, що додається
current_content = {}

def admin_panel(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    if not is_admin(user_id):
        update.message.reply_text("У вас немає доступу до адміністративної панелі.")
        return

    keyboard = [
        [InlineKeyboardButton("Додати контент", callback_data="admin_add_content")],
        [InlineKeyboardButton("Переглянути контент", callback_data="admin_view_content")],
        [InlineKeyboardButton("Видалити контент", callback_data="admin_delete_content")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "Панель адміністратора. Виберіть дію:",
        reply_markup=reply_markup
    )

def admin_button_callback(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    user_id = update.effective_user.id
    if not is_admin(user_id):
        query.edit_message_text("У вас немає доступу до цієї функції.")
        return ConversationHandler.END

    data = query.data

    if data == "admin_add_content":
        query.edit_message_text("Додавання нового контенту. Введіть заголовок:")
        return TITLE

    elif data == "admin_view_content":
        try:
            content = sheets.get_all_records("content")
            if not content:
                query.edit_message_text("Контент відсутній.")
                return ConversationHandler.END

            message = "Список контенту:\n\n"
            for idx, item in enumerate(content, 1):
                message += f"{idx}. {item.get('title', 'Без назви')}\n"

            query.edit_message_text(message)
        except Exception as e:
            logger.error(f"Помилка перегляду контенту: {e}")
            query.edit_message_text("Помилка при перегляді контенту.")

        return ConversationHandler.END

    elif data == "admin_delete_content":
        try:
            content = sheets.get_all_records("content")
            if not content:
                query.edit_message_text("Немає контенту для видалення.")
                return ConversationHandler.END

            keyboard = []
            for idx, item in enumerate(content, 1):
                keyboard.append([
                    InlineKeyboardButton(
                        f"{idx}. {item.get('title', 'Без назви')}",
                        callback_data=f"delete_{idx}"
                    )
                ])

            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                "Виберіть контент для видалення:",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Помилка видалення: {e}")
            query.edit_message_text("Помилка при спробі видалення.")

        return ConversationHandler.END

    return ConversationHandler.END

def title_handler(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("У вас немає доступу до цієї функції.")
        return ConversationHandler.END

    title = update.message.text
    current_content['title'] = title

    update.message.reply_text("Чудово! Тепер введіть опис контенту:")
    return DESCRIPTION

def description_handler(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("У вас немає доступу до цієї функції.")
        return ConversationHandler.END

    description = update.message.text
    current_content['description'] = description

    update.message.reply_text("Добре! Тепер введіть основний контент:")
    return CONTENT

def content_handler(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("У вас немає доступу до цієї функції.")
        return ConversationHandler.END

    content_text = update.message.text
    current_content['content'] = content_text

    message = (
        f"Перевірте інформацію:\n\n"
        f"Заголовок: {current_content['title']}\n"
        f"Опис: {current_content['description']}\n"
        f"Контент: {current_content['content'][:100]}..."
    )

    keyboard = [
        [
            InlineKeyboardButton("Підтвердити", callback_data="confirm_content"),
            InlineKeyboardButton("Скасувати", callback_data="cancel_content")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(message, reply_markup=reply_markup)
    return CONFIRMATION

def confirmation_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    user_id = update.effective_user.id
    if not is_admin(user_id):
        query.edit_message_text("У вас немає доступу до цієї функції.")
        return ConversationHandler.END

    data = query.data

    if data == "confirm_content":
        try:
            # Отримання існуючого контенту для визначення наступного ID
            existing_content = sheets.get_all_records("content")
            next_id = 1
            if existing_content:
                next_id = max([int(item.get('id', 0)) for item in existing_content]) + 1

            current_content['id'] = next_id
            current_content['created_by'] = user_id

            # Перетворення словника на дані рядка
            row_data = [
                current_content.get('id', ''),
                current_content.get('title', ''),
                current_content.get('description', ''),
                current_content.get('content', ''),
                current_content.get('created_by', '')
            ]

            # Перевірка наявності заголовків
            content_sheet = sheets.get_worksheet("content")
            headers = content_sheet.row_values(1)
            if not headers:
                content_sheet.append_row(['id', 'title', 'description', 'content', 'created_by'])

            # Додавання нового контенту
            sheets.append_row("content", row_data)
            query.edit_message_text("Контент успішно додано!")
        except Exception as e:
            logger.error(f"Помилка додавання контенту: {e}")
            query.edit_message_text("Помилка при додаванні контенту.")

    elif data == "cancel_content":
        query.edit_message_text("Додавання контенту скасовано.")

    current_content.clear()
    return ConversationHandler.END

def delete_content_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    user_id = update.effective_user.id
    if not is_admin(user_id):
        query.edit_message_text("У вас немає доступу до цієї функції.")
        return

    data = query.data
    if data.startswith("delete_"):
        try:
            index = int(data.split("_")[1])

            content = sheets.get_all_records("content")
            if index <= len(content):
                sheets.delete_row("content", index + 1)
                query.edit_message_text(f"Контент #{index} успішно видалено.")
            else:
                query.edit_message_text("Контент не знайдено.")
        except Exception as e:
            logger.error(f"Помилка видалення: {e}")
            query.edit_message_text("Помилка при видаленні контенту.")