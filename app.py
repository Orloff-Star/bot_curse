import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.db import create_table
from handlers.user_handlers import user_router
from scheduler.tasks import setup_scheduler

async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Создаем таблицу в БД при запуске
    await create_table()

    # Регистрируем роутеры (обработчики)
    dp.include_router(user_router)

    # Запускаем планировщик
    setup_scheduler()

    # Запускаем опрос серверов Telegram
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())