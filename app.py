import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, BOTHOST_DOMAIN
from database.db import create_table, cleanup_old_messages
from handlers.user_handlers import user_router
from scheduler.tasks import send_scheduled_welcome
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Глобальные переменные
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def on_startup(app):
    """Действия при запуске приложения"""
    try:
        # Инициализируем базу данных
        await create_table()
        logger.info("✅ База данных инициализирована")

        # Устанавливаем вебхук
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )
        logger.info(f"✅ Вебхук установлен: {WEBHOOK_URL}")

        # Запускаем планировщик
        scheduler = AsyncIOScheduler()

        # Задача для приветственных сообщений (каждые 2 минуты для стабильности)
        scheduler.add_job(
            send_scheduled_welcome,
            'interval',
            minutes=2,
            args=[bot],
            id='welcome_messages'
        )

        # Задача для очистки старых сообщений (раз в день)
        scheduler.add_job(
            cleanup_old_messages,
            'interval',
            hours=24,
            id='cleanup'
        )

        scheduler.start()
        logger.info("✅ Планировщик запущен")

    except Exception as e:
        logger.error(f"❌ Ошибка при запуске: {e}")
        raise


async def on_shutdown(app):
    """Действия при остановке приложения"""
    try:
        await bot.delete_webhook()
        logger.info("✅ Вебхук удален")
    except Exception as e:
        logger.error(f"❌ Ошибка при остановке: {e}")
    finally:
        await bot.session.close()


async def health_check(request):
    """Эндпоинт для проверки здоровья приложения"""
    return web.Response(text="Bot is alive and running!")


async def webhook_handler(request):
    """Обработчик вебхука с логированием"""
    logger.info("📨 Получен вебхук запрос")
    try:
        # Создаем обработчик
        handler = SimpleRequestHandler(dispatcher=dp, bot=bot)

        # Получаем данные запроса для логирования
        body = await request.text()
        logger.info(f"📝 Тело запроса: {body[:200]}...")

        # Обрабатываем запрос
        response = await handler.handle(request)
        logger.info("✅ Вебхук обработан успешно")
        return response

    except Exception as e:
        logger.error(f"❌ Ошибка обработки вебхука: {e}")
        return web.Response(status=500, text="Internal Server Error")


def main():
    """Основная функция инициализации"""
    # Регистрируем роутеры
    dp.include_router(user_router)

    # Создаем aiohttp приложение
    app = web.Application()

    # Добавляем health check эндпоинты
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)

    # Регистрируем вебхук
    app.router.add_post(WEBHOOK_PATH, webhook_handler)

    # Регистрируем startup/shutdown
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    return app


if __name__ == "__main__":
    # Запускаем приложение
    port = int(os.environ.get("PORT", 3000))
    app = main()

    logger.info(f"🚀 Запуск бота на bothost.ru")
    logger.info(f"📍 Порт: {port}")
    logger.info(f"🌐 Домен: {BOTHOST_DOMAIN}")
    logger.info(f"🔗 Webhook URL: {WEBHOOK_URL}")

    web.run_app(
        app,
        host='0.0.0.0',
        port=port,
        access_log=None
    )