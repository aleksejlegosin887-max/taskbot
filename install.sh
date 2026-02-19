#!/bin/bash

echo "============================================"
echo " УСТАНОВКА TELEGRAM TASK TRACKER BOT v2.0"
echo "============================================"
echo ""

# Проверка Python
echo "Проверка Python..."
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 не найден!"
    echo "Установите Python 3.8+ с https://www.python.org/downloads/"
    exit 1
fi

python3 --version
echo "✅ Python найден"
echo ""

# Проверка pip
echo "Проверка pip..."
if ! command -v pip3 &> /dev/null
then
    echo "❌ pip не найден!"
    echo "Установите pip"
    exit 1
fi

echo "✅ pip найден"
echo ""

# Обновление pip
echo "Обновление pip..."
python3 -m pip install --upgrade pip
echo ""

# Установка зависимостей
echo "Установка зависимостей..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================"
    echo " УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!"
    echo "============================================"
    echo ""
    echo "Следующие шаги:"
    echo "1. Откройте task_tracker_bot.py"
    echo "2. Укажите ваш BOT_TOKEN"
    echo "3. Укажите ваш ADMIN_USERNAME"
    echo "4. Запустите: python3 task_tracker_bot.py"
    echo ""
    echo "============================================"
else
    echo ""
    echo "❌ ОШИБКА УСТАНОВКИ!"
    echo "Проверьте сообщения об ошибках выше"
    exit 1
fi
