"""
Vercel Serverless Function: Get Yandex Direct Statistics
"""
import os
import json
import requests
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request for dashboard statistics"""
        try:
            # Get credentials from environment variables
            access_token = os.getenv("YANDEX_DIRECT_TOKEN")
            login = os.getenv("YANDEX_DIRECT_LOGIN")

            if not access_token or not login:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "Missing credentials"
                }).encode())
                return

            # First, get campaigns list
            campaigns_url = "https://api.direct.yandex.com/json/v5/campaigns"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Client-Login": login,
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

            campaigns_response = requests.post(
                campaigns_url,
                headers=headers,
                json=campaigns_payload,
                timeout=10
            )

            if campaigns_response.status_code != 200:
                raise Exception(f"Failed to get campaigns: {campaigns_response.text}")

            campaigns_data = campaigns_response.json()
            campaigns = campaigns_data.get("result", {}).get("Campaigns", [])
            campaign_ids = [str(c["Id"]) for c in campaigns]

            # Now get reports for these campaigns
            report_url = "https://api.direct.yandex.com/json/v5/reports"

            # Calculate date range (last 30 days)
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            report_payload = {
                "params": {
                    "SelectionCriteria": {
                        "DateFrom": start_date,
                        "DateTo": end_date,
                        "Filter": [
                            {
                                "Field": "CampaignId",
                                "Operator": "IN",
                                "Values": campaign_ids if campaign_ids else ["0"]
                            }
                        ]
                    },
                    "FieldNames": [
                        "CampaignId",
                        "CampaignName",
                        "Impressions",
                        "Clicks",
                        "Cost",
                        "Conversions",
                        "Ctr"
                    ],
                    "ReportName": "Dashboard Stats Report",
                    "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
                    "DateRangeType": "CUSTOM_DATE",
                    "Format": "TSV",
                    "IncludeVAT": "YES",
                    "IncludeDiscount": "YES"
                }
            }

            report_response = requests.post(
                report_url,
                headers=headers,
                json=report_payload,
                timeout=30
            )

            # Parse TSV response
            total_stats = {
                "total_impressions": 0,
                "total_clicks": 0,
                "total_cost": 0,
                "total_conversions": 0,
                "campaigns_count": len(campaigns),
                "campaigns": []
            }

            if report_response.status_code == 200:
                # Parse TSV data
                lines = report_response.text.strip().split('\n')

                # Skip header rows and parse data
                for line in lines[1:]:  # Skip header
                    if line and not line.startswith('#'):
                        parts = line.split('\t')
                        if len(parts) >= 7:
                            try:
                                campaign_id = parts[0]
                                campaign_name = parts[1]
                                impressions = int(parts[2]) if parts[2] != '--' else 0
                                clicks = int(parts[3]) if parts[3] != '--' else 0
                                cost = float(parts[4]) / 1000000 if parts[4] != '--' else 0  # Convert micros to rubles
                                conversions = int(parts[5]) if parts[5] != '--' else 0
                                ctr = float(parts[6]) if parts[6] != '--' else 0

                                total_stats["total_impressions"] += impressions
                                total_stats["total_clicks"] += clicks
                                total_stats["total_cost"] += cost
                                total_stats["total_conversions"] += conversions

                                total_stats["campaigns"].append({
                                    "id": campaign_id,
                                    "name": campaign_name,
                                    "impressions": impressions,
                                    "clicks": clicks,
                                    "cost": round(cost, 2),
                                    "ctr": round(ctr, 2),
                                    "conversions": conversions
                                })
                            except (ValueError, IndexError):
                                continue

            # Calculate averages
            if total_stats["total_impressions"] > 0:
                total_stats["avg_ctr"] = round(
                    (total_stats["total_clicks"] / total_stats["total_impressions"]) * 100, 2
                )
            else:
                total_stats["avg_ctr"] = 0

            if total_stats["total_clicks"] > 0:
                total_stats["avg_cpc"] = round(
                    total_stats["total_cost"] / total_stats["total_clicks"], 2
                )
            else:
                total_stats["avg_cpc"] = 0

            if total_stats["total_clicks"] > 0:
                total_stats["conversion_rate"] = round(
                    (total_stats["total_conversions"] / total_stats["total_clicks"]) * 100, 2
                )
            else:
                total_stats["conversion_rate"] = 0

            # Round total cost
            total_stats["total_cost"] = round(total_stats["total_cost"], 2)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "stats": total_stats
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": str(e)
            }).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight request"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
