import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ваш токен от BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")
# Базовый URL вашего Web Service на Render
BASE_WEBHOOK_URL = "https://your-service-name.onrender.com"  # ЗАМЕНИТЕ на ваш реальный URL


async def on_startup(bot: Bot, dispatcher: Dispatcher):
    """Действия при запуске бота"""
    # Устанавливаем вебхук
    webhook_url = f"{BASE_WEBHOOK_URL}/webhook"
    await bot.set_webhook(webhook_url)
    logger.info(f"Вебхук установлен на {webhook_url}")


async def on_shutdown(bot: Bot, dispatcher: Dispatcher):
    """Действия при остановке бота"""
    # Удаляем вебхук при завершении работы
    await bot.delete_webhook()
    logger.info("Бот остановлен")


def create_app():
    """Функция создания и настройки приложения aiohttp"""
    # Инициализируем бот и диспетчер
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Здесь регистрируем ваши обработчики сообщений
    # Например, обработчик команды /start
    @dp.message(commands=["start"])
    async def cmd_start(message: types.Message):
        await message.answer("Привет! Я бот с вебхуком!")

    # Связываем диспетчер с запуском и остановкой
    dp.startup.register(lambda: on_startup(bot, dp))
    dp.shutdown.register(lambda: on_shutdown(bot, dp))

    # Создаем aiohttp приложение
    app = web.Application()

    # Создаем обработчик для пути /webhook, куда Telegram будет отправлять сообщения
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )

    # Регистрируем обработчик
    webhook_requests_handler.register(app, path="/webhook")

    # Настраиваем приложение aiogram
    setup_application(app, dp, bot=bot)

    return app


if __name__ == "__main__":
    # Получаем порт из переменной окружения Render или используем по умолчанию 10000
    port = int(os.environ.get("PORT", 10000))
    # Запускаем веб-сервер на правильном IP-адресе и порту
    web.run_app(create_app(), host="0.0.0.0", port=port)