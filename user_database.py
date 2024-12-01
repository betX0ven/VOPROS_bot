import sqlite3

# Инициализация базы данных и создание таблицы, если её ещё нет
def init_db():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            chat_id INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Функция для добавления или обновления данных пользователя в базе данных
def save_user(username: str, chat_id: int):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, chat_id) VALUES (?, ?)
        ON CONFLICT(username) DO UPDATE SET chat_id=excluded.chat_id
    ''', (username, chat_id))
    conn.commit()
    conn.close()

# Функция для поиска chat_id по username
def find_chat_id_by_username(username: str):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT chat_id FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
