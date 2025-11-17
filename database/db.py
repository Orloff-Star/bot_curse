import aiosqlite
import asyncio

# Создание таблицы при первом запуске
async def create_table():
    async with aiosqlite.connect('subscribers.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

# Добавление нового подписчика
async def add_subscriber(user_id: int, username: str, first_name: str):
    async with aiosqlite.connect('subscribers.db') as db:
        await db.execute(
            "INSERT OR REPLACE INTO subscribers (user_id, username, first_name) VALUES (?, ?, ?)",
            (user_id, username, first_name)
        )
        await db.commit()

# Получение списка всех подписчиков
async def get_all_subscribers():
    async with aiosqlite.connect('subscribers.db') as db:
        cursor = await db.execute("SELECT user_id FROM subscribers")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]