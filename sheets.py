import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import SPREADSHEET_ID, CREDENTIALS_FILE

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
        print(f"📁 Завантажуємо {CREDENTIALS_FILE}")
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, self.scope)
        self.client = gspread.authorize(self.creds)
        print(f"🔑 Авторизовано, пробуємо підключитись до: {SPREADSHEET_ID}")
        self.sheet = self.client.open_by_key(SPREADSHEET_ID)
        print(f"✅ Успішно підключено до таблиці: {self.sheet.title}")

    def get_worksheet(self, name):
        try:
            return self.sheet.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            return self.sheet.add_worksheet(title=name, rows=1000, cols=20)

    def append_row(self, worksheet_name, row_data):
        worksheet = self.get_worksheet(worksheet_name)
        worksheet.append_row(row_data)
        return True

    def get_all_records(self, worksheet_name):
        worksheet = self.get_worksheet(worksheet_name)
        return worksheet.get_all_records()
