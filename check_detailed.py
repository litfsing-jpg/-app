#!/usr/bin/env python3
"""
Детальная проверка кампаний с разными фильтрами
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("YANDEX_DIRECT_TOKEN")
LOGIN = os.getenv("YANDEX_DIRECT_LOGIN")

print("=" * 80)
print("🔍 ДЕТАЛЬНАЯ ПРОВЕРКА КАМПАНИЙ")
print("=" * 80)
print(f"📌 Login: {LOGIN}")
print(f"🔑 Токен: {ACCESS_TOKEN[:30]}...")
print("=" * 80)

url = "https://api.direct.yandex.com/json/v5/campaigns"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Client-Login": LOGIN,
    "Accept-Language": "ru",
    "Content-Type": "application/json"
}

# Тест 1: Все кампании (без фильтра по статусу)
print("\n📋 Тест 1: Все кампании (без фильтра)")
print("-" * 80)

payload = {
    "method": "get",
    "params": {
        "SelectionCriteria": {},
        "FieldNames": ["Id", "Name", "Status", "State", "Type"]
    }
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    print(f"📡 Статус: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        campaigns = data.get("result", {}).get("Campaigns", [])
        print(f"✅ Найдено: {len(campaigns)}")

        if campaigns:
            for camp in campaigns:
                print(f"   - {camp['Name']} (ID: {camp['Id']}, Статус: {camp['Status']}, Состояние: {camp['State']})")
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Тест 2: С более широким набором полей
print("\n📋 Тест 2: Запрос с максимальным набором полей")
print("-" * 80)

payload2 = {
    "method": "get",
    "params": {
        "SelectionCriteria": {},
        "FieldNames": [
            "Id", "Name", "Status", "State", "StatusPayment",
            "StatusClarification", "Type"
        ]
    }
}

try:
    response = requests.post(url, headers=headers, json=payload2, timeout=15)
    print(f"📡 Статус: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        campaigns = data.get("result", {}).get("Campaigns", [])
        print(f"✅ Найдено: {len(campaigns)}")

        if campaigns:
            for camp in campaigns:
                print(f"   {camp}")
    else:
        print(f"❌ Ошибка: {response.status_code}")
        error_data = response.json()
        print(json.dumps(error_data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Тест 3: Проверка прав токена
print("\n📋 Тест 3: Проверка прав доступа токена")
print("-" * 80)

print("Попробуем получить любые данные через API...")

# Проверим доступ к AdGroups
adgroups_url = "https://api.direct.yandex.com/json/v5/adgroups"
payload3 = {
    "method": "get",
    "params": {
        "SelectionCriteria": {},
        "FieldNames": ["Id", "Name", "CampaignId"]
    }
}

try:
    response = requests.post(adgroups_url, headers=headers, json=payload3, timeout=15)
    print(f"📡 AdGroups статус: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        adgroups = data.get("result", {}).get("AdGroups", [])
        print(f"   Найдено групп объявлений: {len(adgroups)}")
    else:
        print(f"   Ошибка: {response.text[:200]}")
except Exception as e:
    print(f"   Ошибка: {e}")

print("\n" + "=" * 80)
print("💡 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
print("=" * 80)
print("1. Кампании ещё не синхронизировались в API")
print("2. Токен создан недавно - нужно подождать несколько минут")
print("3. Кампании принадлежат другому клиенту (агентский аккаунт)")
print("4. Недостаточно прав у OAuth приложения")
print("\n💡 ЧТО ПОПРОБОВАТЬ:")
print("- Подождать 5-10 минут и попробовать снова")
print("- Проверить что кампании видны в интерфейсе Директа")
print("- Пересоздать OAuth приложение с полными правами")
print("=" * 80)
