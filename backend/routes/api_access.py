"""REST API access for Predator subscribers — API key authentication."""
from fastapi import APIRouter, Request, Query, HTTPException
from typing import Optional
import uuid
import secrets
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1", tags=["api_access"])


async def require_api_key(request: Request):
    """Validate API key from header and check Predator plan."""
    from server import db
    api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required. Pass via X-API-Key header.")

    key_doc = await db.api_keys.find_one({"key": api_key, "active": True}, {"_id": 0})
    if not key_doc:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")

    # Check subscription is active & Predator
    sub = await db.user_subscriptions.find_one(
        {"user_email": key_doc["user_email"], "status": "active"}, {"_id": 0}
    )
    if not sub or sub.get("plan_id") != "predator":
        raise HTTPException(status_code=403, detail="API access requires active Predator plan")

    # Log usage
    await db.api_usage.insert_one({
        "api_key": api_key[:8] + "...",
        "user_email": key_doc["user_email"],
        "endpoint": str(request.url.path),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    return key_doc


@router.post("/keys/generate")
async def generate_api_key(request: Request):
    """Generate an API key — requires Predator subscription."""
    from server import require_subscription, db
    user = await require_subscription(request)

    # Check plan is Predator
    sub = await db.user_subscriptions.find_one(
        {"user_email": user.email, "status": "active"}, {"_id": 0}
    )
    if not sub or sub.get("plan_id") != "predator":
        raise HTTPException(status_code=403, detail="API keys require Predator plan")

    # Deactivate old keys
    await db.api_keys.update_many({"user_email": user.email}, {"$set": {"active": False}})

    key = f"ak_{secrets.token_hex(24)}"
    await db.api_keys.insert_one({
        "id": str(uuid.uuid4()),
        "user_email": user.email,
        "key": key,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"api_key": key, "message": "Store this key securely — it won't be shown again."}


@router.get("/products")
async def api_get_products(
    request: Request,
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """Get products via API key — Predator only."""
    await require_api_key(request)
    from server import db

    query = {}
    if status:
        query["status"] = status
    if category:
        query["category"] = category
    if min_score:
        query["alpha_score"] = {"$gte": min_score}

    products = await db.products.find(
        query, {"_id": 0, "id": 1, "name": 1, "category": 1, "price": 1,
                "alpha_score": 1, "status": 1, "total_sales": 1, "total_views": 1,
                "creator_count": 1, "avg_engagement": 1, "risk_level": 1, "reason": 1}
    ).sort("alpha_score", -1).limit(limit).to_list(limit)

    return {"products": products, "count": len(products)}


@router.get("/products/{product_id}")
async def api_get_product(product_id: str, request: Request):
    """Get single product via API key — Predator only."""
    await require_api_key(request)
    from server import db
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/affiliates")
async def api_get_affiliates(
    request: Request,
    niche: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """Get affiliates via API key — Predator only."""
    await require_api_key(request)
    from server import db
    query = {}
    if niche:
        query["niche"] = niche
    affiliates = await db.affiliates.find(query, {"_id": 0}).sort("followers", -1).limit(limit).to_list(limit)
    return {"affiliates": affiliates, "count": len(affiliates)}


@router.get("/stats")
async def api_get_stats(request: Request):
    """Get platform stats via API key — Predator only."""
    await require_api_key(request)
    from server import db
    return {
        "total_products": await db.products.count_documents({}),
        "explosive": await db.products.count_documents({"status": "EXPLOSIVE"}),
        "rising": await db.products.count_documents({"status": "RISING"}),
        "early_signal": await db.products.count_documents({"status": "EARLY_SIGNAL"}),
        "total_affiliates": await db.affiliates.count_documents({}),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
