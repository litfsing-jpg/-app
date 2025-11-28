#!/usr/bin/env python3
"""
Детальная диагностика проблемы с кампаниями
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("YANDEX_DIRECT_TOKEN")
LOGIN = os.getenv("YANDEX_DIRECT_LOGIN")

print("=" * 80)
print("🔍 ДЕТАЛЬНАЯ ДИАГНОСТИКА ПРОБЛЕМЫ")
print("=" * 80)
print(f"📌 Client-Login: {LOGIN}")
print(f"🔑 Токен: {ACCESS_TOKEN[:30]}...")
print("=" * 80)

# ========================================================================
# ТЕСТ 1: Запрос БЕЗ Client-Login (от имени владельца токена)
# ========================================================================
print("\n🧪 ТЕСТ 1: Запрос БЕЗ Client-Login")
print("-" * 80)

url = "https://api.direct.yandex.com/json/v5/campaigns"
headers_without_login = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    # НЕТ Client-Login!
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
    response = requests.post(url, headers=headers_without_login, json=payload, timeout=15)

    print(f"📡 Статус: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        campaigns = data.get("result", {}).get("Campaigns", [])

        print(f"✅ УСПЕХ! Найдено кампаний: {len(campaigns)}")

        if campaigns:
            print("\n📋 Список кампаний:")
            for camp in campaigns:
                print(f"   - ID: {camp['Id']}")
                print(f"     Название: {camp['Name']}")
                print(f"     Статус: {camp['Status']}")
                print()
        else:
            print("⚠️  Кампаний не найдено")
    else:
        print(f"❌ ОШИБКА: {response.status_code}")
        print(f"Ответ: {response.text[:500]}")

except Exception as e:
    print(f"❌ ОШИБКА: {e}")

# ========================================================================
# ТЕСТ 2: Запрос С Client-Login
# ========================================================================
print("\n🧪 ТЕСТ 2: Запрос С Client-Login = '{}'".format(LOGIN))
print("-" * 80)

headers_with_login = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Client-Login": LOGIN,
    "Accept-Language": "ru",
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, headers=headers_with_login, json=payload, timeout=15)

    print(f"📡 Статус: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        campaigns = data.get("result", {}).get("Campaigns", [])

        print(f"✅ УСПЕХ! Найдено кампаний: {len(campaigns)}")

        if campaigns:
            print("\n📋 Список кампаний:")
            for camp in campaigns:
                print(f"   - ID: {camp['Id']}")
                print(f"     Название: {camp['Name']}")
                print(f"     Статус: {camp['Status']}")
                print()
        else:
            print("⚠️  Кампаний не найдено")
    else:
        print(f"❌ ОШИБКА: {response.status_code}")
        print(f"Ответ: {response.text[:500]}")

        try:
            error_data = response.json()
            if "error" in error_data:
                print(f"\n🔴 Детали ошибки:")
                print(f"   Код: {error_data['error'].get('error_code')}")
                print(f"   Описание: {error_data['error'].get('error_detail')}")
                print(f"   Строка: {error_data['error'].get('error_string')}")
        except:
            pass

except Exception as e:
    print(f"❌ ОШИБКА: {e}")

# ========================================================================
# ТЕСТ 3: Получение информации о владельце токена
# ========================================================================
print("\n🧪 ТЕСТ 3: Проверка владельца токена")
print("-" * 80)

# Попробуем получить info о пользователе через OAuth API
try:
    oauth_url = "https://login.yandex.ru/info"
    oauth_headers = {
        "Authorization": f"OAuth {ACCESS_TOKEN}"
    }

    response = requests.get(oauth_url, headers=oauth_headers, timeout=10)

    if response.status_code == 200:
        user_info = response.json()
        print(f"✅ Информация о владельце токена:")
        print(f"   Login: {user_info.get('login')}")
        print(f"   Display Name: {user_info.get('display_name')}")
        print(f"   Email: {user_info.get('default_email')}")

        token_login = user_info.get('login')
        if token_login != LOGIN:
            print(f"\n⚠️  ВНИМАНИЕ!")
            print(f"   Токен принадлежит: {token_login}")
            print(f"   Client-Login указан: {LOGIN}")
            print(f"   ❌ НЕ СОВПАДАЮТ!")
            print(f"\n💡 РЕШЕНИЕ:")
            print(f"   Используйте Client-Login = '{token_login}'")
            print(f"   ИЛИ получите новый токен для аккаунта '{LOGIN}'")
        else:
            print(f"\n✅ Токен и Client-Login совпадают!")
    else:
        print(f"⚠️  Не удалось получить информацию о токене: {response.status_code}")

except Exception as e:
    print(f"⚠️  Ошибка при проверке токена: {e}")

print("\n" + "=" * 80)
print("🏁 ДИАГНОСТИКА ЗАВЕРШЕНА")
print("=" * 80)
