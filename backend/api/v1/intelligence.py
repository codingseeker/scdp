"""
api/v1/intelligence.py — External intelligence API.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from core.security import get_optional_user

router = APIRouter(prefix="/intelligence", tags=["Intelligence"])


@router.get("/news")
async def get_news_intelligence(user=Depends(get_optional_user)):
    from integrations.news import fetch_news
    news = await fetch_news("supply chain disruption", max_results=10)
    return {"news": news, "total": len(news)}


@router.get("/weather")
async def get_weather_intelligence(user=Depends(get_optional_user)):
    from integrations.weather import fetch_weather_alerts
    alerts = await fetch_weather_alerts(0, 0)
    return {"alerts": alerts, "total": len(alerts)}