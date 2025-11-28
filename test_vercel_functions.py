#!/usr/bin/env python3
"""
Тест Vercel serverless функций локально
Симулирует как они будут работать на Vercel
"""
import os
import sys
import json

# Добавляем текущую директорию в path
sys.path.insert(0, os.path.dirname(__file__))

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("🧪 ТЕСТ VERCEL SERVERLESS ФУНКЦИЙ")
print("=" * 70)

# Тест функции campaigns
print("\n📋 Тест 1: /api/campaigns")
print("-" * 70)

try:
    # Импортируем модуль campaigns
    from api import campaigns

    # Создаём мок HTTP запроса
    class MockRequest:
        def __init__(self):
            self.response_code = None
            self.response_headers = {}
            self.response_body = None

        def send_response(self, code):
            self.response_code = code
            print(f"📡 Статус: {code}")

        def send_header(self, key, value):
            self.response_headers[key] = value

        def end_headers(self):
            pass

        def wfile_write(self, data):
            self.response_body = data

    # Создаём экземпляр handler
    mock_request = MockRequest()
    handler_instance = campaigns.handler(None, None, None)
    handler_instance.send_response = mock_request.send_response
    handler_instance.send_header = mock_request.send_header
    handler_instance.end_headers = mock_request.end_headers
    handler_instance.wfile = type('obj', (object,), {'write': mock_request.wfile_write})()

    # Вызываем функцию
    handler_instance.do_GET()

    # Проверяем результат
    if mock_request.response_code == 200:
        data = json.loads(mock_request.response_body.decode())
        print(f"✅ УСПЕХ!")
        print(f"   Формат: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")

        if data.get("success"):
            campaigns_count = len(data.get("campaigns", []))
            print(f"   Кампаний: {campaigns_count}")
    else:
        print(f"❌ Ошибка: {mock_request.response_code}")
        if mock_request.response_body:
            print(f"   Ответ: {mock_request.response_body.decode()}")

except Exception as e:
    print(f"❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()

# Тест функции stats
print("\n📊 Тест 2: /api/stats")
print("-" * 70)

try:
    from api import stats

    mock_request = MockRequest()
    handler_instance = stats.handler(None, None, None)
    handler_instance.send_response = mock_request.send_response
    handler_instance.send_header = mock_request.send_header
    handler_instance.end_headers = mock_request.end_headers
    handler_instance.wfile = type('obj', (object,), {'write': mock_request.wfile_write})()

    handler_instance.do_GET()

    if mock_request.response_code == 200:
        data = json.loads(mock_request.response_body.decode())
        print(f"✅ УСПЕХ!")
        print(f"   Формат: {json.dumps(data, ensure_ascii=False, indent=2)[:300]}...")

        if data.get("success"):
            stats_data = data.get("stats", {})
            print(f"   Показы: {stats_data.get('total_impressions', 0)}")
            print(f"   Клики: {stats_data.get('total_clicks', 0)}")
            print(f"   Расход: {stats_data.get('total_cost', 0)} ₽")
    else:
        print(f"❌ Ошибка: {mock_request.response_code}")
        if mock_request.response_body:
            print(f"   Ответ: {mock_request.response_body.decode()}")

except Exception as e:
    print(f"❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("🏁 ТЕСТ ЗАВЕРШЁН")
print("=" * 70)
print("\n💡 Вывод:")
print("   Если оба теста ✅ УСПЕХ - значит код готов для Vercel!")
print("   Можно смело создавать Pull Request и деплоить.")
print("=" * 70)
