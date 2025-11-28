#!/usr/bin/env python3
"""
Проверка кампаний для владельца токена (ivan00567)
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("YANDEX_DIRECT_TOKEN")

print("=" * 80)
print("🔍 ПРОВЕРКА КАМПАНИЙ ДЛЯ ВЛАДЕЛЬЦА ТОКЕНА")
print("=" * 80)
print(f"📌 Login: ivan00567 (владелец токена)")
print(f"🔑 Токен: {ACCESS_TOKEN[:30]}...")
print("=" * 80)

url = "https://api.direct.yandex.com/json/v5/campaigns"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Client-Login": "ivan00567",  # Владелец токена
    "Accept-Language": "ru",
    "Content-Type": "application/json"
}

payload = {
    "method": "get",
    "params": {
        "SelectionCriteria": {},
        "FieldNames": ["Id", "Name", "Status", "State", "StartDate"]
    }
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=15)

    print(f"\n📡 Статус: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        campaigns = data.get("result", {}).get("Campaigns", [])

        print(f"✅ Найдено кампаний: {len(campaigns)}\n")

        if campaigns:
            print("📋 Список кампаний:")
            for i, camp in enumerate(campaigns, 1):
                print(f"\n{i}. {camp['Name']}")
                print(f"   ID: {camp['Id']}")
                print(f"   Статус: {camp['Status']}")
                print(f"   Состояние: {camp.get('State', 'N/A')}")

            print(f"\n✅ РЕШЕНИЕ НАЙДЕНО!")
            print(f"   Используйте Client-Login = 'ivan00567'")
            print(f"\n📝 Обновите .env:")
            print(f"   YANDEX_DIRECT_LOGIN=ivan00567")
            print(f"\n📝 Обновите Vercel:")
            print(f"   Settings → Environment Variables → YANDEX_DIRECT_LOGIN = ivan00567")
        else:
            print("⚠️  У ivan00567 тоже нет кампаний")
            print("\n💡 Возможно getuniq-u78912-1 это КЛИЕНТСКИЙ аккаунт")
            print("   Нужен токен с правами доступа к нему")
    else:
        print(f"❌ ОШИБКА: {response.status_code}")
        print(f"Ответ: {response.text}")

except Exception as e:
    print(f"❌ ОШИБКА: {e}")

print("\n" + "=" * 80)
