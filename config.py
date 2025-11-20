import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# Конфигурация для Bothost.ru с ID приложения
BOTHOST_APP_ID = os.getenv("BOTHOST_APP_ID", "bot_1763602889_6267_eaglestar")
WEBHOOK_PATH = "/webhook"

# Bothost.ru использует структуру URL: https://<app-id>.bothost.ru
WEBHOOK_URL = f"https://{BOTHOST_APP_ID}.bothost.ru{WEBHOOK_PATH}"

# Отключаем само-пинг для Bothost.ru
SELF_PING_ENABLED = False