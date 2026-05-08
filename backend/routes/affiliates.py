"""TikTok Affiliates system — creators by niche with contact info and commission data."""
from fastapi import APIRouter, Request, Query, HTTPException
from typing import Optional, List
import uuid
import random
from datetime import datetime, timezone

router = APIRouter(prefix="/api/affiliates", tags=["affiliates"])

# Niche categories
NICHES = [
    "Beauty & Skincare", "Tech & Gadgets", "Health & Wellness",
    "Fashion & Lifestyle", "Home & Kitchen", "Fitness & Sports",
    "Mom & Baby", "Pet Products", "Food & Cooking", "Jewelry & Accessories",
]

CREATOR_FIRST = ["Emma", "Sophia", "Liam", "Noah", "Olivia", "Ava", "Mia", "Ella", "Zoe", "Lily",
                  "Mason", "Ethan", "Lucas", "James", "Alex", "Chloe", "Riley", "Taylor", "Jordan", "Morgan"]
CREATOR_LAST = ["Shop", "Reviews", "Finds", "Daily", "Picks", "Unboxed", "Hauls", "Style", "Living", "Vibes"]


def _generate_affiliates(db_ref=None):
    """Generate realistic affiliate creator data."""
    creators = []
    for i in range(80):
        niche = random.choice(NICHES)
        handle = f"@{random.choice(CREATOR_FIRST).lower()}{random.choice(CREATOR_LAST).lower()}{random.randint(1,999)}"
        followers = random.randint(5000, 2000000)
        avg_views = int(followers * random.uniform(0.02, 0.15))
        engagement = round(random.uniform(1.5, 12.0), 1)
        creators.append({
            "id": str(uuid.uuid4()),
            "handle": handle,
            "name": f"{random.choice(CREATOR_FIRST)} {random.choice(CREATOR_LAST)}",
            "niche": niche,
            "secondary_niche": random.choice([n for n in NICHES if n != niche]) if random.random() > 0.5 else None,
            "followers": followers,
            "avg_views": avg_views,
            "engagement_rate": engagement,
            "commission_range": f"{random.randint(5,15)}%-{random.randint(16,30)}%",
            "avg_commission": round(random.uniform(8, 25), 1),
            "products_promoted": random.randint(3, 120),
            "total_sales_driven": random.randint(500, 500000),
            "contact_email": f"{handle[1:].replace(' ','')}@creator.com",
            "contact_method": random.choice(["Email", "TikTok DM", "Instagram DM", "Agency"]),
            "agency": random.choice([None, None, None, "Viral Nation", "Gleam Futures", "Select Management", "The Influencer Agency"]),
            "status": random.choice(["Active", "Active", "Active", "Selective", "Exclusive"]),
            "top_categories": [niche] + ([random.choice(NICHES)] if random.random() > 0.4 else []),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "response_time": random.choice(["< 24h", "1-3 days", "3-7 days", "Varies"]),
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    return creators


async def _ensure_affiliates(db):
    count = await db.affiliates.count_documents({})
    if count < 10:
        affiliates = _generate_affiliates()
        await db.affiliates.insert_many(affiliates)
    return await db.affiliates.count_documents({})


@router.get("")
async def get_affiliates(
    request: Request,
    niche: Optional[str] = Query(None),
    min_followers: Optional[int] = Query(None),
    max_followers: Optional[int] = Query(None),
    min_engagement: Optional[float] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("followers"),
    limit: int = Query(50, ge=1, le=100),
):
    """List affiliates with filters — requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)
    await _ensure_affiliates(db)

    query = {}
    if niche:
        query["niche"] = niche
    if min_followers:
        query["followers"] = {"$gte": min_followers}
    if max_followers:
        query.setdefault("followers", {})["$lte"] = max_followers
    if min_engagement:
        query["engagement_rate"] = {"$gte": min_engagement}
    if status:
        query["status"] = status
    if search:
        query["$or"] = [
            {"handle": {"$regex": search, "$options": "i"}},
            {"name": {"$regex": search, "$options": "i"}},
        ]

    sort_field = {"followers": -1, "engagement_rate": -1, "avg_commission": -1, "rating": -1}.get(sort_by, -1)
    affiliates = await db.affiliates.find(query, {"_id": 0}).sort(sort_by, sort_field).limit(limit).to_list(limit)

    # Get niche stats
    niche_pipeline = [
        {"$group": {"_id": "$niche", "count": {"$sum": 1}, "avg_engagement": {"$avg": "$engagement_rate"}}},
        {"$sort": {"count": -1}}
    ]
    niche_stats = await db.affiliates.aggregate(niche_pipeline).to_list(20)

    return {
        "affiliates": affiliates,
        "total": await db.affiliates.count_documents(query),
        "niche_stats": [{"niche": n["_id"], "count": n["count"], "avg_engagement": round(n["avg_engagement"], 1)} for n in niche_stats],
        "niches": NICHES,
    }


@router.get("/{affiliate_id}")
async def get_affiliate_detail(affiliate_id: str, request: Request):
    """Get detailed affiliate profile — requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)
    affiliate = await db.affiliates.find_one({"id": affiliate_id}, {"_id": 0})
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    return affiliate


@router.get("/niches/summary")
async def get_niche_summary(request: Request):
    """Get summary of affiliates by niche — requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)
    await _ensure_affiliates(db)

    pipeline = [
        {"$group": {
            "_id": "$niche",
            "count": {"$sum": 1},
            "avg_followers": {"$avg": "$followers"},
            "avg_engagement": {"$avg": "$engagement_rate"},
            "avg_commission": {"$avg": "$avg_commission"},
            "total_sales": {"$sum": "$total_sales_driven"},
        }},
        {"$sort": {"count": -1}}
    ]
    niches = await db.affiliates.aggregate(pipeline).to_list(20)
    return {
        "niches": [{
            "niche": n["_id"],
            "creator_count": n["count"],
            "avg_followers": int(n["avg_followers"]),
            "avg_engagement": round(n["avg_engagement"], 1),
            "avg_commission": round(n["avg_commission"], 1),
            "total_sales_driven": n["total_sales"],
        } for n in niches]
    }
