from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Bot
from datetime import timedelta

scheduler = AsyncIOScheduler()

async def send_scheduled_welcome(bot: Bot, user_id: int):
    """Функция для отправки запланированных сообщений новому пользователю."""
    messages = [
        {"text": "📚 Первое сообщение. Наш топовый курс по Python...", "delay": 1},  # Через 1 минуту
        {"text": "🤖 Второе сообщение. Погрузись в мир ИИ с нашим курсом...", "delay": 60*24},  # Через 1 день
        {"text": "🚀 Третье сообщение. Не упусти шанс стать востребованным специалистом!", "delay": 60*24*3},  # Через 3 дня
    ]

    for msg in messages:
        scheduler.add_job(
            bot.send_message,
            trigger="date",
            run_date=datetime.now() + timedelta(minutes=msg["delay"]),
            kwargs={"chat_id": user_id, "text": msg["text"]}
        )

def setup_scheduler():
    """Запускает планировщик."""
    scheduler.start()