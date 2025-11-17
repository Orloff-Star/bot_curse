from aiogram import Router, types
from aiogram.filters import Command
from database.db import add_subscriber

user_router = Router()

# Обработчик команды /start
@user_router.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    await add_subscriber(user.id, user.username, user.first_name)

    welcome_text = (
        "Добро пожаловать в IT Courses Bot! 🚀\n\n"
        "Здесь ты будешь получать актуальные рассылки о лучших онлайн-курсах "
        "по программированию и искусственному интеллекту. Приятного обучения!"
    )
    await message.answer(welcome_text)