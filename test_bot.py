"""
Скрипт тестирования Task Tracker Bot
Проверяет основные функции бота
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'task_tracker.db'

def test_database():
    """Тест подключения к базе данных"""
    print("=" * 60)
    print(" ТЕСТ 1: Подключение к базе данных")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print("❌ База данных не найдена!")
        print("Запустите бота один раз для создания базы")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Проверка таблиц
        tables = ['users', 'tasks', 'task_history', 'subtasks']
        for table in tables:
            cursor.execute(f"SELECT count(*) as count FROM sqlite_master WHERE type='table' AND name='{table}'")
            result = cursor.fetchone()
            if result['count'] == 1:
                print(f"✅ Таблица {table} существует")
            else:
                print(f"❌ Таблица {table} не найдена!")
                return False
        
        conn.close()
        print("\n✅ База данных в порядке!")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_database_structure():
    """Тест структуры базы данных"""
    print("\n" + "=" * 60)
    print(" ТЕСТ 2: Структура базы данных")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Проверка полей в tasks
        required_fields = {
            'tasks': ['task_number', 'tm_id', 'tm_username', 'task_text', 'priority', 
                     'deadline', 'status', 'created_by'],
            'task_history': ['task_number', 'changed_by_username'],
            'subtasks': ['task_number']
        }
        
        all_ok = True
        for table, fields in required_fields.items():
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row['name'] for row in cursor.fetchall()]
            
            for field in fields:
                if field in columns:
                    print(f"✅ {table}.{field} - OK")
                else:
                    print(f"❌ {table}.{field} - НЕ НАЙДЕНО!")
                    all_ok = False
        
        conn.close()
        
        if all_ok:
            print("\n✅ Структура базы данных правильная!")
        else:
            print("\n❌ Необходима миграция базы данных!")
            print("Запустите: python full_migration.py")
        
        return all_ok
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_users():
    """Тест пользователей"""
    print("\n" + "=" * 60)
    print(" ТЕСТ 3: Пользователи")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Подсчет пользователей
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        print(f"Всего пользователей: {user_count}")
        
        # Проверка администратора
        cursor.execute("SELECT * FROM users WHERE role = 'admin'")
        admins = cursor.fetchall()
        
        if admins:
            for admin in admins:
                print(f"✅ Администратор: {admin['username']} (ID: {admin['user_id_tg']})")
        else:
            print("⚠️  Администратор не найден!")
            print("Отправьте боту /start от имени администратора")
        
        # Проверка членов команды
        cursor.execute("SELECT * FROM users WHERE role = 'team'")
        team_members = cursor.fetchall()
        
        if team_members:
            print(f"\nЧленов команды: {len(team_members)}")
            for member in team_members:
                print(f"  - {member['username']} (ID: {member['user_id_tg']})")
        else:
            print("\nℹ️  Члены команды не добавлены")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_tasks():
    """Тест задач"""
    print("\n" + "=" * 60)
    print(" ТЕСТ 4: Задачи")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Подсчет задач
        cursor.execute("SELECT COUNT(*) as count FROM tasks")
        task_count = cursor.fetchone()['count']
        print(f"Всего задач: {task_count}")
        
        if task_count > 0:
            # Статистика по статусам
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM tasks 
                GROUP BY status
            """)
            
            print("\nРаспределение по статусам:")
            for row in cursor.fetchall():
                print(f"  {row['status']}: {row['count']}")
            
            # Проверка корректности данных
            cursor.execute("SELECT * FROM tasks LIMIT 1")
            sample_task = cursor.fetchone()
            
            print("\nПример задачи:")
            print(f"  Номер: {sample_task['task_number']}")
            print(f"  Статус: {sample_task['status']}")
            print(f"  Приоритет: {sample_task['priority']}")
            print(f"  Исполнитель (username): {sample_task.get('tm_username', 'НЕТ ДАННЫХ')}")
            
            if not sample_task.get('tm_username'):
                print("\n⚠️  Поле tm_username пустое! Необходима миграция.")
        else:
            print("ℹ️  Задач пока нет")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_config():
    """Тест конфигурации"""
    print("\n" + "=" * 60)
    print(" ТЕСТ 5: Конфигурация")
    print("=" * 60)
    
    try:
        with open('task_tracker_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Проверка токена
            if 'BOT_TOKEN = "8360197362:' in content:
                print("⚠️  ВНИМАНИЕ: Используется токен из примера!")
                print("   Обязательно замените на свой токен")
            else:
                print("✅ BOT_TOKEN настроен")
            
            # Проверка админа
            if 'ADMIN_USERNAME = "chasujebezoshibochno"' in content:
                print("✅ ADMIN_USERNAME настроен")
            else:
                print("⚠️  ADMIN_USERNAME изменен")
            
            # Проверка времени отчета
            if 'DAILY_REPORT_TIME = "21:00"' in content:
                print("✅ DAILY_REPORT_TIME настроен (21:00)")
            else:
                print("ℹ️  DAILY_REPORT_TIME изменен")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_log_file():
    """Тест лог-файла"""
    print("\n" + "=" * 60)
    print(" ТЕСТ 6: Логирование")
    print("=" * 60)
    
    if os.path.exists('bot.log'):
        size = os.path.getsize('bot.log')
        print(f"✅ Файл bot.log существует ({size} байт)")
        
        # Читаем последние строки
        try:
            with open('bot.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print(f"\nПоследние записи:")
                    for line in lines[-5:]:
                        print(f"  {line.strip()}")
                else:
                    print("ℹ️  Лог-файл пуст")
        except Exception as e:
            print(f"⚠️  Ошибка чтения: {e}")
    else:
        print("ℹ️  Файл bot.log не создан (бот еще не запускался)")
    
    return True

def main():
    """Главная функция"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "ТЕСТИРОВАНИЕ TASK TRACKER BOT v2.0" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    tests = [
        test_database,
        test_database_structure,
        test_users,
        test_tasks,
        test_config,
        test_log_file
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Критическая ошибка в тесте: {e}")
            results.append(False)
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print(" ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nПройдено тестов: {passed}/{total}")
    
    if all(results):
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("\nБот готов к работе!")
        print("Запустите: python task_tracker_bot.py")
    else:
        print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("\nРекомендации:")
        if not results[0] or not results[1]:
            print("  1. Запустите миграцию: python full_migration.py")
        if not results[2]:
            print("  2. Запустите бота и отправьте /start")
        print("  3. Проверьте настройки в task_tracker_bot.py")
    
    print("\n" + "=" * 60)
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")
