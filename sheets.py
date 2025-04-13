import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from config import SPREADSHEET_ID, CREDENTIALS_FILE

logger = logging.getLogger(__name__)

class SheetsClient:
    def __init__(self):
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.client = None
        self.sheet = None
        self.initialized = False
        self.initialize()
        
    def initialize(self) -> bool:
        """Initialize Google Sheets connection"""
        try:
            if not os.path.exists(CREDENTIALS_FILE):
                logger.error(f"Credentials file {CREDENTIALS_FILE} not found")
                return False
                
            if not SPREADSHEET_ID:
                logger.error("SPREADSHEET_ID not set in .env")
                return False
                
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, self.scope)
            self.client = gspread.authorize(self.creds)
            self.sheet = self.client.open_by_key(SPREADSHEET_ID)
            
            # Ensure required worksheets exist
            self._ensure_worksheet_exists('users')
            self._ensure_worksheet_exists('yoga_registrations')
            self._ensure_worksheet_exists('events')
            self._ensure_worksheet_exists('schedule')
            
            self.initialized = True
            logger.info(f"Successfully connected to Google Sheets: {self.sheet.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets: {e}")
            return False
            
    def _ensure_worksheet_exists(self, name: str) -> None:
        """Ensure a worksheet exists, create it if not"""
        try:
            try:
                self.sheet.worksheet(name)
            except gspread.exceptions.WorksheetNotFound:
                if name == 'users':
                    worksheet = self.sheet.add_worksheet(title=name, rows=1000, cols=3)
                    worksheet.append_row(["user_id", "language", "last_activity"])
                elif name == 'yoga_registrations':
                    worksheet = self.sheet.add_worksheet(title=name, rows=1000, cols=7)
                    worksheet.append_row(["id", "name", "email", "date", "class_type", "comment", "registered_at"])
                elif name == 'events':
                    worksheet = self.sheet.add_worksheet(title=name, rows=50, cols=10)
                    worksheet.append_row(["id", "title_uk", "title_en", "title_de", "date", "time", 
                                         "location", "price", "description_uk", "description_en", "description_de"])
                elif name == 'schedule':
                    worksheet = self.sheet.add_worksheet(title=name, rows=50, cols=6)
                    worksheet.append_row(["day", "time", "class_uk", "class_en", "class_de", "notes"])
                logger.info(f"Created worksheet: {name}")
        except Exception as e:
            logger.error(f"Error ensuring worksheet {name} exists: {e}")
    
    def set_user_language(self, user_id: int, language: str) -> bool:
        """Set user language preference"""
        if not self.initialized:
            return False
            
        try:
            worksheet = self.sheet.worksheet('users')
            
            # Check if user exists
            try:
                cell = worksheet.find(str(user_id))
                # Update language
                worksheet.update_cell(cell.row, 2, language)
                worksheet.update_cell(cell.row, 3, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            except gspread.exceptions.CellNotFound:
                # Add new user
                worksheet.append_row([str(user_id), language, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                
            return True
        except Exception as e:
            logger.error(f"Error setting user language: {e}")
            return False
    
    def get_user_language(self, user_id: int) -> str:
        """Get user language preference"""
        if not self.initialized:
            return 'uk'
            
        try:
            worksheet = self.sheet.worksheet('users')
            
            try:
                cell = worksheet.find(str(user_id))
                return worksheet.cell(cell.row, 2).value
            except gspread.exceptions.CellNotFound:
                return 'uk'  # Default language
        except Exception as e:
            logger.error(f"Error getting user language: {e}")
            return 'uk'
    
    def add_yoga_registration(self, name: str, email: str, date: str, 
                             class_type: str, comment: str) -> Tuple[bool, str]:
        """Add a new yoga class registration"""
        if not self.initialized:
            return False, "Google Sheets not initialized"
            
        try:
            worksheet = self.sheet.worksheet('yoga_registrations')
            
            # Get next ID
            try:
                all_values = worksheet.get_all_values()
                if len(all_values) <= 1:  # Only header row
                    next_id = 1
                else:
                    ids = [int(row[0]) for row in all_values[1:] if row[0].isdigit()]
                    next_id = max(ids) + 1 if ids else 1
            except:
                next_id = 1
                
            # Add registration
            worksheet.append_row([
                next_id, 
                name, 
                email, 
                date, 
                class_type, 
                comment, 
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            
            return True, f"Registration successful with ID {next_id}"
        except Exception as e:
            logger.error(f"Error adding yoga registration: {e}")
            return False, f"Error: {str(e)}"
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get all events"""
        if not self.initialized:
            return []
            
        try:
            worksheet = self.sheet.worksheet('events')
            
            # Get all records
            records = worksheet.get_all_records()
            
            # Sort by date (upcoming first)
            today = datetime.now().strftime("%Y-%m-%d")
            upcoming_events = [r for r in records if r.get('date', '') >= today]
            upcoming_events.sort(key=lambda x: x.get('date', ''))
            
            return upcoming_events
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return []
    
    def get_schedule(self) -> List[Dict[str, Any]]:
        """Get class schedule"""
        if not self.initialized:
            return []
            
        try:
            worksheet = self.sheet.worksheet('schedule')
            
            # Get all records
            records = worksheet.get_all_records()
            
            # Sort by day of week
            day_order = {
                'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
                'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
            }
            
            records.sort(key=lambda x: day_order.get(x.get('day', ''), 7))
            
            return records
        except Exception as e:
            logger.error(f"Error getting schedule: {e}")
            return []
    
    def add_event(self, event_data: Dict[str, str]) -> Tuple[bool, str]:
        """Add a new event"""
        if not self.initialized:
            return False, "Google Sheets not initialized"
            
        try:
            worksheet = self.sheet.worksheet('events')
            
            # Get next ID
            try:
                all_values = worksheet.get_all_values()
                if len(all_values) <= 1:  # Only header row
                    next_id = 1
                else:
                    ids = [int(row[0]) for row in all_values[1:] if row[0].isdigit()]
                    next_id = max(ids) + 1 if ids else 1
            except:
                next_id = 1
                
            # Add event
            worksheet.append_row([
                next_id,
                event_data.get('title_uk', ''),
                event_data.get('title_en', ''),
                event_data.get('title_de', ''),
                event_data.get('date', ''),
                event_data.get('time', ''),
                event_data.get('location', ''),
                event_data.get('price', ''),
                event_data.get('description_uk', ''),
                event_data.get('description_en', ''),
                event_data.get('description_de', '')
            ])
            
            return True, f"Event added successfully with ID {next_id}"
        except Exception as e:
            logger.error(f"Error adding event: {e}")
            return False, f"Error: {str(e)}"
    
    def get_all_registrations(self) -> List[Dict[str, Any]]:
        """Get all yoga registrations"""
        if not self.initialized:
            return []
            
        try:
            worksheet = self.sheet.worksheet('yoga_registrations')
            
            # Get all records
            records = worksheet.get_all_records()
            
            # Sort by registration date (newest first)
            records.sort(key=lambda x: x.get('registered_at', ''), reverse=True)
            
            return records
        except Exception as e:
            logger.error(f"Error getting registrations: {e}")
            return []
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all bot users"""
        if not self.initialized:
            return []
            
        try:
            worksheet = self.sheet.worksheet('users')
            
            # Get all records
            records = worksheet.get_all_records()
            
            return records
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []