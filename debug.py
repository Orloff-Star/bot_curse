import asyncio
import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импортов
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()


async def debug_info():
    """Отладочная информация о состоянии бота и базы данных"""
    from aiogram import Bot
    from database.db import create_table, get_all_subscribers, get_pending_messages

    # Проверяем токен
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN не найден в переменных окружения")
        print("Проверьте файл .env или переменные окружения")
        return

    bot = Bot(token=token)

    print("=== DEBUG INFO ===")
    print(f"BOT_TOKEN: {'✅ Установлен' if token else '❌ Отсутствует'}")

    try:
        # Проверка вебхука
        webhook_info = await bot.get_webhook_info()
        print(f"🌐 Webhook URL: {webhook_info.url}")
        print(f"📊 Pending updates: {webhook_info.pending_update_count}")
        print(f"❌ Last error: {webhook_info.last_error_message}")

        # Проверка БД
        await create_table()
        subscribers = await get_all_subscribers()
        pending = await get_pending_messages()

        print(f"👥 Subscribers in DB: {len(subscribers)}")
        print(f"📨 Pending messages: {len(pending)}")

        # Вывод списка подписчиков
        if subscribers:
            print("\n📋 Subscribers list:")
            for sub in subscribers[:10]:  # Показываем первые 10
                print(f"  - User ID: {sub}")

        # Вывод ожидающих сообщений
        if pending:
            print("\n⏰ Pending messages:")
            for msg in pending[:10]:  # Показываем первые 10
                print(f"  - ID: {msg[0]}, User: {msg[1]}, Stage: {msg[2]}")

    except Exception as e:
        print(f"❌ Ошибка при получении информации: {e}")
    finally:
        await bot.session.close()


async def test_database():
    """Тестирование функций базы данных"""
    from database.db import create_table, add_subscriber, add_scheduled_message, get_pending_messages

    print("\n=== DATABASE TEST ===")

    try:
        # Создаем таблицы
        await create_table()
        print("✅ Таблицы БД созданы/проверены")

        # Тестовый пользователь
        test_user_id = 123456789
        await add_subscriber(test_user_id, "test_user", "Test User")
        print("✅ Тестовый пользователь добавлен")

        # Тестовое запланированное сообщение
        await add_scheduled_message(test_user_id, 1, 1)  # Через 1 минуту
        print("✅ Тестовое сообщение запланировано")

        # Проверяем ожидающие сообщения
        pending = await get_pending_messages()
        print(f"✅ Ожидающие сообщения: {len(pending)}")

    except Exception as e:
        print(f"❌ Ошибка тестирования БД: {e}")


async def test_bot_functionality():
    """Тестирование функциональности бота"""
    from aiogram import Bot
    from aiogram.methods import GetMe

    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN не найден для тестирования")
        return

    bot = Bot(token=token)

    print("\n=== BOT FUNCTIONALITY TEST ===")

    try:
        # Проверяем, что бот доступен
        me = await bot(GetMe())
        print(f"✅ Бот доступен: {me.first_name} (@{me.username})")

        # Проверяем вебхук
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url:
            print(f"✅ Вебхук установлен: {webhook_info.url}")
        else:
            print("⚠️ Вебхук не установлен")

    except Exception as e:
        print(f"❌ Ошибка тестирования бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    print("Запуск отладочной информации...")


    # Создаем event loop и запускаем все тесты
    async def main():
        await debug_info()
        await test_database()
        await test_bot_functionality()


    asyncio.run(main())