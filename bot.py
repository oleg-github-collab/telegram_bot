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

    # 📌 Основні команди
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("content", get_content))
    dispatcher.add_handler(CommandHandler("admin", admin_panel))

    # 📌 Обробка кнопок (InlineKeyboardButton)
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    # 📌 ConversationHandler для адмінів (наприклад: додавання контенту)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_panel)],
        states={
            TITLE: [MessageHandler(Filters.text & ~Filters.command, title_handler)],
            DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, description_handler)],
            CONTENT: [MessageHandler(Filters.text & ~Filters.command, content_handler)],
            CONFIRMATION: [CallbackQueryHandler(confirmation_handler)],
        },
        fallbacks=[CallbackQueryHandler(delete_content_callback)]
    )
    dispatcher.add_handler(conv_handler)

    # 🚀 Запуск в режимі POLLING
    updater.start_polling()
    logger.info("✅ Бот запущено в режимі polling.")
    updater.idle()

if __name__ == '__main__':
    main()
