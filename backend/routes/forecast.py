"""Time-series sales forecasting — predict product performance 7/14/30 days out."""
from fastapi import APIRouter, Request, Query, HTTPException
from typing import Optional
import random
import math
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/api/forecast", tags=["forecast"])


def _forecast_series(trend_data: list, days_ahead: int = 14) -> list:
    """Generate time-series forecast based on historical trend data."""
    if not trend_data or len(trend_data) < 3:
        return []

    # Extract sales series
    sales = [d.get("sales", d) if isinstance(d, dict) else d for d in trend_data]

    # Calculate growth rate using exponential moving average
    recent = sales[-7:] if len(sales) >= 7 else sales
    if len(recent) < 2:
        return []

    # Daily growth rates
    growth_rates = []
    for i in range(1, len(recent)):
        if recent[i - 1] > 0:
            growth_rates.append(recent[i] / recent[i - 1])

    if not growth_rates:
        return []

    # Weighted average growth (recent days weighted more)
    weights = [i + 1 for i in range(len(growth_rates))]
    avg_growth = sum(g * w for g, w in zip(growth_rates, weights)) / sum(weights)

    # Decay factor: growth slows over time (mean reversion)
    decay = 0.97

    # Generate forecast
    forecast = []
    last_value = sales[-1]
    last_date = datetime.now(timezone.utc)

    for day in range(1, days_ahead + 1):
        # Apply decaying growth + noise
        daily_growth = 1 + (avg_growth - 1) * (decay ** day)
        noise = random.uniform(0.92, 1.08)
        predicted = int(last_value * daily_growth * noise)
        predicted = max(0, predicted)

        forecast.append({
            "date": (last_date + timedelta(days=day)).strftime("%Y-%m-%d"),
            "predicted_sales": predicted,
            "confidence_low": int(predicted * random.uniform(0.7, 0.85)),
            "confidence_high": int(predicted * random.uniform(1.15, 1.35)),
            "day": day,
        })
        last_value = predicted

    return forecast


def _calculate_forecast_metrics(trend_data: list, forecast: list) -> dict:
    """Calculate key forecast metrics."""
    if not forecast:
        return {}

    sales = [d.get("sales", 0) if isinstance(d, dict) else 0 for d in trend_data]
    current_daily = sales[-1] if sales else 0
    week_avg = sum(sales[-7:]) / min(7, len(sales)) if sales else 0

    forecast_7d = sum(f["predicted_sales"] for f in forecast[:7])
    forecast_14d = sum(f["predicted_sales"] for f in forecast[:14])
    forecast_30d = sum(f["predicted_sales"] for f in forecast[:30])

    peak_day = max(forecast, key=lambda x: x["predicted_sales"]) if forecast else {}
    growth_7d = ((forecast[6]["predicted_sales"] / max(current_daily, 1)) - 1) * 100 if len(forecast) >= 7 else 0

    # Viral probability based on growth trajectory
    if growth_7d > 200:
        viral_prob = "Very High (>80%)"
    elif growth_7d > 100:
        viral_prob = "High (60-80%)"
    elif growth_7d > 50:
        viral_prob = "Moderate (30-60%)"
    elif growth_7d > 0:
        viral_prob = "Low (10-30%)"
    else:
        viral_prob = "Declining (<10%)"

    return {
        "current_daily_sales": current_daily,
        "7d_avg_sales": round(week_avg),
        "forecast_7d_total": forecast_7d,
        "forecast_14d_total": forecast_14d,
        "forecast_30d_total": forecast_30d,
        "projected_growth_7d": f"{growth_7d:+.0f}%",
        "peak_forecast_day": peak_day.get("date", ""),
        "peak_forecast_sales": peak_day.get("predicted_sales", 0),
        "viral_probability": viral_prob,
    }


@router.get("/product/{product_id}")
async def get_product_forecast(
    product_id: str,
    request: Request,
    days: int = Query(14, ge=7, le=30),
):
    """Get sales forecast for a product — requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)

    product = await db.products.find_one(
        {"id": product_id},
        {"_id": 0, "id": 1, "name": 1, "status": 1, "alpha_score": 1, "trend_data": 1,
         "momentum_multiplier": 1, "saturation_countdown": 1, "total_sales": 1}
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    trend_data = product.get("trend_data", [])
    forecast = _forecast_series(trend_data, days)
    metrics = _calculate_forecast_metrics(trend_data, forecast)

    return {
        "product_id": product_id,
        "product_name": product["name"],
        "status": product["status"],
        "alpha_score": product["alpha_score"],
        "momentum_multiplier": product.get("momentum_multiplier", 1.0),
        "saturation_countdown": product.get("saturation_countdown", -1),
        "forecast": forecast,
        "metrics": metrics,
        "historical": trend_data,
    }


@router.get("/top-forecasts")
async def get_top_forecasts(request: Request, limit: int = Query(10)):
    """Get products with highest forecast growth — requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)

    products = await db.products.find(
        {"status": {"$in": ["EXPLOSIVE", "SCALING_NOW", "EXPLODING_SOON", "RISING"]}},
        {"_id": 0, "id": 1, "name": 1, "status": 1, "alpha_score": 1, "trend_data": 1, "momentum_multiplier": 1, "category": 1}
    ).sort("alpha_score", -1).limit(limit).to_list(limit)

    forecasts = []
    for p in products:
        forecast = _forecast_series(p.get("trend_data", []), 7)
        metrics = _calculate_forecast_metrics(p.get("trend_data", []), forecast)
        forecasts.append({
            "product_id": p["id"],
            "product_name": p["name"],
            "status": p["status"],
            "alpha_score": p["alpha_score"],
            "category": p.get("category", ""),
            "momentum": p.get("momentum_multiplier", 1.0),
            "forecast_7d": metrics.get("forecast_7d_total", 0),
            "growth_7d": metrics.get("projected_growth_7d", "0%"),
            "viral_probability": metrics.get("viral_probability", ""),
        })

    forecasts.sort(key=lambda x: x["forecast_7d"], reverse=True)
    return {"forecasts": forecasts}
