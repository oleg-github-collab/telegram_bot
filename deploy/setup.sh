#!/bin/bash

# Сценарій для автоматичного налаштування Telegram-бота

echo "⚙️ Створюємо віртуальне середовище..."
python3 -m venv venv
source venv/bin/activate

echo "⬇️ Встановлюємо залежності..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Залежності встановлено."

echo "⚙️ Налаштовуємо systemd сервіс..."
sudo cp deploy/systemd/telegram-bot.service /etc/systemd/system/
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot.service
sudo systemctl restart telegram-bot.service

echo "✅ Готово! Бот запущено як systemd сервіс."
