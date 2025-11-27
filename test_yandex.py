#!/usr/bin/env python3
"""
Простой тест Яндекс.Директ API
Запусти: python3 test_yandex.py
"""
import requests
import json

# ВСТАВЬ СЮДА СВОИ ДАННЫЕ
TOKEN = "y0__xCp7sHEAxjO8jsgo6bhshWsrA5ZdgQApJVAbUcp2p-dluCANQ"
LOGIN = "getuniq-u78912-1"

print("🔍 Тестируем подключение к Яндекс.Директ API...")
print(f"📧 Логин: {LOGIN}")
print(f"🔑 Токен: {TOKEN[:20]}...")

url = "https://api.direct.yandex.com/json/v5/campaigns"
headers = {
    "Authorization": f"Bearer {TOKEN}",
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

print("\n📡 Отправляю запрос к API...")
response = requests.post(url, headers=headers, json=payload, timeout=10)

print(f"\n✅ Статус ответа: {response.status_code}")
print(f"\n📦 Полный ответ от API:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

if response.status_code == 200:
    data = response.json()
    if "result" in data:
        campaigns = data["result"].get("Campaigns", [])
        print(f"\n🎉 Найдено кампаний: {len(campaigns)}")
        for camp in campaigns:
            print(f"  - {camp['Name']} (ID: {camp['Id']}) - {camp['Status']}")
    else:
        print("\n❌ В ответе нет 'result'!")
else:
    print("\n❌ ОШИБКА!")
