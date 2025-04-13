from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import logging
from typing import Dict, Any, List
from datetime import datetime

from utils.localization import get_text
from sheets import SheetsClient
from config import ADMIN_USER_IDS

logger = logging.getLogger(__name__)
sheets_client = SheetsClient()

# Admin state
admin_state: Dict[int, Dict[str, Any]] = {}

async def is_admin(update: Update) -> bool:
    """Check if user is admin"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_USER_IDS:
        user_lang = sheets_client.get_user_language(user_id)
        if update.callback_query:
            await update.callback_query.answer(get_text("admin_only", user_lang))
        else:
            await update.message.reply_text(get_text("admin_only", user_lang))
        return False
    return True

async def admin_panel(update: Update, context: CallbackContext) -> None:
    """Show admin panel"""
    if not await is_admin(update):
        return
    
    query = update.callback_query
    user_id = update.effective_user.id
    user_lang = sheets_client.get_user_language(user_id)
    
    keyboard = [
        [InlineKeyboardButton(get_text("view_registrations", user_lang), callback_data="admin_registrations")],
        [InlineKeyboardButton(get_text("add_event", user_lang), callback_data="admin_add_event")],
        [InlineKeyboardButton(get_text("send_broadcast", user_lang), callback_data="admin_broadcast")],
        [InlineKeyboardButton(get_text("back", user_lang), callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=get_text("admin_panel", user_lang),
        reply_markup=reply_markup
    )

async def admin_view_registrations(update: Update, context: CallbackContext) -> None:
    """Show yoga registrations"""
    if not await is_admin(update):
        return
    
    query = update.callback_query
    user_id = update.effective_user.id
    user_lang = sheets_client.get_user_language(user_id)
    
    # Show loading message
    await query.edit_message_text(
        text=get_text("loading", user_lang)
    )
    
    # Get registrations from Google Sheets
    registrations = sheets_client.get_all_registrations()
    
    if not registrations:
        message_text = "No registrations found."
    else:
        # Limit to 10 most recent registrations to avoid message length limits
        recent_registrations = registrations[:10]
        
        message_text = "*Most Recent Yoga Registrations:*\n\n"
        
        for reg in recent_registrations:
            message_text += f"*ID:* {reg.get('id', 'N/A')}\n"
            message_text += f"*Name:* {reg.get('name', 'N/A')}\n"
            message_text += f"*Email:* {reg.get('email', 'N/A')}\n"
            message_text += f"*Date:* {reg.get('date', 'N/A')}\n"
            message_text += f"*Class:* {reg.get('class_type', 'N/A')}\n"
            
            comment = reg.get('comment', '')
            if comment:
                message_text += f"*Comment:* {comment}\n"
                
            message_text += f"*Registered:* {reg.get('registered_at', 'N/A')}\n"
            message_text += "\n---\n\n"
        
        if len(registrations) > 10:
            message_text += f"\n_Showing 10 of {len(registrations)} registrations._"
    
    keyboard = [[InlineKeyboardButton(get_text("back", user_lang), callback_data="admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def admin_add_event_start(update: Update, context: CallbackContext) -> None:
    """Start process to add a new event"""
    if not await is_admin(update):
        return
    
    query = update.callback_query
    user_id = update.effective_user.id
    user_lang = sheets_client.get_user_language(user_id)
    
    # Initialize admin state
    admin_state[user_id] = {"step": "title_uk"}
    
    await query.edit_message_text(
        text="Please enter the event title in Ukrainian:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(get_text("back", user_lang), callback_data="admin")
        ]])
    )

async def handle_admin_input(update: Update, context: CallbackContext) -> None:
    """Handle admin input for adding events or sending broadcasts"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_USER_IDS:
        return
    
    if user_id not in admin_state:
        return
    
    user_lang = sheets_client.get_user_language(user_id)
    current_step = admin_state[user_id].get("step", "")
    
    # Handle event creation steps
    if current_step.startswith("title_"):
        language = current_step.split("_")[1]
        admin_state[user_id][f"title_{language}"] = update.message.text
        
        if language == "uk":
            admin_state[user_id]["step"] = "title_en"
            await update.message.reply_text("Please enter the event title in English:")
        elif language == "en":
            admin_state[user_id]["step"] = "title_de"
            await update.message.reply_text("Please enter the event title in German:")
        elif language == "de":
            admin_state[user_id]["step"] = "date"
            await update.message.reply_text("Please enter the event date (YYYY-MM-DD):")
    
    elif current_step == "date":
        # Validate date format
        date_text = update.message.text
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            admin_state[user_id]["date"] = date_text
            admin_state[user_id]["step"] = "time"
            await update.message.reply_text("Please enter the event time (e.g., 18:00):")
        except ValueError:
            await update.message.reply_text("Invalid date format. Please use YYYY-MM-DD:")
    
    elif current_step == "time":
        admin_state[user_id]["time"] = update.message.text
        admin_state[user_id]["step"] = "location"
        await update.message.reply_text("Please enter the event location:")
    
    elif current_step == "location":
        admin_state[user_id]["location"] = update.message.text
        admin_state[user_id]["step"] = "price"
        await update.message.reply_text("Please enter the event price:")
    
    elif current_step == "price":
        admin_state[user_id]["price"] = update.message.text
        admin_state[user_id]["step"] = "description_uk"
        await update.message.reply_text("Please enter the event description in Ukrainian:")
    
    elif current_step.startswith("description_"):
        language = current_step.split("_")[1]
        admin_state[user_id][f"description_{language}"] = update.message.text
        
        if language == "uk":
            admin_state[user_id]["step"] = "description_en"
            await update.message.reply_text("Please enter the event description in English:")
        elif language == "en":
            admin_state[user_id]["step"] = "description_de"
            await update.message.reply_text("Please enter the event description in German:")
        elif language == "de":
            # Final step - add event
            event_data = {
                'title_uk': admin_state[user_id].get("title_uk", ""),
                'title_en': admin_state[user_id].get("title_en", ""),
                'title_de': admin_state[user_id].get("title_de", ""),
                'date': admin_state[user_id].get("date", ""),
                'time': admin_state[user_id].get("time", ""),
                'location': admin_state[user_id].get("location", ""),
                'price': admin_state[user_id].get("price", ""),
                'description_uk': admin_state[user_id].get("description_uk", ""),
                'description_en': admin_state[user_id].get("description_en", ""),
                'description_de': admin_state[user_id].get("description_de", "")
            }
            
            success, message = sheets_client.add_event(event_data)
            
            if success:
                await update.message.reply_text(
                    f"✅ {message}",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(get_text("back", user_lang), callback_data="admin")
                    ]])
                )
            else:
                await update.message.reply_text(
                    f"❌ {message}",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(get_text("back", user_lang), callback_data="admin")
                    ]])
                )
            
            # Clear admin state
            del admin_state[user_id]
    
    # Handle broadcast steps
    elif current_step == "broadcast_text":
        broadcast_text = update.message.text
        admin_state[user_id]["broadcast_text"] = broadcast_text
        admin_state[user_id]["step"] = "broadcast_confirm"
        
        await update.message.reply_text(
            f"Your broadcast message:\n\n{broadcast_text}\n\nAre you sure you want to send this to all users?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Yes, send it", callback_data="broadcast_send")],
                [InlineKeyboardButton("No, cancel", callback_data="admin")]
            ])
        )

