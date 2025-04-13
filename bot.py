# 📁 bot.py
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from utils.helpers import setup_logger, translate, LANGUAGES, get_main_menu
from config import BOT_TOKEN

# Setup logger
setup_logger()

# Start command
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    context.user_data.clear()
    keyboard = [[InlineKeyboardButton(lang, callback_data=f"lang_{code}")] for code, lang in LANGUAGES.items()]
    update.message.reply_text("Please choose a language / Bitte Sprache wählen / Оберіть мову:", reply_markup=InlineKeyboardMarkup(keyboard))

# Language selection
def select_language(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    lang_code = query.data.split("_")[1]
    context.user_data['lang'] = lang_code
    query.edit_message_text(text=translate("Вітаю у боті Марини Камінської!", lang_code), reply_markup=get_main_menu(lang_code))

# Main menu callback
def handle_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    lang = context.user_data.get('lang', 'ua')
    data = query.data
    query.answer()

    if data == "menu_events":
        query.edit_message_text(translate("Ось список подій, які плануються...", lang), reply_markup=get_main_menu(lang))
    elif data == "menu_yoga":
        query.edit_message_text(translate("Оберіть зручний час для заняття йогою...", lang), reply_markup=get_main_menu(lang))
    elif data == "menu_schedule":
        query.edit_message_text(translate("Ось розклад найближчих подій та занять:", lang), reply_markup=get_main_menu(lang))
    elif data == "menu_shop":
        query.edit_message_text(translate("Перейдіть до інтернет-магазину: https://marina-art-shop.com", lang), reply_markup=get_main_menu(lang))
    elif data == "menu_about":
        query.edit_message_text(translate("Марина Камінська — художниця та викладачка йоги...", lang), reply_markup=get_main_menu(lang))
    elif data == "menu_main":
        query.edit_message_text(translate("Головне меню:", lang), reply_markup=get_main_menu(lang))


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(select_language, pattern="^lang_"))
    dp.add_handler(CallbackQueryHandler(handle_menu, pattern="^menu_"))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
