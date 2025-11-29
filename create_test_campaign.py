#!/usr/bin/env python3
"""
Создание тестовой кампании через API
Проверим появится ли она сразу
"""
import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("YANDEX_DIRECT_TOKEN")
LOGIN = os.getenv("YANDEX_DIRECT_LOGIN")

print("=" * 80)
print("🧪 СОЗДАНИЕ ТЕСТОВОЙ КАМПАНИИ")
print("=" * 80)
print(f"📌 Login: {LOGIN}")
print(f"🔑 Токен: {ACCESS_TOKEN[:30]}...")
print("=" * 80)

# Создаём тестовую кампанию
url = "https://api.direct.yandex.com/json/v5/campaigns"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Client-Login": LOGIN,
    "Accept-Language": "ru",
    "Content-Type": "application/json"
}

# Параметры тестовой кампании
today = datetime.now()
start_date = today.strftime("%Y-%m-%d")
end_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")

test_campaign = {
    "method": "add",
    "params": {
        "Campaigns": [
            {
                "Name": f"API Test Campaign {today.strftime('%Y%m%d_%H%M%S')}",
                "StartDate": start_date,
                "EndDate": end_date,
                "TextCampaign": {
                    "BiddingStrategy": {
                        "Search": {
                            "BiddingStrategyType": "HIGHEST_POSITION"
                        },
                        "Network": {
                            "BiddingStrategyType": "SERVING_OFF"
                        }
                    },
                    "Settings": []
                }
            }
        ]
    }
}

print("\n📋 Шаг 1: Попытка создать тестовую кампанию")
print("-" * 80)
print(f"Название: API Test Campaign {today.strftime('%Y%m%d_%H%M%S')}")
print(f"Период: {start_date} - {end_date}")
print()

try:
    response = requests.post(url, headers=headers, json=test_campaign, timeout=15)

    print(f"📡 Статус: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        if "result" in data:
            campaign_ids = data["result"].get("AddResults", [])

            if campaign_ids:
                new_id = campaign_ids[0].get("Id")
                print(f"✅ УСПЕХ! Кампания создана!")
                print(f"   ID: {new_id}")
                print()

                # Сразу пробуем получить её
                print("\n📋 Шаг 2: Проверяем - видна ли новая кампания сразу")
                print("-" * 80)

                import time
                time.sleep(2)  # Ждём 2 секунды

                get_payload = {
                    "method": "get",
                    "params": {
                        "SelectionCriteria": {"Ids": [new_id]},
                        "FieldNames": ["Id", "Name", "Status", "State"]
                    }
                }

                get_response = requests.post(url, headers=headers, json=get_payload, timeout=15)

                if get_response.status_code == 200:
                    get_data = get_response.json()
                    campaigns = get_data.get("result", {}).get("Campaigns", [])

                    if campaigns:
                        print(f"✅ КАМПАНИЯ ВИДНА СРАЗУ!")
                        print(f"   Название: {campaigns[0]['Name']}")
                        print(f"   Статус: {campaigns[0]['Status']}")
                        print()
                        print("💡 ВЫВОД:")
                        print("   Новые кампании видны через API сразу!")
                        print("   Старые кампании ТОЖЕ должны быть видны.")
                        print()
                        print("🔍 ПРОБЛЕМА НЕ В ДАТЕ СОЗДАНИЯ!")
                        print("   Скорее всего старые кампании:")
                        print("   - Принадлежат другому аккаунту/клиенту")
                        print("   - Или созданы через Direct Commander")
                    else:
                        print("⚠️  Кампания создана, но пока не видна")
                        print("   Возможна задержка синхронизации")
            else:
                print("⚠️  Кампания вроде создана, но нет ID")
                print(f"   Ответ: {data}")
        else:
            print("❌ Ошибка создания")
            print(f"   Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")

    elif response.status_code == 400:
        error_data = response.json()
        print(f"❌ ОШИБКА 400: Неверные параметры")
        print(json.dumps(error_data, indent=2, ensure_ascii=False))

    elif response.status_code == 403:
        print(f"❌ ОШИБКА 403: Нет прав на создание кампаний")
        print("   Токен должен иметь права 'Яндекс.Директ: управление рекламными кампаниями'")
        print()
        print("💡 РЕШЕНИЕ:")
        print("   1. Создайте новое OAuth приложение с полными правами")
        print("   2. Или создайте кампанию вручную в интерфейсе")
        print("   3. Подождите 1-2 часа и проверьте появится ли в API")

    else:
        print(f"❌ ОШИБКА {response.status_code}")
        print(f"   Ответ: {response.text}")

except Exception as e:
    print(f"❌ ОШИБКА: {e}")

print("\n" + "=" * 80)
print("💡 АЛЬТЕРНАТИВНЫЙ ТЕСТ:")
print("=" * 80)
print("Если создание через API не работает:")
print()
print("1. Создайте новую кампанию ВРУЧНУЮ в интерфейсе Яндекс.Директ")
print("2. Подождите 5 минут")
print("3. Запустите: python check_detailed.py")
print("4. Проверьте появилась ли новая кампания")
print()
print("Если новая появилась, а старые нет → проблема в миграции старых кампаний")
print("Если и новая не появилась → проблема в правах токена или агентском аккаунте")
print("=" * 80)
