"""
Скрипт очистки и исправления базы данных
Исправляет некорректные данные в базе
"""

import sqlite3
import os

DB_PATH = 'task_tracker.db'

def clean_database():
    """Очистка некорректных данных"""
    
    if not os.path.exists(DB_PATH):
        print("❌ Файл task_tracker.db не найден!")
        return
    
    print("=" * 60)
    print(" ОЧИСТКА БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n1. Проверка задач...")
    
    # Получаем все задачи
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    
    print(f"   Найдено задач: {len(tasks)}")
    
    fixed_count = 0
    
    for task in tasks:
        task_id = task['id']
        task_number = task['task_number']
        status = task['status']
        priority = task['priority']
        
        # Исправляем некорректный статус
        valid_statuses = ['Новая', 'В работе', 'Выполнено', 'Не выполнено', 'Просрочена']
        if status not in valid_statuses:
            print(f"   ⚠️  Задача {task_number}: некорректный статус '{status}' → 'Новая'")
            cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", ('Новая', task_id))
            fixed_count += 1
        
        # Исправляем некорректный приоритет
        valid_priorities = ['Высокий', 'Средний', 'Низкий']
        if priority not in valid_priorities:
            print(f"   ⚠️  Задача {task_number}: некорректный приоритет '{priority}' → 'Средний'")
            cursor.execute("UPDATE tasks SET priority = ? WHERE id = ?", ('Средний', task_id))
            fixed_count += 1
        
        # Проверяем наличие обязательных полей
        if not task.get('task_text'):
            print(f"   ⚠️  Задача {task_number}: нет описания → добавляем")
            cursor.execute("UPDATE tasks SET task_text = ? WHERE id = ?", ('Задача без описания', task_id))
            fixed_count += 1
        
        if not task.get('deadline'):
            cursor.execute("UPDATE tasks SET deadline = ? WHERE id = ?", ('-', task_id))
            fixed_count += 1
    
    print(f"\n2. Исправлено записей: {fixed_count}")
    
    # Удаляем задачи со статусами кроме Новая и В работе, если они старые
    print("\n3. Очистка завершенных задач...")
    cursor.execute("""
        SELECT COUNT(*) as count FROM tasks 
        WHERE status IN ('Выполнено', 'Не выполнено')
        AND datetime(created_at) < datetime('now', '-30 days')
    """)
    old_completed = cursor.fetchone()['count']
    
    if old_completed > 0:
        response = input(f"\n   Найдено {old_completed} завершенных задач старше 30 дней.\n   Удалить их? (yes/no): ")
        if response.lower() in ['yes', 'y', 'да', 'д']:
            cursor.execute("""
                DELETE FROM tasks 
                WHERE status IN ('Выполнено', 'Не выполнено')
                AND datetime(created_at) < datetime('now', '-30 days')
            """)
            print(f"   ✓ Удалено задач: {old_completed}")
    
    # Сохраняем изменения
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print(" ОЧИСТКА ЗАВЕРШЕНА")
    print("=" * 60)
    print("\nТеперь запустите бота:")
    print("  python task_tracker_bot.py")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        clean_database()
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nНажмите Enter для выхода...")
