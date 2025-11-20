import requests
import os
from dotenv import load_dotenv

load_dotenv()


def test_bothost_url():
    """Проверка доступности URL Bothost.ru"""
    BOTHOST_APP_ID = "bot_1763602889_6267_eaglestar"
    base_url = f"https://{BOTHOST_APP_ID}.bothost.ru"

    print(f"Тестируем URL: {base_url}")

    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✅ Статус: {response.status_code}")
        print(f"✅ Ответ: {response.text}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения: {e}")
        return False


if __name__ == "__main__":
    test_bothost_url()