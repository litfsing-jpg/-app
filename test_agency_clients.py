import requests

# Ваши данные
TOKEN = "y0__xClvtjPBRjv-DsgvPWruBUw-9mmxQhAy9qWa9MiAGc795tFeGmeQZP4rg"
LOGIN = "getuniq-u78912-1"

print("=" * 80)
print("ТЕСТ АГЕНТСКОГО АККАУНТА ЯНДЕКС.ДИРЕКТ")
print("=" * 80)

# Шаг 1: Получаем список клиентов агентства
print("\n1. ПОЛУЧЕНИЕ СПИСКА КЛИЕНТОВ АГЕНТСТВА...")
print("-" * 80)

url = "https://api.direct.yandex.com/json/v5/agencyclients"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept-Language": "ru",
    "Content-Type": "application/json"
    # НЕ указываем Client-Login для agencyclients!
}

payload = {
    "method": "get",
    "params": {
        "SelectionCriteria": {},
        "FieldNames": ["Login", "ClientId", "ClientInfo", "CountryId", "CreatedAt"]
    }
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=10)

    if response.status_code == 200:
        data = response.json()
        clients = data.get("result", {}).get("Clients", [])

        print(f"✅ Найдено клиентов: {len(clients)}")

        if len(clients) == 0:
            print("\n⚠️ У агентства нет клиентов!")
            print("Возможные причины:")
            print("1. Клиенты не добавлены в агентский аккаунт")
            print("2. Токен не имеет прав агентства")
            exit()

        print("\n" + "=" * 80)
        print("СПИСОК КЛИЕНТОВ:")
        print("=" * 80)

        for i, client in enumerate(clients, 1):
            print(f"\n{i}. Логин: {client.get('Login')}")
            print(f"   ClientId: {client.get('ClientId')}")
            if 'ClientInfo' in client:
                print(f"   Инфо: {client.get('ClientInfo')}")

        # Шаг 2: Для каждого клиента получаем кампании
        print("\n" + "=" * 80)
        print("2. ПОЛУЧЕНИЕ КАМПАНИЙ КЛИЕНТОВ...")
        print("=" * 80)

        total_campaigns = 0

        for client in clients:
            client_login = client.get('Login')
            print(f"\n--- КЛИЕНТ: {client_login} ---")

            # Запрашиваем кампании клиента
            campaigns_url = "https://api.direct.yandex.com/json/v5/campaigns"
            campaigns_headers = {
                "Authorization": f"Bearer {TOKEN}",
                "Client-Login": client_login,  # ВАЖНО: указываем логин клиента!
                "Accept-Language": "ru",
                "Content-Type": "application/json"
            }

            campaigns_payload = {
                "method": "get",
                "params": {
                    "SelectionCriteria": {},
                    "FieldNames": ["Id", "Name", "Status", "State", "Type"]
                }
            }

            try:
                campaigns_response = requests.post(
                    campaigns_url,
                    headers=campaigns_headers,
                    json=campaigns_payload,
                    timeout=10
                )

                if campaigns_response.status_code == 200:
                    campaigns_data = campaigns_response.json()
                    campaigns = campaigns_data.get("result", {}).get("Campaigns", [])

                    active_campaigns = [c for c in campaigns if c.get('State') != 'ARCHIVED']
                    archived_campaigns = [c for c in campaigns if c.get('State') == 'ARCHIVED']

                    print(f"   Всего кампаний: {len(campaigns)}")
                    print(f"   Активных: {len(active_campaigns)}")
                    print(f"   Архивных: {len(archived_campaigns)}")

                    total_campaigns += len(campaigns)

                    if active_campaigns:
                        print("\n   🟢 АКТИВНЫЕ КАМПАНИИ:")
                        for camp in active_campaigns:
                            print(f"      • {camp.get('Name')}")
                            print(f"        ID: {camp.get('Id')}")
                            print(f"        Статус: {camp.get('Status')}")
                            print(f"        Состояние: {camp.get('State')}")
                            print()

                    if archived_campaigns:
                        print(f"   📦 Архивных кампаний: {len(archived_campaigns)}")

                else:
                    print(f"   ❌ Ошибка: {campaigns_response.status_code}")
                    print(f"   {campaigns_response.text[:200]}")

            except Exception as e:
                print(f"   ❌ Ошибка при запросе кампаний: {e}")

        print("\n" + "=" * 80)
        print(f"✅ ИТОГО: {len(clients)} клиентов, {total_campaigns} кампаний")
        print("=" * 80)

    else:
        print(f"❌ Ошибка при получении клиентов!")
        print(f"Код: {response.status_code}")
        print(f"Ответ: {response.text}")

except Exception as e:
    print(f"❌ Ошибка: {e}")

print()
input("Нажмите Enter чтобы закрыть...")
