import aiosqlite
import datetime
from typing import List, Tuple

# Схема сообщений для новых подписчиков
WELCOME_MESSAGES = [
    {
        "delay_minutes": 0,  # Сразу после /start
        "text": "👋 Добро пожаловать в IT Courses Bot!\n\nЯ буду присылать вам лучшие курсы по программированию и ИИ. Оставайтесь на связи! 🚀",
        "image": None
    },
    {
        "delay_minutes": 1,  # Через 1 минуту (для теста)
        "text": "📚 Первое рекомендация!\n\nКурс 'Python для начинающих' - идеальный старт в программировании.\nОсвойте основы за 2 недели!",
        "image": "https://example.com/python-course.jpg",
        "button_text": "Посмотреть курс",
        "button_url": "https://example.com/python-course"
    },
    {
        "delay_minutes": 10,  # Через 10 минут
        "text": "🤖 Второе рекомендация!\n\nКурс 'Машинное обучение на Python' - станьте специалистом в ИИ!\nПрактические проекты и поддержка ментора.",
        "image": "https://example.com/ml-course.jpg",
        "button_text": "Узнать подробнее",
        "button_url": "https://example.com/ml-course"
    },
    {
        "delay_minutes": 60,  # Через 1 час
        "text": "🚀 Специальное предложение!\n\nПолучите скидку 20% на все наши курсы по промокоду WELCOME20!\nНе упустите шанс начать карьеру в IT!",
        "image": "https://example.com/special-offer.jpg",
        "button_text": "Получить скидку",
        "button_url": "https://example.com/special-offer"
    }
]


async def create_table():
    """Создание таблиц базы данных"""
    async with aiosqlite.connect('subscribers.db') as db:
        # Таблица подписчиков
        await db.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                welcome_stage INTEGER DEFAULT 0
            )
        ''')

        # Таблица для отслеживания отправленных сообщений
        await db.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_stage INTEGER,
                scheduled_for TIMESTAMP,
                sent BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES subscribers (user_id)
            )
        ''')

        await db.commit()


async def add_subscriber(user_id: int, username: str, first_name: str):
    """Добавление нового подписчика"""
    async with aiosqlite.connect('subscribers.db') as db:
        await db.execute(
            """INSERT OR REPLACE INTO subscribers 
               (user_id, username, first_name, subscribed_at, welcome_stage) 
               VALUES (?, ?, ?, datetime('now'), 0)""",
            (user_id, username, first_name)
        )
        await db.commit()


async def get_all_subscribers():
    """Получение всех подписчиков"""
    async with aiosqlite.connect('subscribers.db') as db:
        cursor = await db.execute("SELECT user_id FROM subscribers")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


async def get_subscribers_for_welcome():
    """Получение подписчиков, которым нужно отправить приветственные сообщения"""
    async with aiosqlite.connect('subscribers.db') as db:
        cursor = await db.execute('''
            SELECT s.user_id, s.welcome_stage, s.subscribed_at
            FROM subscribers s
            WHERE s.welcome_stage < ?
        ''', (len(WELCOME_MESSAGES),))
        rows = await cursor.fetchall()
        return rows


async def update_welcome_stage(user_id: int, new_stage: int):
    """Обновление стадии приветственных сообщений"""
    async with aiosqlite.connect('subscribers.db') as db:
        await db.execute(
            "UPDATE subscribers SET welcome_stage = ? WHERE user_id = ?",
            (new_stage, user_id)
        )
        await db.commit()


async def add_scheduled_message(user_id: int, message_stage: int, delay_minutes: int):
    """Добавление запланированного сообщения"""
    async with aiosqlite.connect('subscribers.db') as db:
        scheduled_for = f"datetime('now', '+{delay_minutes} minutes')"
        await db.execute(
            f"""INSERT INTO scheduled_messages 
                (user_id, message_stage, scheduled_for) 
                VALUES (?, ?, {scheduled_for})""",
            (user_id, message_stage)
        )
        await db.commit()


async def get_pending_messages():
    """Получение сообщений, готовых к отправке"""
    async with aiosqlite.connect('subscribers.db') as db:
        cursor = await db.execute('''
            SELECT sm.id, sm.user_id, sm.message_stage, s.username
            FROM scheduled_messages sm
            JOIN subscribers s ON sm.user_id = s.user_id
            WHERE sm.sent = FALSE AND sm.scheduled_for <= datetime('now')
        ''')
        rows = await cursor.fetchall()
        return rows


async def mark_message_sent(message_id: int):
    """Отметка сообщения как отправленного"""
    async with aiosqlite.connect('subscribers.db') as db:
        await db.execute(
            "UPDATE scheduled_messages SET sent = TRUE WHERE id = ?",
            (message_id,)
        )
        await db.commit()