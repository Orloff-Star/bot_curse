import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# Для bothost.ru - используем их домен
# Получите ваш реальный домен от bothost.ru и замените здесь
BOTHOST_DOMAIN = os.getenv("BOTHOST_DOMAIN", "bot_1763602889_6267_eaglestar")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{BOTHOST_DOMAIN}{WEBHOOK_PATH}"

# Отключаем само-пинг для bothost.ru (они сами поддерживают активность)
SELF_PING_ENABLED = False