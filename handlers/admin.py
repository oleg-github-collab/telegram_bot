from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from utils.helpers import is_admin

TITLE, DESCRIPTION, CONTENT, CONFIRMATION = range(4)

def admin_panel(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return update.message.reply_text("Доступ заборонено.")
    update.message.reply_text("Адмін панель: /add_content")

def admin_button_callback(update: Update, context: CallbackContext):
    pass  # Порожній для прикладу

def title_handler(update: Update, context: CallbackContext):
    return TITLE

def description_handler(update: Update, context: CallbackContext):
    return DESCRIPTION

def content_handler(update: Update, context: CallbackContext):
    return CONTENT

def confirmation_handler(update: Update, context: CallbackContext):
    return CONFIRMATION

def delete_content_callback(update: Update, context: CallbackContext):
    pass  # Порожній для прикладу
