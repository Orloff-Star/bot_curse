from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
import logging
from database.db import add_subscriber, add_scheduled_message, WELCOME_MESSAGES

user_router = Router()
logger = logging.getLogger(__name__)


@user_router.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    try:
        user = message.from_user
        logger.info(f"🎯 Получен /start от {user.id} ({user.first_name})")

        # Добавляем пользователя в базу
        await add_subscriber(user.id, user.username or "No username", user.first_name or "No name")
        logger.info(f"✅ Пользователь {user.id} добавлен в БД")

        # Отправляем первое приветственное сообщение сразу
        first_message = WELCOME_MESSAGES[0]
        await message.answer(first_message["text"])
        logger.info(f"📨 Отправлено приветствие пользователю {user.id}")

        # Планируем остальные сообщения
        scheduled_count = 0
        for i, msg_data in enumerate(WELCOME_MESSAGES[1:], 1):
            await add_scheduled_message(user.id, i, msg_data["delay_minutes"])
            scheduled_count += 1

        logger.info(f"⏰ Запланировано {scheduled_count} сообщений для {user.id}")

        await message.answer("✅ Вы успешно подписались! Ожидайте новые курсы 📚")

    except Exception as e:
        logger.error(f"❌ Ошибка в /start: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


@user_router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    logger.info(f"❓ Получен /help от {message.from_user.id}")

    help_text = (
        "🤖 <b>IT Courses Bot - Помощь</b>\n\n"
        "Я присылаю лучшие курсы по программированию и ИИ.\n\n"
        "<b>Команды:</b>\n"
        "/start - подписаться на рассылку\n"
        "/help - эта справка\n\n"
        "После подписки вы получите серию сообщений с курсами!"
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML)


@user_router.message()
async def handle_other_messages(message: types.Message):
    """Обработчик всех остальных сообщений"""
    logger.info(f"💬 Прочее сообщение от {message.from_user.id}: {message.text}")
    await message.answer("Используйте /start для подписки или /help для справки")