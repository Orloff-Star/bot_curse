import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import BOT_TOKEN
from services.mailing import broadcast_message
from aiogram import Bot


async def main():
    bot = Bot(token=BOT_TOKEN)

    # Данные для рассылки
    image_url = "https://example.com/new-course.jpg"  # Замените на реальную ссылку
    text = """🔥 <b>Новый курс по Machine Learning!</b>

Освойте одну из самых востребованных профессий 2024 года!

🎯 Что вы получите:
• Практические навыки ML
• Реальные проекты в портфолио
• Поддержку ментора
• Сертификат о завершении

Не упустите шанс стать специалистом в области ИИ!"""

    button_url = "https://example.com/ml-course"  # Замените на реальную ссылку

    success_count = await broadcast_message(bot, image_url, text, button_url, "Записаться на курс")
    print(f"Рассылка отправлена {success_count} пользователям")

    await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())