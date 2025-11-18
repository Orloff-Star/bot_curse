import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ваш токен от BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# Базовый URL вашего Web Service на Render
# ЗАМЕНИТЕ "your-service-name" на реальное имя вашего сервиса в Render
BASE_WEBHOOK_URL = "https://bot-curse.onrender.com"
WEBHOOK_PATH = "/webhook"


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    # Устанавливаем вебхук
    webhook_url = f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}"
    await bot.set_webhook(webhook_url)
    logger.info(f"Вебхук установлен на {webhook_url}")


async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    # Удаляем вебхук при завершении работы
    await bot.delete_webhook()
    logger.info("Бот остановлен")


# Обработчики команд
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer("Привет! Я бот для рассылки IT курсов! 🚀")


async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    await message.answer("Это бот для получения рассылки IT курсов. Просто подпишись и жди обновлений!")


def create_app():
    """Функция создания и настройки приложения aiohttp"""

    # Инициализируем бот с настройками по умолчанию
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Инициализируем диспетчер
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрируем обработчики КОРРЕКТНЫМ способом для aiogram 3.x
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command(commands=["help"]))

    # Регистрируем запуск и остановку
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Создаем aiohttp приложение
    app = web.Application()

    # Создаем обработчик для пути /webhook
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )

    # Регистрируем обработчик
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Настраиваем приложение aiogram
    setup_application(app, dp, bot=bot)

    return app


if __name__ == "__main__":
    # Получаем порт из переменной окружения Render или используем по умолчанию 10000
    port = int(os.environ.get("PORT", 10000))

    # Запускаем веб-сервер
    logger.info(f"Запуск сервера на порту {port}")
    web.run_app(create_app(), host="0.0.0.0", port=port, access_log=None)