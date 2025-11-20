import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, BOTHOST_URL, SELF_PING_ENABLED, SELF_PING_INTERVAL
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


async def self_ping():
    """Функция для само-пинга сервиса (если нужно)"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BOTHOST_URL}/health", timeout=10) as resp:
                logger.info(f"Self-ping выполнен, статус: {resp.status}")
    except Exception as e:
        logger.error(f"Ошибка при само-пинге: {e}")


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    try:
        # Инициализируем базу данных
        await create_table()
        logger.info("База данных инициализирована")

        # Устанавливаем вебхук
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )
        logger.info(f"✅ Вебхук установлен на {WEBHOOK_URL}")

        # Запускаем планировщик
        scheduler = AsyncIOScheduler()

        # Задача для приветственных сообщений (каждую минуту)
        scheduler.add_job(
            send_scheduled_welcome,
            'interval',
            minutes=1,
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

        # Задача для само-пинга (если включено)
        if SELF_PING_ENABLED:
            scheduler.add_job(
                self_ping,
                'interval',
                minutes=SELF_PING_INTERVAL,
                id='self_ping'
            )
            logger.info(f"Само-пинг включен с интервалом {SELF_PING_INTERVAL} минут")

        scheduler.start()
        logger.info("Планировщик запущен")

    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")
        raise


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


async def bot_info(request):
    """Информация о боте"""
    info_text = f"""
Bot Information:
- Status: ✅ Running
- Webhook: {WEBHOOK_URL}
- Platform: bothost.ru
- Health: OK
"""
    return web.Response(text=info_text)


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
    app.router.add_get("/info", bot_info)

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
    # Запускаем приложение
    # Bothost обычно использует порт 3000 (как видно из логов)
    port = int(os.environ.get("PORT", 3000))
    app = main()

    logger.info(f"🚀 Запуск бота на bothost.ru, порт: {port}")
    logger.info(f"🌐 Webhook URL: {WEBHOOK_URL}")
    web.run_app(app, host="0.0.0.0", port=port, access_log=None)