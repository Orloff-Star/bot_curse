from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
import logging
from database.db import add_subscriber, add_scheduled_message, WELCOME_MESSAGES
from aiogram.utils.keyboard import InlineKeyboardBuilder

user_router = Router()
logger = logging.getLogger(__name__)


@user_router.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    try:
        user = message.from_user

        # Добавляем пользователя в базу
        await add_subscriber(user.id, user.username, user.first_name)

        # Отправляем первое приветственное сообщение сразу
        first_message = WELCOME_MESSAGES[0]
        await message.answer(
            first_message["text"],
            parse_mode=ParseMode.HTML
        )

        # Планируем остальные сообщения
        for i, msg_data in enumerate(WELCOME_MESSAGES[1:], 1):
            await add_scheduled_message(user.id, i, msg_data["delay_minutes"])

        await message.answer("✅ Вы успешно подписались на рассылку! Ожидайте новые курсы в ближайшее время.")
        logger.info(f"Пользователь {user.id} успешно подписан")

    except Exception as e:
        logger.error(f"Ошибка при обработке /start для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка при подписке. Попробуйте позже.")


@user_router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "ℹ️ <b>Справка по боту</b>\n\n"
        "Это бот для рассылки IT-курсов. После подписки вы будете автоматически получать:\n"
        "• Приветственное сообщение\n"
        "• Рекомендации курсов через определенные интервалы\n"
        "• Специальные предложения\n\n"
        "<b>Команды:</b>\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку"
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML)