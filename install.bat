@echo off
chcp 65001 >nul
cls
echo ============================================
echo TELEGRAM TASK TRACKER BOT v2.0 - INSTALL
echo ============================================
echo.

echo [1/4] Checking Python...
python --version 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo [OK] Python found
echo.

echo [2/4] Upgrading pip...
python -m pip install --upgrade pip
echo.

echo [3/4] Installing dependencies...
python -m pip install aiogram==3.4.1
python -m pip install aiohttp==3.9.3
python -m pip install openpyxl==3.1.2
python -m pip install python-dateutil==2.8.2
echo.

echo [4/4] Checking installation...
python -c "import aiogram; print('[OK] aiogram installed')" 2>nul
python -c "import openpyxl; print('[OK] openpyxl installed')" 2>nul
python -c "import dateutil; print('[OK] python-dateutil installed')" 2>nul
echo.

echo ============================================
echo INSTALLATION COMPLETED!
echo ============================================
echo.
echo Next steps:
echo 1. Open task_tracker_bot.py
echo 2. Set your BOT_TOKEN
echo 3. Set your ADMIN_USERNAME
echo 4. Run: python task_tracker_bot.py
echo.
echo ============================================
pause
