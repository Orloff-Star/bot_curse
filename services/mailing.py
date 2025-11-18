from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.db import get_all_subscribers

async def broadcast_message(bot: Bot, image_url: str, text: str, button_url: str, button_text: str = "Узнать подробнее"):
    """Функция для массовой рассылки сообщения всем подписчикам."""
    subscribers = await get_all_subscribers()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=button_text, url=button_url)]]
    )

    for user_id in subscribers:
        try:
            if image_url:
                await bot.send_photo(chat_id=user_id, photo=image_url, caption=text, reply_markup=keyboard)
            else:
                await bot.send_message(chat_id=user_id, text=text, reply_markup=keyboard)
        except Exception as e:
            print(f"Не удалось отправить сообщение {user_id}: {e}")