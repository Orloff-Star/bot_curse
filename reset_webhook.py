import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot

load_dotenv()


async def reset_webhook():
    """Сброс вебхука и установка правильного для Bothost.ru"""
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN не найден")
        return

    bot = Bot(token=token)

    # ID вашего приложения в Bothost.ru
    BOTHOST_APP_ID = "bot_1763602889_6267_eaglestar"
    WEBHOOK_URL = f"https://{BOTHOST_APP_ID}.bothost.ru/webhook"

    try:
        print("=== СБРОС ВЕБХУКА ДЛЯ BOTHOST.RU ===")

        # Получаем текущую информацию
        webhook_info = await bot.get_webhook_info()
        print(f"Текущий вебхук: {webhook_info.url}")

        # Удаляем старый вебхук
        await bot.delete_webhook()
        print("✅ Старый вебхук удален")

        # Устанавливаем новый вебхук для Bothost.ru
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )
        print(f"✅ Новый вебхук установлен: {WEBHOOK_URL}")

        # Проверяем установку
        webhook_info = await bot.get_webhook_info()
        print(f"Подтверждение: {webhook_info.url}")

        if BOTHOST_APP_ID in webhook_info.url:
            print("🎉 Вебхук успешно настроен для Bothost.ru!")
        else:
            print("❌ Вебхук все еще указывает на старый адрес")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(reset_webhook())