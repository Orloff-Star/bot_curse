import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# Для bothost.ru используем их настройки
# Bothost обычно предоставляет свой URL через переменные окружения
BOTHOST_URL = os.getenv("BOTHOST_URL", "https://your-domain.bothost.ru")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{BOTHOST_URL}{WEBHOOK_PATH}"

# Настройки для планировщика
SELF_PING_ENABLED = os.getenv("SELF_PING_ENABLED", "false").lower() == "true"
SELF_PING_INTERVAL = int(os.getenv("SELF_PING_INTERVAL", "10"))