"""
Yandex Direct API Integration
Основано на: https://github.com/pavelmaksimov/tapi-yandex-direct
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests


class YandexDirectAPI:
    """
    Класс для работы с Yandex Direct API v5
    """

    def __init__(self, access_token: str, login: str, is_sandbox: bool = False):
        """
        Инициализация клиента Yandex Direct API

        Args:
            access_token: OAuth токен доступа
            login: Логин клиента в Яндекс.Директ
            is_sandbox: Использовать sandbox режим (для тестирования)
        """
        self.access_token = access_token
        self.login = login
        self.is_sandbox = is_sandbox

        # API URLs
        self.api_url = "https://api-sandbox.direct.yandex.com/json/v5/" if is_sandbox else "https://api.direct.yandex.com/json/v5/"
        self.reports_url = "https://api-sandbox.direct.yandex.com/v4/json/" if is_sandbox else "https://api.direct.yandex.ru/reports/"

        # Headers
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Client-Login": login,
            "Accept-Language": "ru",
            "Content-Type": "application/json; charset=utf-8"
        }

    def _make_request(self, service: str, method: str, params: Dict) -> Dict:
        """
        Выполнить запрос к API

        Args:
            service: Название сервиса (campaigns, adgroups, ads, etc.)
            method: Метод API (get, add, update, delete)
            params: Параметры запроса

        Returns:
            Ответ от API
        """
        url = f"{self.api_url}{service}"

        payload = {
            "method": method,
            "params": params
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "failed"}

    # ===== CAMPAIGNS (Кампании) =====

    def get_campaigns(self, campaign_ids: Optional[List[int]] = None) -> List[Dict]:
        """
        Получить список кампаний

        Args:
            campaign_ids: Список ID кампаний (если None - все кампании)

        Returns:
            Список кампаний с параметрами
        """
        params = {
            "SelectionCriteria": {},
            "FieldNames": [
                "Id", "Name", "Status", "State", "StatusPayment",
                "StatusClarification", "StartDate", "EndDate",
                "DailyBudget", "Currency", "Funds"
            ]
        }

        if campaign_ids:
            params["SelectionCriteria"]["Ids"] = campaign_ids

        response = self._make_request("campaigns", "get", params)

        if "result" in response:
            return response["result"].get("Campaigns", [])
        else:
            print(f"Error getting campaigns: {response.get('error')}")
            return []

    def get_campaign_stats(self, campaign_id: int, date_from: str, date_to: str) -> Dict:
        """
        Получить статистику по кампании

        Args:
            campaign_id: ID кампании
            date_from: Дата начала (YYYY-MM-DD)
            date_to: Дата окончания (YYYY-MM-DD)

        Returns:
            Статистика кампании
        """
        # Используем метод Reports для получения статистики
        return self.get_report(
            campaign_ids=[campaign_id],
            date_from=date_from,
            date_to=date_to
        )

    # ===== AD GROUPS (Группы объявлений) =====

    def get_adgroups(self, campaign_ids: Optional[List[int]] = None) -> List[Dict]:
        """
        Получить группы объявлений

        Args:
            campaign_ids: Список ID кампаний

        Returns:
            Список групп объявлений
        """
        params = {
            "SelectionCriteria": {},
            "FieldNames": [
                "Id", "Name", "CampaignId", "Status", "Type",
                "Subtype", "TrackingParams"
            ]
        }

        if campaign_ids:
            params["SelectionCriteria"]["CampaignIds"] = campaign_ids

        response = self._make_request("adgroups", "get", params)

        if "result" in response:
            return response["result"].get("AdGroups", [])
        else:
            print(f"Error getting ad groups: {response.get('error')}")
            return []

    # ===== REPORTS (Отчёты) =====

    def get_report(
        self,
        campaign_ids: Optional[List[int]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict:
        """
        Получить отчёт по статистике

        Args:
            campaign_ids: Список ID кампаний
            date_from: Дата начала (YYYY-MM-DD)
            date_to: Дата окончания (YYYY-MM-DD)
            fields: Поля для выгрузки

        Returns:
            Отчёт с данными
        """
        # Если даты не указаны - последние 30 дней
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not date_to:
            date_to = datetime.now().strftime("%Y-%m-%d")

        # Поля по умолчанию
        if not fields:
            fields = [
                "CampaignId", "CampaignName", "Date",
                "Impressions", "Clicks", "Cost", "Ctr",
                "AvgCpc", "Conversions", "ConversionRate", "CostPerConversion"
            ]

        params = {
            "SelectionCriteria": {
                "DateFrom": date_from,
                "DateTo": date_to
            },
            "FieldNames": fields,
            "ReportName": f"Report_{date_from}_{date_to}",
            "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
            "DateRangeType": "CUSTOM_DATE",
            "Format": "TSV",
            "IncludeVAT": "YES",
            "IncludeDiscount": "NO"
        }

        if campaign_ids:
            params["SelectionCriteria"]["Filter"] = [
                {
                    "Field": "CampaignId",
                    "Operator": "IN",
                    "Values": campaign_ids
                }
            ]

        # Reports endpoint отличается
        headers = self.headers.copy()
        headers["skipReportHeader"] = "true"
        headers["skipReportSummary"] = "true"

        try:
            response = requests.post(
                self.reports_url,
                headers=headers,
                json=params,
                timeout=120
            )

            if response.status_code == 200:
                # Парсим TSV ответ
                lines = response.text.strip().split('\n')
                if len(lines) < 2:
                    return {"data": [], "total": 0}

                # Первая строка - заголовки
                headers_line = lines[0].split('\t')

                # Парсим данные
                data = []
                for line in lines[1:]:
                    values = line.split('\t')
                    row = dict(zip(headers_line, values))
                    data.append(row)

                return {
                    "data": data,
                    "total": len(data),
                    "date_from": date_from,
                    "date_to": date_to
                }
            else:
                return {
                    "error": f"Status {response.status_code}",
                    "message": response.text
                }
        except Exception as e:
            return {"error": str(e)}

    # ===== ANALYTICS (Аналитика) =====

    def get_dashboard_stats(self, campaign_ids: Optional[List[int]] = None) -> Dict:
        """
        Получить общую статистику для дашборда

        Returns:
            Словарь с агрегированной статистикой
        """
        # Последние 30 дней
        date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d")

        report = self.get_report(campaign_ids, date_from, date_to)

        if "error" in report or not report.get("data"):
            return {
                "total_impressions": 0,
                "total_clicks": 0,
                "total_cost": 0,
                "avg_ctr": 0,
                "avg_cpc": 0,
                "total_conversions": 0,
                "conversion_rate": 0,
                "campaigns_count": 0
            }

        data = report["data"]

        # Агрегируем данные
        total_impressions = sum(int(row.get("Impressions", 0)) for row in data)
        total_clicks = sum(int(row.get("Clicks", 0)) for row in data)
        total_cost = sum(float(row.get("Cost", 0)) for row in data)
        total_conversions = sum(int(row.get("Conversions", 0)) for row in data)

        # Средние показатели
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0

        # Уникальные кампании
        campaigns = set(row.get("CampaignId") for row in data)

        return {
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_cost": round(total_cost, 2),
            "avg_ctr": round(avg_ctr, 2),
            "avg_cpc": round(avg_cpc, 2),
            "total_conversions": total_conversions,
            "conversion_rate": round(conversion_rate, 2),
            "campaigns_count": len(campaigns),
            "period": f"{date_from} — {date_to}"
        }

    # ===== EXPORT (Экспорт) =====

    def export_to_csv(self, campaign_ids: Optional[List[int]] = None, filename: str = "yandex_direct_report.csv") -> str:
        """
        Экспортировать отчёт в CSV

        Args:
            campaign_ids: Список ID кампаний
            filename: Имя файла для сохранения

        Returns:
            Путь к сохранённому файлу
        """
        report = self.get_report(campaign_ids)

        if "error" in report or not report.get("data"):
            return None

        import csv

        data = report["data"]

        # Сохраняем в CSV
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

        return filename


# ===== EXAMPLE USAGE =====

if __name__ == "__main__":
    # Пример использования

    # Получи токен и логин из переменных окружения или конфига
    # ВАЖНО: Замени на свои значения!
    ACCESS_TOKEN = os.getenv("YANDEX_DIRECT_TOKEN", "YOUR_TOKEN_HERE")  # <-- Вставь сюда токен из браузера
    LOGIN = os.getenv("YANDEX_DIRECT_LOGIN", "your-login")  # <-- Вставь свой логин Яндекса

    # Создаём клиент (is_sandbox=True для тестирования)
    client = YandexDirectAPI(
        access_token=ACCESS_TOKEN,
        login=LOGIN,
        is_sandbox=False  # Поставь True для sandbox режима
    )

    # Получаем список кампаний
    print("=== Получаем кампании ===")
    campaigns = client.get_campaigns()
    print(f"Найдено кампаний: {len(campaigns)}")

    for campaign in campaigns[:3]:  # Первые 3
        print(f"- {campaign['Name']} (ID: {campaign['Id']}) - {campaign['Status']}")

    # Получаем общую статистику
    print("\n=== Получаем статистику ===")
    stats = client.get_dashboard_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    # Экспортируем отчёт
    print("\n=== Экспортируем отчёт ===")
    csv_file = client.export_to_csv()
    if csv_file:
        print(f"Отчёт сохранён: {csv_file}")
    else:
        print("Ошибка при экспорте")
