"""Creator self-registration portal — creators can sign up, build profile, set rates."""
from fastapi import APIRouter, Request, Query, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import uuid
import bcrypt
from datetime import datetime, timezone

router = APIRouter(prefix="/api/creators", tags=["creator_portal"])


class CreatorRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    handle: str  # TikTok handle
    niche: str
    secondary_niche: Optional[str] = None
    bio: Optional[str] = None
    followers: Optional[int] = 0
    engagement_rate: Optional[float] = 0
    content_style: Optional[str] = "UGC"
    commission_preference: Optional[str] = "10-20%"
    contact_method: Optional[str] = "Email"
    portfolio_link: Optional[str] = None


class CreatorLogin(BaseModel):
    email: str
    password: str


class CreatorProfileUpdate(BaseModel):
    name: Optional[str] = None
    handle: Optional[str] = None
    niche: Optional[str] = None
    secondary_niche: Optional[str] = None
    bio: Optional[str] = None
    followers: Optional[int] = None
    engagement_rate: Optional[float] = None
    content_style: Optional[str] = None
    commission_preference: Optional[str] = None
    contact_method: Optional[str] = None
    portfolio_link: Optional[str] = None
    availability: Optional[str] = None  # Available, Selective, Booked
    response_time: Optional[str] = None


@router.post("/register")
async def register_creator(body: CreatorRegister):
    """Register as a creator — public endpoint."""
    from server import db
    import bcrypt as _bcrypt

    # Check if email already exists
    existing = await db.creator_accounts.find_one({"email": body.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check handle uniqueness
    handle_exists = await db.creator_accounts.find_one({"handle": body.handle.lower()})
    if handle_exists:
        raise HTTPException(status_code=400, detail="Handle already taken")

    password_hash = _bcrypt.hashpw(body.password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")

    creator = {
        "id": str(uuid.uuid4()),
        "email": body.email.lower(),
        "password_hash": password_hash,
        "name": body.name,
        "handle": body.handle.lower() if not body.handle.startswith("@") else body.handle.lower(),
        "niche": body.niche,
        "secondary_niche": body.secondary_niche,
        "bio": body.bio or "",
        "followers": body.followers or 0,
        "engagement_rate": body.engagement_rate or 0,
        "content_style": body.content_style or "UGC",
        "commission_preference": body.commission_preference or "10-20%",
        "contact_method": body.contact_method or "Email",
        "contact_email": body.email.lower(),
        "portfolio_link": body.portfolio_link or "",
        "availability": "Available",
        "response_time": "< 24h",
        "rating": 5.0,
        "products_promoted": 0,
        "total_sales_driven": 0,
        "total_earnings": 0,
        "verified": False,
        "status": "Active",
        "sample_content": [],
        "categories_worked": [body.niche],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.creator_accounts.insert_one(creator)

    # Also add to the main affiliates collection for discoverability
    affiliate_entry = {
        "id": creator["id"],
        "handle": creator["handle"],
        "name": creator["name"],
        "niche": creator["niche"],
        "secondary_niche": creator["secondary_niche"],
        "followers": creator["followers"],
        "avg_views": int(creator["followers"] * 0.05),
        "engagement_rate": creator["engagement_rate"],
        "commission_range": creator["commission_preference"],
        "avg_commission": 15.0,
        "products_promoted": 0,
        "total_sales_driven": 0,
        "contact_email": creator["email"],
        "contact_method": creator["contact_method"],
        "agency": None,
        "status": "Active",
        "top_categories": [creator["niche"]],
        "rating": 5.0,
        "response_time": "< 24h",
        "created_at": creator["created_at"],
    }
    await db.affiliates.insert_one(affiliate_entry)

    creator.pop("password_hash", None)
    creator.pop("_id", None)
    return {"message": "Creator account registered successfully", "creator": {k: v for k, v in creator.items() if k != "_id"}}


@router.post("/login")
async def login_creator(body: CreatorLogin, response=None):
    """Creator login — returns profile data."""
    from server import db
    from fastapi import Response
    import bcrypt as _bcrypt
    import jwt as _jwt
    import os

    creator = await db.creator_accounts.find_one({"email": body.email.lower()})
    if not creator:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not _bcrypt.checkpw(body.password.encode("utf-8"), creator["password_hash"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate token
    jwt_secret = os.environ.get("JWT_SECRET", "fallback_secret")
    from datetime import timedelta
    import jwt as pyjwt
    token = pyjwt.encode({
        "sub": creator["id"],
        "email": creator["email"],
        "role": "creator",
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
    }, jwt_secret, algorithm="HS256")

    profile = {k: v for k, v in creator.items() if k not in ("_id", "password_hash")}
    return {"token": token, "creator": profile}


@router.get("/profile/{creator_id}")
async def get_creator_profile(creator_id: str):
    """Get public creator profile — public endpoint."""
    from server import db
    creator = await db.creator_accounts.find_one({"id": creator_id}, {"_id": 0, "password_hash": 0})
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    return creator


@router.put("/profile/{creator_id}")
async def update_creator_profile(creator_id: str, body: CreatorProfileUpdate, request: Request):
    """Update creator profile — requires creator auth or admin."""
    from server import db, get_admin_user
    
    # Check admin or creator token
    try:
        await get_admin_user(request)
    except HTTPException:
        # Not admin, check creator token
        import jwt as pyjwt
        import os
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            raise HTTPException(status_code=401, detail="Authentication required")
        try:
            payload = pyjwt.decode(token, os.environ.get("JWT_SECRET", ""), algorithms=["HS256"])
            if payload.get("sub") != creator_id:
                raise HTTPException(status_code=403, detail="Can only update your own profile")
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    await db.creator_accounts.update_one({"id": creator_id}, {"$set": update_data})

    # Also update affiliates collection
    affiliate_fields = {k: v for k, v in update_data.items() if k in ("handle", "name", "niche", "secondary_niche", "followers", "engagement_rate", "contact_method", "availability")}
    if affiliate_fields:
        await db.affiliates.update_one({"id": creator_id}, {"$set": affiliate_fields})

    return {"message": "Profile updated", "updated_fields": list(update_data.keys())}


@router.get("/browse")
async def browse_creators(
    niche: Optional[str] = Query(None),
    min_followers: Optional[int] = Query(None),
    availability: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50),
):
    """Browse registered creators — public endpoint for sellers."""
    from server import db
    query = {}
    if niche:
        query["niche"] = niche
    if min_followers:
        query["followers"] = {"$gte": min_followers}
    if availability:
        query["availability"] = availability

    creators = await db.creator_accounts.find(
        query, {"_id": 0, "password_hash": 0}
    ).sort("followers", -1).limit(limit).to_list(limit)

    return {"creators": creators, "total": await db.creator_accounts.count_documents(query)}


@router.post("/sample-content/{creator_id}")
async def add_sample_content(creator_id: str, request: Request, video_url: str = Query(...), description: str = Query("")):
    """Add sample content to portfolio. Requires creator auth."""
    from server import db
    import jwt as pyjwt
    import os

    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = pyjwt.decode(token, os.environ.get("JWT_SECRET", ""), algorithms=["HS256"])
        if payload.get("sub") != creator_id:
            raise HTTPException(status_code=403, detail="Can only update your own profile")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    content = {
        "id": str(uuid.uuid4())[:8],
        "video_url": video_url,
        "description": description,
        "added_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.creator_accounts.update_one(
        {"id": creator_id},
        {"$push": {"sample_content": content}}
    )

    return {"message": "Sample content added", "content": content}
