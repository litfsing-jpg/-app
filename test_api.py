#!/usr/bin/env python3
"""
Простой тест Yandex Direct API
Проверяет работу с одобренным токеном
"""
import os
import requests
import json

# Загружаем переменные из .env
from dotenv import load_dotenv
load_dotenv()

# Получаем токен и логин
ACCESS_TOKEN = os.getenv("YANDEX_DIRECT_TOKEN")
LOGIN = os.getenv("YANDEX_DIRECT_LOGIN")

print("=" * 60)
print("🧪 ТЕСТ YANDEX DIRECT API")
print("=" * 60)
print(f"📌 Логин: {LOGIN}")
print(f"🔑 Токен: {ACCESS_TOKEN[:20]}..." if ACCESS_TOKEN else "❌ Токен не найден!")
print("=" * 60)

if not ACCESS_TOKEN or not LOGIN:
    print("❌ ОШИБКА: Переменные окружения не настроены!")
    print("Проверьте файл .env")
    exit(1)

# Тест 1: Получение списка кампаний
print("\n📋 Тест 1: Получение списка кампаний...")
print("-" * 60)

url = "https://api.direct.yandex.com/json/v5/campaigns"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Client-Login": LOGIN,
    "Accept-Language": "ru",
    "Content-Type": "application/json"
}

payload = {
    "method": "get",
    "params": {
        "SelectionCriteria": {},
        "FieldNames": ["Id", "Name", "Status", "State"]
    }
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)

    print(f"📡 Статус ответа: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        campaigns = data.get("result", {}).get("Campaigns", [])

        print(f"✅ УСПЕХ! Получено кампаний: {len(campaigns)}\n")

        if campaigns:
            print("Список кампаний:")
            for i, campaign in enumerate(campaigns[:5], 1):  # Показываем первые 5
                print(f"  {i}. {campaign['Name']}")
                print(f"     ID: {campaign['Id']}, Статус: {campaign['Status']}")
        else:
            print("⚠️  У вас нет кампаний в аккаунте")
    else:
        print(f"❌ ОШИБКА {response.status_code}")
        print(f"Ответ API: {response.text[:500]}")

        # Попробуем распарсить ошибку
        try:
            error_data = response.json()
            if "error" in error_data:
                print(f"\nДетали ошибки:")
                print(f"  Код: {error_data['error'].get('error_code')}")
                print(f"  Описание: {error_data['error'].get('error_detail')}")
        except:
            pass

except requests.exceptions.Timeout:
    print("❌ TIMEOUT: API не ответил за 30 секунд")
except requests.exceptions.ConnectionError as e:
    print(f"❌ ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
    print("\nВозможные причины:")
    print("  - Нет доступа к api.direct.yandex.com")
    print("  - Блокировка прокси/файрвола")
except Exception as e:
    print(f"❌ НЕОЖИДАННАЯ ОШИБКА: {e}")

print("\n" + "=" * 60)
print("🏁 ТЕСТ ЗАВЕРШЁН")
print("=" * 60)
