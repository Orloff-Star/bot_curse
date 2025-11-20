import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен")

# Используем ID приложения Bothost.ru
BOTHOST_APP_ID = os.getenv("BOTHOST_APP_ID", "bot_1763602889_6267_eaglestar")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{BOTHOST_APP_ID}.bothost.ru{WEBHOOK_PATH}"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Импортируем роутеры
from handlers.user_handlers import user_router


# Обработчики команд
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    try:
        user = message.from_user
        logger.info(f"🎯 /start от {user.id} ({user.first_name})")

        from database.db import add_subscriber, add_scheduled_message, WELCOME_MESSAGES

        # Добавляем пользователя в базу
        await add_subscriber(user.id, user.username or "No username", user.first_name or "No name")
        logger.info(f"✅ Пользователь {user.id} добавлен в БД")

        # Отправляем первое сообщение сразу
        first_message = WELCOME_MESSAGES[0]
        await message.answer(first_message["text"])

        # Планируем остальные сообщения
        for i, msg_data in enumerate(WELCOME_MESSAGES[1:], 1):
            await add_scheduled_message(user.id, i, msg_data["delay_minutes"])

        await message.answer("✅ Вы подписались! Ожидайте новые курсы 📚")

    except Exception as e:
        logger.error(f"❌ Ошибка в /start: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "🤖 <b>IT Courses Bot - Помощь</b>\n\n"
        "Я присылаю лучшие курсы по программированию и ИИ.\n\n"
        "<b>Команды:</b>\n"
        "/start - подписаться на рассылку\n"
        "/help - эта справка\n\n"
        "После подписки вы получите серию сообщений с курсами!"
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML)


@dp.message()
async def handle_other_messages(message: types.Message):
    """Обработчик всех остальных сообщений"""
    await message.answer("Используйте /start для подписки или /help для справки")


async def on_startup(app):
    """Действия при запуске приложения"""
    try:
        # Инициализируем базу данных
        from database.db import create_table
        await create_table()
        logger.info("✅ База данных инициализирована")

        # Устанавливаем вебхук для Bothost.ru
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )
        logger.info(f"✅ Вебхук установлен для Bothost.ru: {WEBHOOK_URL}")

        # Запускаем планировщик
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from scheduler.tasks import send_scheduled_welcome
        from database.db import cleanup_old_messages

        scheduler = AsyncIOScheduler()

        # Задача для приветственных сообщений (каждые 2 минуты)
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
    """Обработчик вебхука"""
    logger.info("📨 Получен вебхук запрос")
    try:
        handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        return await handler.handle(request)
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

    logger.info(f"🚀 Запуск бота на Bothost.ru")
    logger.info(f"📍 ID приложения: {BOTHOST_APP_ID}")
    logger.info(f"📍 Порт: {port}")
    logger.info(f"🔗 Webhook URL: {WEBHOOK_URL}")

    web.run_app(
        app,
        host='0.0.0.0',
        port=port,
        access_log=None
    )