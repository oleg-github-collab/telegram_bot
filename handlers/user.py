from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
import logging
from typing import Dict, Any
from datetime import datetime

from utils.localization import get_text
from utils.helpers import validate_email, generate_calendar_keyboard
from sheets import SheetsClient
from config import ADMIN_USER_IDS

logger = logging.getLogger(__name__)
sheets_client = SheetsClient()

# User registration state
user_state: Dict[int, Dict[str, Any]] = {}
# Store URL
STORE_URL = "https://marina-kaminska-art.myshopify.com/"

async def start_command(update: Update, context: CallbackContext) -> None:
    """Handle /start command - Entry point"""
    user_id = update.effective_user.id
    
    # Clear user state
    if user_id in user_state:
        del user_state[user_id]
    
    # Check if user has a language set
    user_lang = sheets_client.get_user_language(user_id)
    
    if not user_lang:
        # Ask for language
        await language_selection(update, context)
    else:
        # Go to main menu
        await main_menu(update, context)

async def language_selection(update: Update, context: CallbackContext) -> None:
    """Show language selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_uk"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Оберіть мову / Select language / Sprache wählen:",
        reply_markup=reply_markup
    )

async def main_menu(update: Update, context: CallbackContext) -> None:
    """Show main menu"""
    user_id = update.effective_user.id
    user_lang = sheets_client.get_user_language(user_id)
    
    keyboard = [
        [
            InlineKeyboardButton(get_text("events", user_lang), callback_data="events"),
            InlineKeyboardButton(get_text("yoga_signup", user_lang), callback_data="yoga_signup")
        ],
        [
            InlineKeyboardButton(get_text("schedule", user_lang), callback_data="schedule"),
            InlineKeyboardButton(get_text("store", user_lang), callback_data="store")
        ],
        [
            InlineKeyboardButton(get_text("about_me", user_lang), callback_data="about"),
            InlineKeyboardButton("🌐 " + {
                'uk': 'Українська',
                'en': 'English',
                'de': 'Deutsch'
            }[user_lang], callback_data="change_language")
        ]
    ]
    
    # Add admin button for administrators
    if user_id in ADMIN_USER_IDS:
        keyboard.append([
            InlineKeyboardButton(get_text("admin_panel", user_lang), callback_data="admin")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        # Try to edit message if it's a callback
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=get_text("main_menu", user_lang),
                reply_markup=reply_markup
            )
        else:
            # Otherwise send new message
            await update.message.reply_text(
                text=get_text("main_menu", user_lang),
                reply_markup=reply_markup
            )
    except Exception as e:
        # If edit fails, send new message
        if update.message:
            await update.message.reply_text(
                text=get_text("main_menu", user_lang),
                reply_markup=reply_markup
            )
        else:
            # Get chat id from callback query
            chat_id = update.callback_query.message.chat_id
            await context.bot.send_message(
                chat_id=chat_id,
                text=get_text("main_menu", user_lang),
                reply_markup=reply_markup
            )

async def events_menu(update: Update, context: CallbackContext) -> None:
    """Show list of events"""
    query = update.callback_query
    user_id = update.effective_user.id
    user_lang = sheets_client.get_user_language(user_id)
    
    # Show loading message
    await query.edit_message_text(
        text=get_text("loading", user_lang)
    )
    
    # Get events from Google Sheets
    events = sheets_client.get_events()
    
    if not events:
        # No events available
        keyboard = [[InlineKeyboardButton(get_text("back", user_lang), callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=get_text("no_events", user_lang),
            reply_markup=reply_markup
        )
        return
    
    # Show first event
    current_event = events[0]
    event_details = format_event_details(current_event, user_lang)
    
    # Create keyboard
    keyboard = [
        [InlineKeyboardButton(get_text("sign_up", user_lang), callback_data=f"signup_event_{current_event['id']}")],
    ]
    
    # Add navigation if there are more events
    nav_row = []
    if len(events) > 1:
        nav_row.append(InlineKeyboardButton("⏩ Next", callback_data="next_event_1"))
    
    nav_row.append(InlineKeyboardButton(get_text("back", user_lang), callback_data="back_to_main"))
    keyboard.append(nav_row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Format message with event details
    message_text = get_text("event_details", user_lang).format(
        title=event_details['title'],
        date=event_details['date'],
        time=event_details['time'],
        location=event_details['location'],
        price=event_details['price'],
        description=event_details['description']
    )
    
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def yoga_signup(update: Update, context: CallbackContext) -> None:
    """Start yoga signup process"""
    query = update.callback_query
    user_id = update.effective_user.id
    user_lang = sheets_client.get_user_language(user_id)
    
    # Initialize user state for registration
    user_state[user_id] = {"step": "name"}
    
    # Ask for name
    await query.edit_message_text(
        text=get_text("name_prompt", user_lang),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(get_text("back", user_lang), callback_data="back_to_main")
        ]])
    )

async def handle_yoga_registration(update: Update, context: CallbackContext) -> None:
    """Handle yoga registration process"""
    user_id = update.effective_user.id
    user_lang = sheets_client.get_user_language(user_id)
    
    # Check if user is in registration process
    if user_id not in user_state:
        await update.message.reply_text(
            text=get_text("error_occurred", user_lang),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text("back", user_lang), callback_data="back_to_main")
            ]])
        )
        return
    
    current_step = user_state[user_id].get("step", "")
    
    if current_step == "name":
        # Save name and ask for email
        user_state[user_id]["name"] = update.message.text
        user_state[user_id]["step"] = "email"
        
        await update.message.reply_text(
            text=get_text("email_prompt", user_lang),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text("back", user_lang), callback_data="back_to_main")
            ]])
        )
    
    elif current_step == "email":
        email = update.message.text
        
        # Validate email
        if not validate_email(email):
            await update.message.reply_text(
                "❌ Invalid email. Please enter a valid email address.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text("back", user_lang), callback_data="back_to_main")
                ]])
            )
            return
        
        # Save email and show calendar
        user_state[user_id]["email"] = email
        user_state[user_id]["step"] = "date"
        
        # Generate calendar keyboard
        keyboard, title = generate_calendar_keyboard()
        
        await update.message.reply_text(
            text=get_text("date_prompt", user_lang),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif current_step == "class_type":
        # Save class type and ask for comment
        user_state[user_id]["class_type"] = update.message.text
        user_state[user_id]["step"] = "comment"
        
        # Create keyboard with skip option
        keyboard = [[InlineKeyboardButton(get_text("skip", user_lang), callback_data="skip_comment")]]
        
        await update.message.reply_text(
            text=get_text("comment_prompt", user_lang),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif current_step == "comment":
        # Save comment and finalize registration
        user_state[user_id]["comment"] = update.message.text
        
        # Register to class
        success, message = sheets_client.add_yoga_registration(
            name=user_state[user_id].get("name", ""),
            email=user_state[user_id].get("email", ""),
            date=user_state[user_id].get("date", ""),
            class_type=user_state[user_id].get("class_type", ""),
            comment=user_state[user_id].get("comment", "")
        )
        
        if success:
            # Registration successful
            await update.message.reply_text(
                text=get_text("registration_success", user_lang),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text("back", user_lang), callback_data="back_to_main")
                ]])
            )
        else:
            # Registration failed
            await update.message.reply_text(
                text=f"❌ {message}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text("back", user_lang), callback_data="back_to_main")
                ]])
            )
        
        # Clear user state
        del user_state[user_id]

async def schedule_menu(update: Update, context: CallbackContext) -> None:
    """Show class schedule"""
    query = update.callback_query
    user_id = update.effective_user.id
    user_lang = sheets_client.get_user_language(user_id)
    
    # Show loading message
    await query.edit_message_text(
        text=get_text("loading", user_lang)
    )
    
    # Get schedule from Google Sheets
    schedule = sheets_client.get_schedule()
    
    # Prepare message
    if not schedule:
        message_text = "No schedule available."
    else:
        message_text = "*🗓 " + get_text("schedule", user_lang) + "*\n\n"
        current_day = ""
        
        for item in schedule:
            day = item.get("day", "")
            if day != current_day:
                current_day = day
                message_text += f"\n*{day}*\n"
            
            time = item.get("time", "")
            class_name = item.get(f"class_{user_lang}", "") or item.get("class_uk", "") or item.get("class_en", "")
            notes = item.get("notes", "")
            
            message_text += f"• {time} - {class_name}"
            if notes:
                message_text += f" ({notes})"
            message_text += "\n"
    
    # Create keyboard
    keyboard = [[InlineKeyboardButton(get_text("back", user_lang), callback_data="back_to_main")]]
    if schedule:  # Add signup button if schedule exists
        keyboard.insert(0, [InlineKeyboardButton(get_text("yoga_signup", user_lang), callback_data="yoga_signup")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def store_menu(update: Update, context: CallbackContext) -> None:
    """Show store information"""
    query = update.callback_query
    user_id = update.effective_user.id
    user_lang = sheets_client.get_user_language(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🛒 Online Store", url=STORE_URL)],
        [InlineKeyboardButton(get_text("back", user_lang), callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=get_text("store_text", user_lang),
        reply_markup=reply_markup
    )

async def about_menu(update: Update, context: CallbackContext) -> None:
    """Show about information"""
    query = update.callback_query
    user_id = update.effective_user.id
    user_lang = sheets_client.get_user_language(user_id)
    
    keyboard = [
        [
            InlineKeyboardButton("📸 Instagram", url="https://instagram.com/marina_kaminska_art"),
            InlineKeyboardButton("🌐 Website", url="https://www.marinakaminska.com")
        ],
        [InlineKeyboardButton(get_text("back", user_lang), callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=get_text("about_text", user_lang),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )