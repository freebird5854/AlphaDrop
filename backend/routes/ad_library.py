"""Ad Creative Library — track TikTok ad creatives linked to products."""
from fastapi import APIRouter, Request, Query, HTTPException
from typing import Optional
import uuid
import random
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/api/ads", tags=["ad_library"])

# Simulated ad creative data
AD_FORMATS = ["UGC Review", "Before/After", "POV Unboxing", "Tutorial", "Green Screen", "Voiceover B-Roll", "Duet/Stitch", "Lifestyle"]
AD_HOOKS = [
    "Stop scrolling! This changed my life...",
    "I can't believe no one talks about this",
    "POV: You finally found the product that actually works",
    "Day 1 vs Day 30 using this...",
    "TikTok made me buy it and I'm NOT mad",
    "Run don't walk to get this before it sells out",
    "The #1 product I recommend to everyone",
    "Unpopular opinion: this is better than the expensive version",
    "Why is nobody talking about this??",
    "I've been using this for 3 months and here's my honest review",
]
ADVERTISERS = [f"@shop_{random.randint(100,9999)}" for _ in range(50)]


def _generate_ad_creatives(product_name: str, category: str, count: int = 10):
    """Generate realistic ad creative data for a product."""
    creatives = []
    for _ in range(count):
        days_ago = random.randint(1, 30)
        run_days = random.randint(3, 21)
        views = random.randint(10000, 5000000)
        creatives.append({
            "id": str(uuid.uuid4())[:12],
            "product_name": product_name,
            "category": category,
            "advertiser": random.choice(ADVERTISERS),
            "format": random.choice(AD_FORMATS),
            "hook_text": random.choice(AD_HOOKS),
            "duration_seconds": random.choice([15, 20, 30, 45, 60]),
            "views": views,
            "likes": int(views * random.uniform(0.02, 0.12)),
            "comments": int(views * random.uniform(0.001, 0.02)),
            "shares": int(views * random.uniform(0.005, 0.03)),
            "ctr_estimate": round(random.uniform(0.8, 4.5), 2),
            "spend_estimate": random.randint(100, 15000),
            "first_seen": (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "running_days": run_days,
            "still_active": run_days < 14 and random.random() > 0.3,
            "duplication_count": random.randint(0, 25),
            "platform": "TikTok",
        })
    return creatives


async def _ensure_ad_library(db):
    """Seed ad library if empty."""
    count = await db.ad_creatives.count_documents({})
    if count < 50:
        from server import db as main_db
        products = await main_db.products.find(
            {"status": {"$in": ["EXPLOSIVE", "SCALING_NOW", "RISING", "EXPLODING_SOON"]}},
            {"_id": 0, "id": 1, "name": 1, "category": 1}
        ).limit(30).to_list(30)

        all_ads = []
        for p in products:
            ads = _generate_ad_creatives(p["name"], p["category"], random.randint(3, 8))
            for ad in ads:
                ad["product_id"] = p["id"]
            all_ads.extend(ads)

        if all_ads:
            await db.ad_creatives.insert_many(all_ads)
    return await db.ad_creatives.count_documents({})


@router.get("")
async def get_ad_library(
    request: Request,
    product_id: Optional[str] = Query(None),
    format_type: Optional[str] = Query(None),
    min_views: Optional[int] = Query(None),
    still_active: Optional[bool] = Query(None),
    sort_by: str = Query("views"),
    limit: int = Query(50, ge=1, le=100),
):
    """Browse ad creatives — requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)
    await _ensure_ad_library(db)

    query = {}
    if product_id:
        query["product_id"] = product_id
    if format_type:
        query["format"] = format_type
    if min_views:
        query["views"] = {"$gte": min_views}
    if still_active is not None:
        query["still_active"] = still_active

    sort_dir = -1
    ads = await db.ad_creatives.find(query, {"_id": 0}).sort(sort_by, sort_dir).limit(limit).to_list(limit)

    # Get format breakdown
    format_pipeline = [
        {"$group": {"_id": "$format", "count": {"$sum": 1}, "avg_views": {"$avg": "$views"}}},
        {"$sort": {"count": -1}}
    ]
    format_stats = await db.ad_creatives.aggregate(format_pipeline).to_list(20)

    return {
        "ads": ads,
        "total": await db.ad_creatives.count_documents(query),
        "formats": AD_FORMATS,
        "format_stats": [{"format": f["_id"], "count": f["count"], "avg_views": int(f["avg_views"])} for f in format_stats],
    }


@router.get("/top-hooks")
async def get_top_hooks(request: Request, limit: int = Query(20)):
    """Get top-performing ad hooks ranked by engagement — requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)
    await _ensure_ad_library(db)

    pipeline = [
        {"$group": {
            "_id": "$hook_text",
            "total_views": {"$sum": "$views"},
            "total_likes": {"$sum": "$likes"},
            "avg_ctr": {"$avg": "$ctr_estimate"},
            "usage_count": {"$sum": 1},
        }},
        {"$sort": {"total_views": -1}},
        {"$limit": limit}
    ]
    hooks = await db.ad_creatives.aggregate(pipeline).to_list(limit)

    return {
        "top_hooks": [{
            "hook": h["_id"],
            "total_views": h["total_views"],
            "total_likes": h["total_likes"],
            "avg_ctr": round(h["avg_ctr"], 2),
            "times_used": h["usage_count"],
        } for h in hooks]
    }


@router.get("/duplication-alerts")
async def get_duplication_alerts(request: Request):
    """Get products with highest ad duplication (saturation signal) — requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)
    await _ensure_ad_library(db)

    pipeline = [
        {"$group": {
            "_id": "$product_id",
            "product_name": {"$first": "$product_name"},
            "total_ads": {"$sum": 1},
            "total_advertisers": {"$addToSet": "$advertiser"},
            "max_duplication": {"$max": "$duplication_count"},
        }},
        {"$addFields": {"unique_advertisers": {"$size": "$total_advertisers"}}},
        {"$sort": {"unique_advertisers": -1}},
        {"$limit": 15}
    ]
    results = await db.ad_creatives.aggregate(pipeline).to_list(15)

    return {
        "duplication_alerts": [{
            "product_id": r["_id"],
            "product_name": r["product_name"],
            "total_ads": r["total_ads"],
            "unique_advertisers": r["unique_advertisers"],
            "max_duplication": r["max_duplication"],
            "saturation_signal": "HIGH" if r["unique_advertisers"] > 10 else "MEDIUM" if r["unique_advertisers"] > 5 else "LOW",
        } for r in results]
    }
