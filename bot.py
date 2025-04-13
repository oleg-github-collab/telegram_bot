#!/usr/bin/env python3
import logging
import os
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from telegram import Update

# Import configuration
from config import BOT_TOKEN, BOT_MODE, WEBHOOK_URL, PORT, logger

# Import handlers
from handlers import start_command, button_callback, handle_yoga_registration, handle_admin_input

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by Updates."""
    logger.error(f"Update {update} caused error {context.error}")

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))

    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))

    # Add message handler for registration process
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_yoga_registration))

    # Add admin message handler (same handler as registration but will check admin state)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_input))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    if BOT_MODE.lower() == 'webhook' and WEBHOOK_URL:
        # Start webhook mode
        logger.info(f"Starting bot in webhook mode on port {PORT}")
        application.run_webhook(
            listen="0.0.0.0",
            port=int(PORT),
            url_path=BOT_TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
        )
    else:
        # Start polling mode
        logger.info("Starting bot in polling mode")
        application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()