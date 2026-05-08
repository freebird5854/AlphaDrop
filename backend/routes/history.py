"""Historical data tracking — daily snapshots and trend over time."""
from fastapi import APIRouter, Request, Query
from typing import Optional
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/snapshots")
async def get_history_snapshots(request: Request, days: int = Query(30, ge=1, le=180)):
    """Get daily product count snapshots — requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    snapshots = await db.daily_snapshots.find(
        {"date": {"$gte": cutoff}}, {"_id": 0}
    ).sort("date", 1).to_list(days)

    return {"snapshots": snapshots, "days": days}


@router.get("/product/{product_id}")
async def get_product_history(product_id: str, request: Request, days: int = Query(30, ge=1, le=180)):
    """Get historical data for a specific product — requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    history = await db.product_history.find(
        {"product_id": product_id, "date": {"$gte": cutoff}}, {"_id": 0}
    ).sort("date", 1).to_list(days)

    return {"product_id": product_id, "history": history, "days": days}


@router.post("/snapshot")
async def take_snapshot(request: Request, api_key: str = Query(None)):
    """Take a daily snapshot of all product stats — called by cron."""
    import os
    expected = os.environ.get('CRON_API_KEY', 'alpha-drop-cron-2024')
    if api_key != expected:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid API key")

    from server import db
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    # Check if already taken today
    existing = await db.daily_snapshots.find_one({"date": date_str})
    if existing:
        return {"message": "Snapshot already taken today", "date": date_str}

    total = await db.products.count_documents({})
    explosive = await db.products.count_documents({"status": "EXPLOSIVE"})
    rising = await db.products.count_documents({"status": "RISING"})
    early = await db.products.count_documents({"status": "EARLY_SIGNAL"})

    pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$alpha_score"}}}]
    avg_result = await db.products.aggregate(pipeline).to_list(1)
    avg_score = round(avg_result[0]["avg"], 1) if avg_result else 0

    snapshot = {
        "date": date_str,
        "timestamp": now.isoformat(),
        "total_products": total,
        "explosive": explosive,
        "rising": rising,
        "early_signal": early,
        "avg_alpha_score": avg_score,
        "active_subscribers": await db.user_subscriptions.count_documents({"status": "active"}),
    }
    await db.daily_snapshots.insert_one(snapshot)

    # Also snapshot individual product scores for history tracking
    products = await db.products.find(
        {}, {"_id": 0, "id": 1, "name": 1, "alpha_score": 1, "status": 1, "total_sales": 1, "creator_count": 1, "price": 1}
    ).limit(500).to_list(500)

    if products:
        history_docs = [{
            "product_id": p["id"],
            "date": date_str,
            "alpha_score": p.get("alpha_score", 0),
            "status": p.get("status", ""),
            "total_sales": p.get("total_sales", 0),
            "creator_count": p.get("creator_count", 0),
            "price": p.get("price", 0),
        } for p in products]
        await db.product_history.insert_many(history_docs)

    return {"message": "Snapshot taken", "date": date_str, "products_tracked": len(products)}
