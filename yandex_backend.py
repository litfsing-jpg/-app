"""
FastAPI Backend for Yandex Direct Integration
Provides REST API endpoints for the dashboard
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from yandex_direct_api import YandexDirectAPI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Yandex Direct API Backend",
    description="REST API for Yandex Direct integration",
    version="1.0.0"
)

# CORS configuration - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Yandex Direct client
ACCESS_TOKEN = os.getenv("YANDEX_DIRECT_TOKEN")
LOGIN = os.getenv("YANDEX_DIRECT_LOGIN")

if not ACCESS_TOKEN or not LOGIN:
    raise ValueError("YANDEX_DIRECT_TOKEN and YANDEX_DIRECT_LOGIN must be set in .env file")

client = YandexDirectAPI(
    access_token=ACCESS_TOKEN,
    login=LOGIN,
    is_sandbox=False
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Yandex Direct API Backend",
        "version": "1.0.0"
    }


@app.get("/api/yandex-direct/stats")
async def get_stats():
    """
    Get dashboard statistics
    Returns aggregated stats for the last 30 days
    """
    try:
        stats = client.get_dashboard_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/yandex-direct/campaigns")
async def get_campaigns():
    """
    Get list of campaigns
    """
    try:
        campaigns = client.get_campaigns()
        return {"campaigns": campaigns, "total": len(campaigns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/yandex-direct/campaigns/{campaign_id}")
async def get_campaign(campaign_id: int):
    """
    Get specific campaign by ID
    """
    try:
        campaigns = client.get_campaigns(campaign_ids=[campaign_id])
        if not campaigns:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return campaigns[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/yandex-direct/report")
async def get_report(days: int = 30):
    """
    Get performance report

    Args:
        days: Number of days to include in report (default: 30)
    """
    try:
        from datetime import datetime, timedelta

        date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d")

        report = client.get_report(date_from=date_from, date_to=date_to)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/yandex-direct/export")
async def export_report(days: int = 30):
    """
    Export report to CSV

    Args:
        days: Number of days to include in report (default: 30)
    """
    try:
        from fastapi.responses import FileResponse

        filename = client.export_to_csv()

        if not filename:
            raise HTTPException(status_code=500, detail="Failed to export report")

        return FileResponse(
            filename,
            media_type="text/csv",
            filename="yandex_direct_report.csv"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/yandex-direct/adgroups")
async def get_adgroups(campaign_id: int = None):
    """
    Get ad groups

    Args:
        campaign_id: Filter by campaign ID (optional)
    """
    try:
        campaign_ids = [campaign_id] if campaign_id else None
        adgroups = client.get_adgroups(campaign_ids=campaign_ids)
        return {"adgroups": adgroups, "total": len(adgroups)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Yandex Direct API Backend...")
    print(f"📊 Login: {LOGIN}")
    print(f"🔑 Token: {ACCESS_TOKEN[:20]}...")
    print(f"🌐 Server: http://localhost:8000")
    print(f"📖 Docs: http://localhost:8000/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
