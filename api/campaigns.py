"""
Vercel Serverless Function: Get Yandex Direct Campaigns
"""
import os
import json
import requests
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request for campaigns list"""
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

            # Make request to Yandex Direct API
            url = "https://api.direct.yandex.com/json/v5/campaigns"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Client-Login": login,
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

            response = requests.post(url, headers=headers, json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                campaigns = data.get("result", {}).get("Campaigns", [])

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "campaigns": campaigns
                }).encode())
            else:
                self.send_response(response.status_code)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": f"Yandex API error: {response.status_code}",
                    "details": response.text
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
