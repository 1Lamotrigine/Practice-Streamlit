import sqlite3

DB_NAME = "tasks.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.text_factory = lambda x: str(x, 'utf-8', 'ignore') if isinstance(x, bytes) else str(x)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time_slot TEXT NOT NULL,
            category TEXT NOT NULL,
            task_text TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_schedule(schedule_list):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks")
    for task in schedule_list:
        cursor.execute(
            "INSERT INTO tasks (time_slot, category, task_text) VALUES (?, ?, ?)",
            (str(task['time_slot']), str(task['category']), str(task['task_text']))
        )
    conn.commit()
    conn.close()

def get_all_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT time_slot, category, task_text FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [{"time_slot": r[0], "category": r[1], "task_text": r[2]} for r in rows]

def get_stats():
    """Возвращает статистику для дашборда."""
    tasks = get_all_tasks()
    total = len(tasks)
    work_count = len([t for t in tasks if "Работа" in t['category']])
    health_count = len([t for t in tasks if "Здоровье" in t['category']])
    return total, work_count, health_count