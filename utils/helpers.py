from datetime import datetime, timedelta
import calendar
import re
from typing import List, Dict, Any, Tuple, Union
import logging

logger = logging.getLogger(__name__)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def generate_calendar_keyboard(year: int = None, month: int = None) -> Tuple[List[List[Dict[str, str]]], str]:
    """Generate an inline keyboard with calendar for date selection"""
    # Default to current month
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
        
    # Get month name and create title
    month_name = calendar.month_name[month]
    title = f"{month_name} {year}"
    
    # Create calendar matrix
    cal = calendar.monthcalendar(year, month)
    
    # Initialize keyboard
    keyboard = []
    
    # Add days of week header
    days_row = []
    for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
        days_row.append({"text": day, "callback_data": "ignore"})
    keyboard.append(days_row)
    
    # Minimum date - tomorrow
    min_date = now.date() + timedelta(days=1)
    
    # Add date buttons
    for week in cal:
        week_row = []
        for day in week:
            if day == 0:
                # Empty day
                week_row.append({"text": " ", "callback_data": "ignore"})
            else:
                # Check if date is in the past
                current_date = datetime(year, month, day).date()
                if current_date < min_date:
                    # Past date - disable
                    week_row.append({"text": str(day), "callback_data": "ignore"})
                else:
                    # Future date - selectable
                    date_str = current_date.strftime("%Y-%m-%d")
                    week_row.append({"text": str(day), "callback_data": f"date_{date_str}"})
        
        if week_row:
            keyboard.append(week_row)
    
    # Add navigation buttons
    nav_row = []
    
    # Previous month
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1
    nav_row.append({"text": "« Prev", "callback_data": f"calendar_{prev_year}_{prev_month}"})
    
    # Back to main
    nav_row.append({"text": "🏠 Menu", "callback_data": "back_to_main"})
    
    # Next month
    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1
    nav_row.append({"text": "Next »", "callback_data": f"calendar_{next_year}_{next_month}"})
    
    keyboard.append(nav_row)
    
    return keyboard, title

def format_event_details(event: Dict[str, Any], lang: str) -> str:
    """Format event details based on language"""
    try:
        title = event.get(f'title_{lang}', '')
        if not title:  # Fallback
            title = event.get('title_uk', event.get('title_en', event.get('title_de', 'Untitled Event')))
            
        description = event.get(f'description_{lang}', '')
        if not description:  # Fallback
            description = event.get('description_uk', event.get('description_en', 
                                   event.get('description_de', 'No description available')))
        
        date = event.get('date', '')
        if date:
            try:
                # Format date as DD.MM.YYYY
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                date = date_obj.strftime("%d.%m.%Y")
            except:
                pass
                
        return {
            'title': title,
            'date': date,
            'time': event.get('time', ''),
            'location': event.get('location', ''),
            'price': event.get('price', ''),
            'description': description
        }
    except Exception as e:
        logger.error(f"Error formatting event: {e}")
        return {
            'title': 'Error',
            'date': '',
            'time': '',
            'location': '',
            'price': '',
            'description': 'Error formatting event details'
        }