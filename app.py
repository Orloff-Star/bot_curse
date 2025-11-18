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

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Получаем настройки из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# Получаем Render URL или используем локальный для тестирования
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "https://your-service-name.onrender.com")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"


async def on_startup(bot: Bot, base_url: str):
    """Действия при запуске бота"""
    try:
        # Устанавливаем вебхук
        await bot.set_webhook(
            url=base_url,
            drop_pending_updates=True
        )
        logger.info(f"Вебхук установлен на {base_url}")
    except Exception as e:
        logger.error(f"Ошибка при установке вебхука: {e}")


async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    try:
        await bot.delete_webhook()
        logger.info("Вебхук удален")
    except Exception as e:
        logger.error(f"Ошибка при удалении вебхука: {e}")
    finally:
        await bot.session.close()


# Обработчики команд
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user = message.from_user
    logger.info(f"Новый пользователь: {user.id} - {user.first_name}")

    welcome_text = (
        "👋 Добро пожаловать в IT Courses Bot!\n\n"
        "Я буду присылать вам актуальные рассылки о лучших онлайн-курсах "
        "по программированию и искусственному интеллекту.\n\n"
        "Оставайтесь на связи! 🚀"
    )
    await message.answer(welcome_text)


async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "ℹ️ Справка по боту:\n\n"
        "Это бот для рассылки IT-курсов. "
        "Вы будете получать уведомления о новых курсах автоматически.\n\n"
        "Доступные команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку"
    )
    await message.answer(help_text)


async def health_check(request):
    """Эндпоинт для проверки здоровья приложения (для Render)"""
    return web.Response(text="Bot is alive!")


def main():
    """Основная функция инициализации и запуска"""
    try:
        # Инициализируем бот
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

        # Инициализируем диспетчер
        dp = Dispatcher(storage=MemoryStorage())

        # Регистрируем обработчики
        dp.message.register(cmd_start, CommandStart())
        dp.message.register(cmd_help, Command("help"))

        # Создаем aiohttp приложение
        app = web.Application()

        # Добавляем health check эндпоинт
        app.router.add_get("/", health_check)
        app.router.add_get("/health", health_check)

        # Создаем и регистрируем обработчик вебхуков
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)

        # Настраиваем приложение aiogram
        setup_application(app, dp, bot=bot)

        # Регистрируем startup/shutdown
        app.on_startup.append(lambda app: on_startup(bot, WEBHOOK_URL))
        app.on_shutdown.append(lambda app: on_shutdown(bot))

        return app

    except Exception as e:
        logger.error(f"Ошибка при инициализации бота: {e}")
        raise


if __name__ == "__main__":
    # Получаем порт из переменной окружения Render
    port = int(os.environ.get("PORT", 10000))

    # Создаем и запускаем приложение
    app = main()

    logger.info(f"Запуск сервера на порту {port}")
    logger.info(f"Webhook URL: {WEBHOOK_URL}")

    try:
        web.run_app(
            app,
            host="0.0.0.0",
            port=port,
            access_log=None  # Отключаем access логи для чистоты вывода
        )
    except KeyboardInterrupt:
        logger.info("Сервер остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске сервера: {e}")