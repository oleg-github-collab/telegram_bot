#!/bin/bash

echo "Початок налаштування Telegram Bot з Google Sheets інтеграцією..."

# Оновлення системи
echo "Оновлення пакетів системи..."
sudo apt update
sudo apt upgrade -y

# Встановлення залежностей
echo "Встановлення необхідних пакетів..."
sudo apt install -y python3-pip python3-venv git

# Створення директорії для бота
echo "Створення директорії для проекту..."
mkdir -p /opt/telegram_bot
cd /opt/telegram_bot

# Копіювання файлів проекту
echo "Налаштування файлів проекту..."
# Якщо ви використовуєте Git
# git clone ваш_репозиторій .

# Створення структури каталогів
mkdir -p handlers utils deploy/systemd

# Створення віртуального середовища
echo "Створення Python віртуального середовища..."
python3 -m venv venv
source venv/bin/activate

# Налаштування .env файлу
echo "Налаштування .env файлу..."
cat > .env << EOL
BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_telegram_id_here
SPREADSHEET_ID=your_spreadsheet_id_here
CREDENTIALS_FILE=credentials.json
LOG_LEVEL=INFO
EOL

echo "Не забудьте змінити значення в .env файлі на свої власні!"

# Встановлення залежностей
echo "Встановлення Python залежностей..."
pip install -r requirements.txt

# Копіювання credentials.json
echo "ВАЖЛИВО: Не забудьте завантажити credentials.json від Google API в кореневу директорію проекту!"

# Створення systemd сервісу
echo "Налаштування systemd сервісу..."
sudo cp deploy/systemd/telegram-bot.service /etc/systemd/system/

# Встановлення прав
echo "Налаштування прав доступу..."
sudo chmod +x bot.py
sudo chown -R $(whoami):$(whoami) /opt/telegram_bot

# Включення та запуск сервісу
echo "Включення та запуск сервісу..."
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

echo "======================================================"
echo "Встановлення телеграм-бота успішно завершено!"
echo "Перевірити статус: sudo systemctl status telegram-bot"
echo "Переглянути логи: sudo journalctl -u telegram-bot -f"
echo "======================================================"