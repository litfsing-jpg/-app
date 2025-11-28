#!/usr/bin/env python3
"""
Проверка клиентов агентского аккаунта и их кампаний
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("YANDEX_DIRECT_TOKEN")
LOGIN = os.getenv("YANDEX_DIRECT_LOGIN")

print("=" * 80)
print("🏢 АГЕНТСКИЙ АККАУНТ - ПОЛУЧЕНИЕ КЛИЕНТОВ")
print("=" * 80)
print(f"📌 Агентство: {LOGIN}")
print(f"🔑 Токен: {ACCESS_TOKEN[:30]}...")
print("=" * 80)

# ========================================================================
# Шаг 1: Получаем список клиентов агентства
# ========================================================================
print("\n📋 Шаг 1: Получение списка клиентов")
print("-" * 80)

# Для агентских аккаунтов используем метод Clients
clients_url = "https://api.direct.yandex.com/json/v5/agencyclients"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept-Language": "ru",
    "Content-Type": "application/json"
}

payload = {
    "method": "get",
    "params": {
        "SelectionCriteria": {},
        "FieldNames": ["Login", "ClientId", "ClientInfo", "CountryId"]
    }
}

try:
    response = requests.post(clients_url, headers=headers, json=payload, timeout=15)

    print(f"📡 Статус: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        clients = data.get("result", {}).get("Clients", [])

        print(f"✅ Найдено клиентов: {len(clients)}\n")

        if clients:
            print("📋 Список клиентов:")
            for i, client in enumerate(clients, 1):
                client_login = client.get("Login")
                client_id = client.get("ClientId")
                client_info = client.get("ClientInfo", "")

                print(f"\n{i}. Клиент: {client_login}")
                print(f"   ID: {client_id}")
                print(f"   Инфо: {client_info}")

                # Получаем кампании этого клиента
                print(f"   Получаем кампании...")

                campaigns_url = "https://api.direct.yandex.com/json/v5/campaigns"
                campaigns_headers = {
                    "Authorization": f"Bearer {ACCESS_TOKEN}",
                    "Client-Login": client_login,  # ВАЖНО: используем логин клиента!
                    "Accept-Language": "ru",
                    "Content-Type": "application/json"
                }

                campaigns_payload = {
                    "method": "get",
                    "params": {
                        "SelectionCriteria": {},
                        "FieldNames": ["Id", "Name", "Status", "State"]
                    }
                }

                try:
                    camp_response = requests.post(
                        campaigns_url,
                        headers=campaigns_headers,
                        json=campaigns_payload,
                        timeout=15
                    )

                    if camp_response.status_code == 200:
                        camp_data = camp_response.json()
                        campaigns = camp_data.get("result", {}).get("Campaigns", [])

                        print(f"   ✅ Кампаний: {len(campaigns)}")

                        for camp in campaigns[:3]:  # Показываем первые 3
                            print(f"      - {camp['Name']} (ID: {camp['Id']}, Статус: {camp['Status']})")

                        if len(campaigns) > 3:
                            print(f"      ... и ещё {len(campaigns) - 3}")
                    else:
                        print(f"   ❌ Ошибка получения кампаний: {camp_response.status_code}")

                except Exception as e:
                    print(f"   ❌ Ошибка: {e}")

            print("\n" + "=" * 80)
            print("💡 РЕШЕНИЕ ДЛЯ АГЕНТСКИХ АККАУНТОВ:")
            print("=" * 80)
            print("Для получения всех кампаний нужно:")
            print("1. Получить список клиентов (AgencyClients API)")
            print("2. Для КАЖДОГО клиента делать запрос с его Client-Login")
            print("3. Агрегировать данные со всех клиентов")
            print("\n📝 Обновим API функции для работы с агентским аккаунтом")
            print("=" * 80)

        else:
            print("⚠️  Клиентов не найдено")
            print("\n💡 Попробуем другой метод...")

            # Пробуем через обычный метод campaigns без Client-Login
            print("\n📋 Проверка: запрос кампаний без указания клиента")
            print("-" * 80)

            campaigns_url = "https://api.direct.yandex.com/json/v5/campaigns"
            campaigns_headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Accept-Language": "ru",
                "Content-Type": "application/json"
            }

            campaigns_payload = {
                "method": "get",
                "params": {
                    "SelectionCriteria": {},
                    "FieldNames": ["Id", "Name", "Status"]
                }
            }

            camp_response = requests.post(
                campaigns_url,
                headers=campaigns_headers,
                json=campaigns_payload,
                timeout=15
            )

            print(f"📡 Статус: {camp_response.status_code}")

            if camp_response.status_code == 200:
                camp_data = camp_response.json()
                campaigns = camp_data.get("result", {}).get("Campaigns", [])
                print(f"   Кампаний: {len(campaigns)}")

                if campaigns:
                    for camp in campaigns:
                        print(f"   - {camp['Name']} (ID: {camp['Id']})")

    else:
        print(f"❌ ОШИБКА: {response.status_code}")
        print(f"Ответ: {response.text}")

        # Попробуем альтернативный подход - получить кампании напрямую
        print("\n💡 Пробуем получить кампании напрямую (может это не совсем агентский аккаунт)")
        print("-" * 80)

except Exception as e:
    print(f"❌ ОШИБКА: {e}")

print("\n" + "=" * 80)
print("🏁 ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 80)
