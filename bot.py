import os
import logging
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler,
    MessageHandler, Filters, ConversationHandler
)
from config import BOT_TOKEN
from handlers import (
    start, help_command, get_content, button_callback,
    admin_panel, admin_button_callback, title_handler,
    description_handler, content_handler, confirmation_handler,
    delete_content_callback,
    TITLE, DESCRIPTION, CONTENT, CONFIRMATION
)
from utils.helpers import setup_logger


# Налаштування логування
setup_logger()
logger = logging.getLogger(__name__)

def main() -> None:
    """Запуск бота."""
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Обробники команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("content", get_content))
    dispatcher.add_handler(CommandHandler("admin", admin_panel))

    # 🚀 ЗАПУСК В POLLING
    updater.start_polling()
    logger.info("Бот запущено в режимі polling.")
    updater.idle()
    
if __name__ == '__main__':
    main()