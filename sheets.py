import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import SPREADSHEET_ID, CREDENTIALS_FILE
import logging

logger = logging.getLogger(__name__)

class SheetsManager:
    def __init__(self):
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.creds = None
        self.client = None
        self.sheet = None
        self.initialize()

    def initialize(self):
        try:
            print(f"📁 Завантажуємо {CREDENTIALS_FILE}")
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, self.scope)
            self.client = gspread.authorize(self.creds)
            print(f"🔑 Авторизовано, пробуємо підключитись до: {SPREADSHEET_ID}")
            self.sheet = self.client.open_by_key(SPREADSHEET_ID)
            print(f"✅ Успішно підключено до таблиці: {self.sheet.title}")
        except Exception as e:
            print(f"❌ ПОМИЛКА: {e}")
            raise

    def get_worksheet(self, name):
        """Отримати аркуш за назвою, створити якщо не існує."""
        try:
            return self.sheet.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            return self.sheet.add_worksheet(title=name, rows=1000, cols=20)

    def get_all_records(self, worksheet_name):
        worksheet = self.get_worksheet(worksheet_name)
        return worksheet.get_all_records()

    def append_row(self, worksheet_name, row_data):
        worksheet = self.get_worksheet(worksheet_name)
        worksheet.append_row(row_data)
        return True

    def update_cell(self, worksheet_name, row, col, value):
        worksheet = self.get_worksheet(worksheet_name)
        worksheet.update_cell(row, col, value)
        return True

    def find_cell(self, worksheet_name, query):
        worksheet = self.get_worksheet(worksheet_name)
        try:
            return worksheet.find(query)
        except gspread.exceptions.CellNotFound:
            return None

    def get_row(self, worksheet_name, row_number):
        worksheet = self.get_worksheet(worksheet_name)
        return worksheet.row_values(row_number)

    def delete_row(self, worksheet_name, row_number):
        worksheet = self.get_worksheet(worksheet_name)
        worksheet.delete_row(row_number)
        return True
