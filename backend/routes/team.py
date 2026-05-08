"""Team collaboration for Predator plan — invite members, shared resources."""
from fastapi import APIRouter, Request, Query, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/api/team", tags=["team"])


class TeamInvite(BaseModel):
    email: EmailStr
    role: str = "member"  # member, viewer


@router.get("")
async def get_team(request: Request):
    """Get current user's team — requires Predator subscription."""
    from server import require_subscription, db
    user = await require_subscription(request)

    sub = await db.user_subscriptions.find_one(
        {"user_email": user.email, "status": "active"}, {"_id": 0}
    )
    if not sub or sub.get("plan_id") != "predator":
        raise HTTPException(status_code=403, detail="Team features require Predator plan")

    team = await db.teams.find_one({"owner_email": user.email}, {"_id": 0})
    if not team:
        # Auto-create team
        team = {
            "id": str(uuid.uuid4()),
            "owner_email": user.email,
            "name": f"{user.name}'s Team",
            "members": [],
            "max_seats": 3,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.teams.insert_one(team)

    return team


@router.post("/invite")
async def invite_member(body: TeamInvite, request: Request):
    """Invite a team member — requires Predator subscription."""
    from server import require_subscription, db
    user = await require_subscription(request)

    sub = await db.user_subscriptions.find_one(
        {"user_email": user.email, "status": "active"}, {"_id": 0}
    )
    if not sub or sub.get("plan_id") != "predator":
        raise HTTPException(status_code=403, detail="Team features require Predator plan")

    team = await db.teams.find_one({"owner_email": user.email}, {"_id": 0})
    if not team:
        raise HTTPException(status_code=404, detail="No team found")

    if len(team.get("members", [])) >= team.get("max_seats", 3):
        raise HTTPException(status_code=400, detail=f"Team is full ({team['max_seats']} seats)")

    # Check if already a member
    if any(m["email"] == body.email for m in team.get("members", [])):
        raise HTTPException(status_code=400, detail="Already a team member")

    member = {
        "email": body.email,
        "role": body.role,
        "status": "invited",
        "invited_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.teams.update_one(
        {"owner_email": user.email},
        {"$push": {"members": member}}
    )

    # Grant the invited member a subscription bypass
    existing_sub = await db.user_subscriptions.find_one({"user_email": body.email, "status": "active"})
    if not existing_sub:
        await db.user_subscriptions.insert_one({
            "id": str(uuid.uuid4()),
            "user_email": body.email,
            "plan_id": "predator",
            "plan_name": "Predator (Team)",
            "status": "active",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": sub.get("expires_at", ""),
            "payment_session_id": f"team_invite_{user.email}",
        })

    return {"message": f"Invited {body.email} to the team", "member": member}


@router.delete("/members/{member_email}")
async def remove_member(member_email: str, request: Request):
    """Remove a team member — requires Predator subscription."""
    from server import require_subscription, db
    user = await require_subscription(request)

    await db.teams.update_one(
        {"owner_email": user.email},
        {"$pull": {"members": {"email": member_email}}}
    )

    # Remove their team subscription
    await db.user_subscriptions.delete_many({
        "user_email": member_email,
        "payment_session_id": {"$regex": "^team_invite_"}
    })

    return {"message": f"Removed {member_email} from team"}
