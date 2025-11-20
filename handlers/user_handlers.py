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
        logger.info(f"Новый пользователь: {user.id} - {user.first_name}")

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

        success_text = (
            "✅ Вы успешно подписались на рассылку!\n\n"
            "В ближайшее время вы получите:\n"
            "• Рекомендации лучших IT-курсов\n"
            "• Специальные предложения\n"
            "• Советы по развитию в программировании\n\n"
            "Оставайтесь на связи! 🚀"
        )
        await message.answer(success_text)
        logger.info(f"Пользователь {user.id} успешно подписан")

    except Exception as e:
        logger.error(f"Ошибка при обработке /start: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


@user_router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "🤖 <b>IT Courses Bot - Помощь</b>\n\n"
        "Я автоматически присылаю подборки лучших курсов по:\n"
        "• Программированию\n"
        "• Искусственному интеллекту\n"
        "• Data Science\n"
        "• Веб-разработке\n\n"
        "<b>После подписки вы получите:</b>\n"
        "🎯 Приветственное сообщение\n"
        "📚 Подборки курсов через определенные интервалы\n"
        "🔥 Специальные предложения и скидки\n\n"
        "<b>Команды:</b>\n"
        "/start - начать работу и подписаться\n"
        "/help - показать эту справку\n\n"
        "Просто подпишитесь и получайте лучшие курсы!"
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML)


@user_router.message(F.text)
async def handle_other_messages(message: types.Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "Я понимаю только команды:\n"
        "/start - для подписки на рассылку\n"
        "/help - для справки\n\n"
        "Используйте эти команды для работы с ботом 😊"
    )