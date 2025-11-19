import aiosqlite
import logging
from typing import List

logger = logging.getLogger(__name__)

# Схема сообщений для новых подписчиков
WELCOME_MESSAGES = [
    {
        "delay_minutes": 0,  # Сразу после /start
        "text": "👋 Добро пожаловать в IT Courses Bot!\n\nЯ буду присылать вам лучшие курсы по программированию и ИИ. Оставайтесь на связи! 🚀",
        "image": None
    },
    {
        "delay_minutes": 1,  # Через 1 минуту (для теста)
        "text": "📚 Первая рекомендация!\n\nКурс 'Python для начинающих' - идеальный старт в программировании.\nОсвойте основы за 2 недели!",
        "image": None,
        "button_text": "Посмотреть курс",
        "button_url": "https://example.com/python-course"
    },
    {
        "delay_minutes": 60 * 24,  # Через 1 день
        "text": "🤖 Вторая рекомендация!\n\nКурс 'Машинное обучение на Python' - станьте специалистом в ИИ!\nПрактические проекты и поддержка ментора.",
        "image": None,
        "button_text": "Узнать подробнее",
        "button_url": "https://example.com/ml-course"
    },
    {
        "delay_minutes": 60 * 24 * 3,  # Через 3 дня
        "text": "🚀 Специальное предложение!\n\nПолучите скидку 20% на все наши курсы по промокоду WELCOME20!\nНе упустите шанс начать карьеру в IT!",
        "image": None,
        "button_text": "Получить скидку",
        "button_url": "https://example.com/special-offer"
    }
]


async def create_table():
    """Создание таблиц базы данных с поддержкой миграций"""
    async with aiosqlite.connect('subscribers.db') as db:
        # Включаем поддержку внешних ключей
        await db.execute("PRAGMA foreign_keys = ON")

        # Создаем таблицу подписчиков
        await db.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                welcome_stage INTEGER DEFAULT 0
            )
        ''')

        # Создаем таблицу для отслеживания отправленных сообщений
        await db.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_stage INTEGER,
                scheduled_for TIMESTAMP,
                sent BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES subscribers (user_id) ON DELETE CASCADE
            )
        ''')

        # ✅ МИГРАЦИЯ: Добавляем столбец welcome_stage если его нет
        try:
            await db.execute("ALTER TABLE subscribers ADD COLUMN welcome_stage INTEGER DEFAULT 0")
            logger.info("Миграция: добавлен столбец welcome_stage")
        except aiosqlite.OperationalError:
            # Столбец уже существует - это нормально
            pass

        await db.commit()
        logger.info("База данных инициализирована")


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
    logger.info(f"Добавлен подписчик: {user_id}")


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
    logger.debug(f"Обновлена стадия welcome_stage для {user_id}: {new_stage}")


async def add_scheduled_message(user_id: int, message_stage: int, delay_minutes: int):
    """Добавление запланированного сообщения"""
    async with aiosqlite.connect('subscribers.db') as db:
        # Используем SQLite datetime функцию для вычисления времени
        scheduled_for = f"datetime('now', '+{delay_minutes} minutes')"
        await db.execute(
            f"""INSERT INTO scheduled_messages 
                (user_id, message_stage, scheduled_for) 
                VALUES (?, ?, {scheduled_for})""",
            (user_id, message_stage)
        )
        await db.commit()
    logger.debug(f"Добавлено запланированное сообщение для {user_id}, стадия {message_stage}")


async def get_pending_messages():
    """Получение сообщений, готовых к отправке"""
    async with aiosqlite.connect('subscribers.db') as db:
        cursor = await db.execute('''
            SELECT sm.id, sm.user_id, sm.message_stage, s.username
            FROM scheduled_messages sm
            JOIN subscribers s ON sm.user_id = s.user_id
            WHERE sm.sent = FALSE AND sm.scheduled_for <= datetime('now')
            ORDER BY sm.scheduled_for ASC
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
    logger.debug(f"Отмечено сообщение {message_id} как отправленное")


async def cleanup_old_messages():
    """Очистка старых отправленных сообщений (чтобы база не росла бесконечно)"""
    async with aiosqlite.connect('subscribers.db') as db:
        await db.execute(
            "DELETE FROM scheduled_messages WHERE sent = TRUE AND created_at < datetime('now', '-7 days')"
        )
        await db.commit()
    logger.info("Очищены старые отправленные сообщения")