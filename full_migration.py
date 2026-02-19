"""
ПОЛНАЯ МИГРАЦИЯ БАЗЫ ДАННЫХ
Этот скрипт исправит ВСЕ проблемы с базой данных
"""

import sqlite3
import os
from datetime import datetime
import shutil

DB_PATH = 'task_tracker.db'

def backup_database():
    """Создание резервной копии"""
    if os.path.exists(DB_PATH):
        backup_name = f'task_tracker_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        shutil.copy2(DB_PATH, backup_name)
        print(f"✅ Резервная копия создана: {backup_name}")
        return backup_name
    return None

def check_column_exists(cursor, table_name, column_name):
    """Проверка существования колонки"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def recreate_database():
    """Пересоздание базы данных с нуля"""
    print("\n🔄 Пересоздание базы данных с правильной структурой...")
    
    # Удаляем старую базу
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("   ✓ Старая база удалена")
    
    # Создаем новую
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id_tg INTEGER UNIQUE,
            username TEXT,
            full_name TEXT,
            role TEXT CHECK(role IN ('admin', 'team'))
        )
    ''')
    print("   ✓ Таблица users создана")
    
    # Таблица задач
    cursor.execute('''
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_number TEXT UNIQUE,
            tm_id INTEGER,
            tm_username TEXT,
            task_text TEXT,
            priority TEXT CHECK(priority IN ('Высокий', 'Средний', 'Низкий')),
            deadline TEXT,
            comment TEXT,
            status TEXT CHECK(status IN ('Новая', 'В работе', 'Выполнено', 'Не выполнено', 'Просрочена')),
            created_at TEXT,
            updated_at TEXT,
            is_recurring INTEGER DEFAULT 0,
            recurring_period TEXT,
            message_id INTEGER,
            created_by INTEGER,
            FOREIGN KEY (tm_id) REFERENCES users(user_id_tg),
            FOREIGN KEY (created_by) REFERENCES users(user_id_tg)
        )
    ''')
    print("   ✓ Таблица tasks создана")
    
    # Таблица истории
    cursor.execute('''
        CREATE TABLE task_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            task_number TEXT,
            changed_by INTEGER,
            changed_by_username TEXT,
            action TEXT,
            comment TEXT,
            timestamp TEXT,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (changed_by) REFERENCES users(user_id_tg)
        )
    ''')
    print("   ✓ Таблица task_history создана")
    
    # Таблица подзадач
    cursor.execute('''
        CREATE TABLE subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            task_number TEXT,
            text TEXT,
            is_done INTEGER DEFAULT 0,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    ''')
    print("   ✓ Таблица subtasks создана")
    
    conn.commit()
    conn.close()
    
    print("\n✅ База данных успешно пересоздана с правильной структурой!")

def migrate_with_data_preservation():
    """Миграция с сохранением данных"""
    print("\n🔄 Миграция базы данных с сохранением данных...")
    
    backup_file = backup_database()
    if not backup_file:
        print("❌ Файл базы данных не найден. Будет создана новая база.")
        recreate_database()
        return
    
    # Открываем старую базу
    old_conn = sqlite3.connect(backup_file)
    old_conn.row_factory = sqlite3.Row
    old_cursor = old_conn.cursor()
    
    # Проверяем наличие данных
    try:
        old_cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = old_cursor.fetchone()['count']
        
        old_cursor.execute("SELECT COUNT(*) as count FROM tasks")
        task_count = old_cursor.fetchone()['count']
        
        print(f"   Найдено пользователей: {user_count}")
        print(f"   Найдено задач: {task_count}")
        
        if user_count == 0 and task_count == 0:
            print("\n   База пуста. Создаем чистую базу...")
            old_conn.close()
            recreate_database()
            return
        
    except Exception as e:
        print(f"   ⚠️ Ошибка чтения старой базы: {e}")
        old_conn.close()
        recreate_database()
        return
    
    # Создаем новую базу
    recreate_database()
    
    # Переносим данные
    new_conn = sqlite3.connect(DB_PATH)
    new_cursor = new_conn.cursor()
    
    print("\n📦 Перенос данных...")
    
    try:
        # Переносим пользователей
        old_cursor.execute("SELECT * FROM users")
        users = old_cursor.fetchall()
        
        for user in users:
            new_cursor.execute(
                'INSERT INTO users (user_id_tg, username, full_name, role) VALUES (?, ?, ?, ?)',
                (user['user_id_tg'], user['username'], user['full_name'], user['role'])
            )
        print(f"   ✓ Перенесено пользователей: {len(users)}")
        
        # Переносим задачи
        old_cursor.execute("SELECT * FROM tasks")
        tasks = old_cursor.fetchall()
        
        for task in tasks:
            # Получаем username исполнителя
            old_cursor.execute("SELECT username FROM users WHERE user_id_tg = ?", (task['tm_id'],))
            tm_user = old_cursor.fetchone()
            tm_username = tm_user['username'] if tm_user else ''
            
            new_cursor.execute('''
                INSERT INTO tasks (
                    task_number, tm_id, tm_username, task_text, priority, deadline,
                    comment, status, created_at, updated_at, is_recurring, 
                    recurring_period, message_id, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task['task_number'],
                task['tm_id'],
                tm_username,
                task['task_text'],
                task['priority'],
                task['deadline'],
                task.get('comment', ''),
                task['status'],
                task['created_at'],
                task['updated_at'],
                task.get('is_recurring', 0),
                task.get('recurring_period', None),
                task.get('message_id', None),
                task.get('created_by', task['tm_id'])  # Если нет created_by, ставим tm_id
            ))
        print(f"   ✓ Перенесено задач: {len(tasks)}")
        
        # Переносим историю если есть
        try:
            old_cursor.execute("SELECT * FROM task_history")
            history = old_cursor.fetchall()
            
            for entry in history:
                # Получаем task_number и username
                old_cursor.execute("SELECT task_number FROM tasks WHERE id = ?", (entry['task_id'],))
                task_row = old_cursor.fetchone()
                task_number = task_row['task_number'] if task_row else ''
                
                old_cursor.execute("SELECT username FROM users WHERE user_id_tg = ?", (entry['changed_by'],))
                user_row = old_cursor.fetchone()
                username = user_row['username'] if user_row else ''
                
                new_cursor.execute('''
                    INSERT INTO task_history (
                        task_id, task_number, changed_by, changed_by_username, 
                        action, comment, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry['task_id'],
                    task_number,
                    entry['changed_by'],
                    username,
                    entry['action'],
                    entry.get('comment', ''),
                    entry['timestamp']
                ))
            print(f"   ✓ Перенесено записей истории: {len(history)}")
        except Exception as e:
            print(f"   ⚠️ История не перенесена: {e}")
        
        # Переносим подзадачи если есть
        try:
            old_cursor.execute("SELECT * FROM subtasks")
            subtasks = old_cursor.fetchall()
            
            for subtask in subtasks:
                # Получаем task_number
                old_cursor.execute("SELECT task_number FROM tasks WHERE id = ?", (subtask['task_id'],))
                task_row = old_cursor.fetchone()
                task_number = task_row['task_number'] if task_row else ''
                
                new_cursor.execute('''
                    INSERT INTO subtasks (task_id, task_number, text, is_done)
                    VALUES (?, ?, ?, ?)
                ''', (
                    subtask['task_id'],
                    task_number,
                    subtask['text'],
                    subtask['is_done']
                ))
            print(f"   ✓ Перенесено подзадач: {len(subtasks)}")
        except Exception as e:
            print(f"   ⚠️ Подзадачи не перенесены: {e}")
        
        new_conn.commit()
        print("\n✅ Данные успешно перенесены!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при переносе данных: {e}")
        new_conn.rollback()
    finally:
        old_conn.close()
        new_conn.close()

def main():
    print("=" * 70)
    print(" ПОЛНАЯ МИГРАЦИЯ БАЗЫ ДАННЫХ")
    print("=" * 70)
    
    print("\nЭтот скрипт:")
    print("1. Создаст резервную копию текущей базы")
    print("2. Пересоздаст базу данных с правильной структурой")
    print("3. Перенесет все данные (пользователи, задачи, история)")
    
    if not os.path.exists(DB_PATH):
        print(f"\n❌ Файл {DB_PATH} не найден!")
        print("Запустите бота один раз, чтобы создать базу данных.")
        print("Затем запустите этот скрипт.")
        input("\nНажмите Enter для выхода...")
        return
    
    print("\n⚠️  ВАЖНО: Бот должен быть остановлен!")
    response = input("\nПродолжить? (yes/no): ")
    
    if response.lower() not in ['yes', 'y', 'да', 'д']:
        print("Отменено.")
        return
    
    migrate_with_data_preservation()
    
    print("\n" + "=" * 70)
    print(" МИГРАЦИЯ ЗАВЕРШЕНА!")
    print("=" * 70)
    print("\nТеперь вы можете запустить бота:")
    print("  python task_tracker_bot.py")
    print("\nИли дважды кликнуть на: start_bot.bat")
    print("\n" + "=" * 70)
    
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")
