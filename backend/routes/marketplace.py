"""Creator Marketplace — two-sided: sellers post briefs, creators apply."""
from fastapi import APIRouter, Request, Query, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])


class ProductBrief(BaseModel):
    product_name: str
    category: str
    description: str
    budget_range: str  # e.g., "$50-200 per video"
    commission_offered: float  # percentage
    content_type: str  # UGC, Review, Tutorial, etc.
    requirements: Optional[str] = None
    deadline: Optional[str] = None


class CreatorApplication(BaseModel):
    brief_id: str
    message: str
    proposed_rate: Optional[float] = None
    portfolio_link: Optional[str] = None


@router.get("/briefs")
async def get_briefs(
    request: Request,
    category: Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
    status: str = Query("open"),
    limit: int = Query(20, ge=1, le=50),
):
    """Get product briefs — for creators to browse. Requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)

    query = {"status": status}
    if category:
        query["category"] = category
    if content_type:
        query["content_type"] = content_type

    briefs = await db.marketplace_briefs.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"briefs": briefs, "total": await db.marketplace_briefs.count_documents(query)}


@router.post("/briefs")
async def create_brief(body: ProductBrief, request: Request):
    """Post a product brief — sellers looking for creators. Requires subscription."""
    from server import require_subscription, db
    user = await require_subscription(request)

    brief = {
        "id": str(uuid.uuid4()),
        "seller_email": user.email,
        "seller_name": getattr(user, "name", "Seller"),
        "product_name": body.product_name,
        "category": body.category,
        "description": body.description,
        "budget_range": body.budget_range,
        "commission_offered": body.commission_offered,
        "content_type": body.content_type,
        "requirements": body.requirements,
        "deadline": body.deadline,
        "status": "open",
        "applications_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.marketplace_briefs.insert_one(brief)
    brief.pop("_id", None)
    return {"message": "Brief posted", "brief": brief}


@router.get("/briefs/{brief_id}")
async def get_brief_detail(brief_id: str, request: Request):
    """Get a brief with its applications. Requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)

    brief = await db.marketplace_briefs.find_one({"id": brief_id}, {"_id": 0})
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")

    applications = await db.marketplace_applications.find(
        {"brief_id": brief_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)

    return {"brief": brief, "applications": applications}


@router.post("/apply")
async def apply_to_brief(body: CreatorApplication, request: Request):
    """Apply to a product brief — creators applying. Requires subscription."""
    from server import require_subscription, db
    user = await require_subscription(request)

    # Check brief exists
    brief = await db.marketplace_briefs.find_one({"id": body.brief_id}, {"_id": 0})
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    if brief["status"] != "open":
        raise HTTPException(status_code=400, detail="Brief is no longer accepting applications")

    # Check if already applied
    existing = await db.marketplace_applications.find_one({
        "brief_id": body.brief_id, "creator_email": user.email
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this brief")

    application = {
        "id": str(uuid.uuid4()),
        "brief_id": body.brief_id,
        "creator_email": user.email,
        "creator_name": getattr(user, "name", "Creator"),
        "message": body.message,
        "proposed_rate": body.proposed_rate,
        "portfolio_link": body.portfolio_link,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.marketplace_applications.insert_one(application)

    # Increment application count
    await db.marketplace_briefs.update_one(
        {"id": body.brief_id},
        {"$inc": {"applications_count": 1}}
    )

    application.pop("_id", None)
    return {"message": "Application submitted", "application": application}


@router.post("/briefs/{brief_id}/close")
async def close_brief(brief_id: str, request: Request):
    """Close a brief (stop accepting applications). Requires subscription."""
    from server import require_subscription, db
    user = await require_subscription(request)

    result = await db.marketplace_briefs.update_one(
        {"id": brief_id, "seller_email": user.email},
        {"$set": {"status": "closed"}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Brief not found or not yours")
    return {"message": "Brief closed"}


@router.get("/my-briefs")
async def get_my_briefs(request: Request):
    """Get all briefs posted by current user. Requires subscription."""
    from server import require_subscription, db
    user = await require_subscription(request)
    briefs = await db.marketplace_briefs.find(
        {"seller_email": user.email}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return {"briefs": briefs}


@router.get("/my-applications")
async def get_my_applications(request: Request):
    """Get all applications by current user. Requires subscription."""
    from server import require_subscription, db
    user = await require_subscription(request)
    applications = await db.marketplace_applications.find(
        {"creator_email": user.email}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return {"applications": applications}


@router.get("/stats")
async def get_marketplace_stats(request: Request):
    """Get marketplace statistics. Requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)
    return {
        "total_briefs": await db.marketplace_briefs.count_documents({}),
        "open_briefs": await db.marketplace_briefs.count_documents({"status": "open"}),
        "total_applications": await db.marketplace_applications.count_documents({}),
        "categories": ["Beauty & Skincare", "Tech Gadgets", "Health & Wellness", "Home & Kitchen",
                       "Fashion Accessories", "Fitness Equipment", "Pet Products", "Food & Beverages"],
        "content_types": ["UGC Review", "Tutorial", "Unboxing", "Before/After", "Lifestyle", "Green Screen", "Voiceover"],
    }
