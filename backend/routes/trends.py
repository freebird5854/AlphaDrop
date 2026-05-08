"""Google Trends + Amazon demand estimation — cross-platform intelligence."""
from fastapi import APIRouter, Request, Query, HTTPException
from typing import Optional
import random
import asyncio
from datetime import datetime, timezone

router = APIRouter(prefix="/api/trends", tags=["trends"])


async def _fetch_google_trends(keyword: str) -> dict:
    """Fetch Google Trends data for a keyword using pytrends."""
    try:
        from pytrends.request import TrendReq

        def _sync_fetch():
            pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
            pytrends.build_payload([keyword], cat=0, timeframe='today 3-m')
            interest = pytrends.interest_over_time()
            if interest.empty:
                return None
            # Get the series for the keyword
            values = interest[keyword].tolist()
            dates = [d.strftime("%Y-%m-%d") for d in interest.index]
            return {
                "keyword": keyword,
                "trend_data": [{"date": d, "interest": v} for d, v in zip(dates, values)],
                "current_interest": values[-1] if values else 0,
                "peak_interest": max(values) if values else 0,
                "avg_interest": round(sum(values) / len(values), 1) if values else 0,
                "trend_direction": "up" if len(values) > 1 and values[-1] > values[-2] else "down",
            }

        return await asyncio.to_thread(_sync_fetch)
    except Exception as e:
        return {"keyword": keyword, "error": str(e), "trend_data": [], "current_interest": 0}


def _estimate_amazon_demand(keyword: str, category: str, price: float, tiktok_score: int) -> dict:
    """Estimate Amazon demand based on category, price point, and TikTok signals."""
    # Category demand multipliers (based on typical Amazon category competition)
    cat_multipliers = {
        "Beauty & Skincare": 0.85, "Home & Kitchen": 0.90, "Tech Gadgets": 0.75,
        "Health & Wellness": 0.80, "Fashion Accessories": 0.70, "Pet Products": 0.65,
        "Fitness Equipment": 0.75, "Baby Products": 0.80, "Outdoor & Travel": 0.70,
        "Food & Beverages": 0.60, "Jewelry": 0.55, "Car Accessories": 0.50,
    }
    cat_mult = cat_multipliers.get(category, 0.6)

    # Price sweet spot (Amazon buyers prefer $15-$50 range)
    if 15 <= price <= 50:
        price_mult = 1.0
    elif 10 <= price <= 70:
        price_mult = 0.8
    else:
        price_mult = 0.5

    # TikTok virality signals translate to Amazon search volume
    tiktok_mult = min(tiktok_score / 100, 1.0)

    base_score = 50
    demand_score = int(base_score * cat_mult * price_mult + tiktok_mult * 40)
    demand_score = min(max(demand_score, 5), 99)

    # Estimate competition level
    competition = "Low" if demand_score > 70 and cat_mult < 0.7 else "Medium" if demand_score > 50 else "High"

    # Estimate monthly search volume range
    search_vol_base = demand_score * random.randint(80, 200)

    return {
        "keyword": keyword,
        "demand_score": demand_score,
        "estimated_monthly_searches": f"{search_vol_base:,}-{search_vol_base * 2:,}",
        "competition_level": competition,
        "price_competitiveness": "Sweet Spot" if price_mult == 1.0 else "Acceptable" if price_mult == 0.8 else "Outside Range",
        "category_strength": f"{int(cat_mult * 100)}%",
        "recommendation": "Strong opportunity" if demand_score > 70 else "Worth testing" if demand_score > 45 else "Proceed with caution",
    }


@router.get("/google/{keyword}")
async def get_google_trends(keyword: str, request: Request):
    """Get Google Trends data for a keyword — requires subscription."""
    from server import require_subscription
    await require_subscription(request)
    result = await _fetch_google_trends(keyword)
    return result


@router.get("/amazon/estimate")
async def get_amazon_estimate(
    request: Request,
    keyword: str = Query(...),
    category: str = Query(""),
    price: float = Query(0),
    tiktok_score: int = Query(50),
):
    """Estimate Amazon demand — requires subscription."""
    from server import require_subscription
    await require_subscription(request)
    return _estimate_amazon_demand(keyword, category, price, tiktok_score)


@router.get("/product/{product_id}")
async def get_product_trends(product_id: str, request: Request):
    """Get combined Google Trends + Amazon estimate for a product — requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)

    product = await db.products.find_one({"id": product_id}, {"_id": 0, "name": 1, "category": 1, "price": 1, "alpha_score": 1})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Extract a good keyword from product name (first 2-3 words)
    name_words = product["name"].split()[:3]
    keyword = " ".join(name_words)

    google_data = await _fetch_google_trends(keyword)
    amazon_data = _estimate_amazon_demand(
        keyword, product.get("category", ""), product.get("price", 0), product.get("alpha_score", 50)
    )

    return {
        "product_id": product_id,
        "product_name": product["name"],
        "google_trends": google_data,
        "amazon_estimate": amazon_data,
    }
