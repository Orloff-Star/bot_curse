import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH
from database.db import create_table
from handlers.user_handlers import user_router
from scheduler.tasks import send_scheduled_welcome
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    try:
        # Устанавливаем вебхук
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )
        logger.info(f"Вебхук установлен на {WEBHOOK_URL}")

        # Запускаем планировщик
        scheduler = AsyncIOScheduler()
        # Проверяем каждую минуту наличие сообщений для отправки
        scheduler.add_job(
            send_scheduled_welcome,
            'interval',
            minutes=1,
            args=[bot],
            id='welcome_messages'
        )
        scheduler.start()
        logger.info("Планировщик запущен")

    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")


async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    try:
        await bot.delete_webhook()
        logger.info("Вебхук удален")
    except Exception as e:
        logger.error(f"Ошибка при остановке: {e}")
    finally:
        await bot.session.close()


async def health_check(request):
    """Эндпоинт для проверки здоровья приложения"""
    return web.Response(text="Bot is alive and running!")


def main():
    """Основная функция инициализации"""
    # Инициализируем бот
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Инициализируем диспетчер
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем роутеры
    dp.include_router(user_router)

    # Создаем aiohttp приложение
    app = web.Application()

    # Добавляем health check эндпоинты
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    # Создаем обработчик вебхуков
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Настраиваем приложение aiogram
    setup_application(app, dp, bot=bot)

    # Регистрируем startup/shutdown
    app.on_startup.append(lambda app: on_startup(bot))
    app.on_shutdown.append(lambda app: on_shutdown(bot))

    return app


if __name__ == "__main__":
    # Создаем таблицы БД при запуске
    asyncio.run(create_table())

    # Запускаем приложение
    port = int(os.environ.get("PORT", 10000))
    app = main()

    logger.info(f"Запуск сервера на порту {port}")
    web.run_app(app, host="0.0.0.0", port=port, access_log=None)