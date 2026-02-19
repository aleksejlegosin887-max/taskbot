@echo off
chcp 65001 >nul
cls
echo ============================================
echo DATABASE MIGRATION
echo ============================================
echo.
echo This script will update your database structure.
echo.
echo IMPORTANT: Close the bot before running migration!
echo.
pause

python full_migration.py

pause
