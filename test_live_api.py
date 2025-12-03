#!/usr/bin/env python3
"""
Простой тест Яндекс.Директ API
Проверяет: токен, список кампаний, детали
"""
import os
import requests
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

def test_api():
    print("=" * 60)
    print("🔍 ТЕСТ ЯНДЕКС.ДИРЕКТ API")
    print("=" * 60)
    print()

    # Получаем данные из .env
    token = os.getenv("YANDEX_DIRECT_TOKEN")
    login = os.getenv("YANDEX_DIRECT_LOGIN")

    print(f"📌 Токен: {token[:20]}...{token[-10:] if token else 'НЕТ'}")
    print(f"📌 Логин: {login}")
    print()

    if not token or not login:
        print("❌ ОШИБКА: Нет токена или логина в .env файле!")
        return

    # Проверяем токен
    print("=" * 60)
    print("1️⃣  ПРОВЕРКА ТОКЕНА")
    print("=" * 60)

    try:
        oauth_url = "https://login.yandex.ru/info"
        oauth_headers = {"Authorization": f"OAuth {token}"}
        oauth_response = requests.get(oauth_url, headers=oauth_headers, timeout=10)

        if oauth_response.status_code == 200:
            user_info = oauth_response.json()
            print(f"✅ Токен валидный!")
            print(f"   Владелец: {user_info.get('login', 'неизвестно')}")
            print(f"   ID: {user_info.get('id', 'неизвестно')}")
        else:
            print(f"❌ Токен невалидный! Код: {oauth_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Ошибка при проверке токена: {e}")
        return

    print()

    # Получаем список кампаний
    print("=" * 60)
    print("2️⃣  ПОЛУЧЕНИЕ СПИСКА КАМПАНИЙ")
    print("=" * 60)

    try:
        url = "https://api.direct.yandex.com/json/v5/campaigns"
        headers = {
            "Authorization": f"Bearer {token}",
            "Client-Login": login,
            "Accept-Language": "ru",
            "Content-Type": "application/json"
        }

        payload = {
            "method": "get",
            "params": {
                "SelectionCriteria": {},
                "FieldNames": ["Id", "Name", "Status", "State", "Type"]
            }
        }

        print(f"📡 Отправляю запрос к {url}...")
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        print(f"📥 Код ответа: {response.status_code}")
        print()

        if response.status_code == 200:
            data = response.json()
            campaigns = data.get("result", {}).get("Campaigns", [])

            print(f"✅ УСПЕХ! Найдено кампаний: {len(campaigns)}")
            print()

            if len(campaigns) == 0:
                print("⚠️  КАМПАНИЙ НЕТ!")
                print()
                print("Возможные причины:")
                print("1. У аккаунта действительно нет кампаний")
                print("2. Это агентский аккаунт - кампании принадлежат клиентам")
                print("3. Нужно подождать синхронизации (24-48 часов)")
                print("4. Кампания только создана - нужно подождать")
            else:
                print("=" * 60)
                print("📋 СПИСОК КАМПАНИЙ:")
                print("=" * 60)

                for i, campaign in enumerate(campaigns, 1):
                    print(f"\n{i}. ID: {campaign.get('Id')}")
                    print(f"   Название: {campaign.get('Name')}")
                    print(f"   Статус: {campaign.get('Status')}")
                    print(f"   Состояние: {campaign.get('State')}")
                    print(f"   Тип: {campaign.get('Type', 'не указан')}")
        else:
            print(f"❌ ОШИБКА API!")
            print(f"Код: {response.status_code}")
            print(f"Ответ: {response.text[:500]}")

    except Exception as e:
        print(f"❌ Ошибка при запросе: {e}")
        return

    print()
    print("=" * 60)
    print("✅ ТЕСТ ЗАВЕРШЁН")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
