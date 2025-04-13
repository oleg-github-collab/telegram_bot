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
from utils import setup_logger

# Налаштування логування
setup_logger()
logger = logging.getLogger(__name__)

def main() -> None:
    """Запуск бота."""
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Обробники команд (залишіть ваші існуючі обробники)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("content", get_content))
    dispatcher.add_handler(CommandHandler("admin", admin_panel))

    # Зберігаємо всі ваші існуючі обробники...

    # Зміна режиму з polling на webhook
    webhook_url = os.getenv('WEBHOOK_URL', '')
    port = int(os.getenv('PORT', '8443'))

    if not webhook_url:
        logger.error("WEBHOOK_URL не вказано в .env файлі!")
        return

    # Налаштування і запуск вебхука
    updater.start_webhook(
        listen='0.0.0.0',
        port=port,
        url_path=BOT_TOKEN,
        webhook_url=f'{webhook_url}/{BOT_TOKEN}'
    )

    logger.info(f"Бот запущено з вебхуком на {webhook_url}")
    updater.idle()

if __name__ == '__main__':
    main()