async def admin_broadcast_start(update: Update, context: CallbackContext) -> None:
    """Start process to send a broadcast message"""
    if not await is_admin(update):
        return
    
    query = update.callback_query
    user_id = update.effective_user.id
    user_lang = sheets_client.get_user_language(user_id)
    
    # Initialize admin state
    admin_state[user_id] = {"step": "broadcast_text"}
    
    await query.edit_message_text(
        text="Please enter the broadcast message text:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(get_text("back", user_lang), callback_data="admin")
        ]])
    )

async def admin_broadcast_send(update: Update, context: CallbackContext) -> None:
    """Send broadcast message to all users"""
    if not await is_admin(update):
        return
    
    query = update.callback_query
    user_id = update.effective_user.id
    user_lang = sheets_client.get_user_language(user_id)
    
    if user_id not in admin_state or "broadcast_text" not in admin_state[user_id]:
        await query.edit_message_text(
            text="Error: Broadcast text not found.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text("back", user_lang), callback_data="admin")
            ]])
        )
        return
    
    broadcast_text = admin_state[user_id]["broadcast_text"]
    
    # Get all users from Google Sheets
    users = sheets_client.get_all_users()
    
    if not users:
        await query.edit_message_text(
            text="No users found to send broadcast to.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text("back", user_lang), callback_data="admin")
            ]])
        )
        return
    
    # Send message to all users
    sent_count = 0
    failed_count = 0
    
    # Update message to show progress
    progress_message = await query.edit_message_text(
        text=f"Sending broadcast to {len(users)} users...\nSent: 0\nFailed: 0"
    )
    
    for user in users:
        try:
            user_id_str = user.get("user_id", "")
            if not user_id_str or not user_id_str.isdigit():
                failed_count += 1
                continue
                
            recipient_id = int(user_id_str)
            await context.bot.send_message(
                chat_id=recipient_id,
                text=broadcast_text,
                parse_mode='Markdown'
            )
            sent_count += 1
            
            # Update progress every 10 users
            if sent_count % 10 == 0:
                await progress_message.edit_text(
                    text=f"Sending broadcast...\nSent: {sent_count}\nFailed: {failed_count}"
                )
        except Exception as e:
            logger.error(f"Failed to send broadcast to user {user.get('user_id')}: {e}")
            failed_count += 1
    
    # Clear admin state
    del admin_state[user_id]
    
    # Final report
    await progress_message.edit_text(
        text=f"Broadcast complete!\nSent: {sent_count}\nFailed: {failed_count}",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(get_text("back", user_lang), callback_data="admin")
        ]])
    )