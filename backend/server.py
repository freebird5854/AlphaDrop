from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
import secrets
import io
import csv
from datetime import datetime, timezone, timedelta
import random
import math
import httpx
import resend
import bcrypt
import jwt as pyjwt

# Stripe integration
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, 
    CheckoutSessionResponse, 
    CheckoutStatusResponse, 
    CheckoutSessionRequest
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Data API Keys (optional - enables real data)
SCRAPE_CREATORS_API_KEY = os.environ.get('SCRAPE_CREATORS_API_KEY')
SOCIAVAULT_API_KEY = os.environ.get('SOCIAVAULT_API_KEY')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
APP_URL = os.environ.get('APP_URL', '')

# Admin auth
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@alphadrop.com')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'AlphaDr0p!2026')
JWT_SECRET = os.environ.get('JWT_SECRET', secrets.token_hex(32))
JWT_ALGORITHM = "HS256"

# Initialize Resend
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY


# ============== PASSWORD & JWT HELPERS ==============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_admin_token(user_id: str, email: str, role: str = "admin") -> str:
    payload = {
        "sub": user_id, "email": email, "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "admin_access"
    }
    return pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_admin_user(request: Request):
    """Extract and verify admin JWT from cookie or header."""
    token = request.cookies.get("admin_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Admin authentication required")
    try:
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        return payload
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


app = FastAPI(title="ALPHA DROP - Product Intelligence Engine")
api_router = APIRouter(prefix="/api")

# ============== SUBSCRIPTION PLANS ==============
SUBSCRIPTION_PLANS = {
    "scout": {
        "name": "Scout",
        "price": 79.00,
        "products_limit": 50,
        "features": ["50 products tracked", "Basic Alpha Score", "7-day history", "Email alerts", "CSV export"]
    },
    "hunter": {
        "name": "Hunter", 
        "price": 199.00,
        "products_limit": 500,
        "features": ["500 products tracked", "Full analytics", "30-day history", "Real-time alerts", "Hook intelligence", "Market validation", "Basic affiliate data", "CSV export"]
    },
    "predator": {
        "name": "Predator",
        "price": 499.00,
        "products_limit": -1,  # Unlimited
        "features": ["Unlimited products", "180-day history", "REST API access", "Team seats (3)", "Priority support", "Full affiliate tools", "Google Trends data", "Historical tracking"]
    },
    "affiliate_pro": {
        "name": "Affiliate Pro",
        "price": 99.00,
        "products_limit": 0,
        "is_addon": True,
        "requires_plan": "hunter",
        "features": ["Full affiliate marketplace", "Niche-matched creators", "Contact info access", "Earnings calculator", "Bulk affiliate apply"]
    }
}

# ============== MODELS ==============

class ScoreBreakdown(BaseModel):
    velocity_score: float = Field(ge=0, le=100)
    creator_adoption_score: float = Field(ge=0, le=100)
    engagement_quality_score: float = Field(ge=0, le=100)
    hook_strength_score: float = Field(ge=0, le=100)
    market_expansion_score: float = Field(ge=0, le=100)
    saturation_risk_score: float = Field(ge=0, le=100)
    repeatability_score: float = Field(ge=0, le=100)
    # Enhanced v2.0 signals
    ad_duplication_index: float = Field(default=0, ge=0, le=100)
    comment_sentiment_score: float = Field(default=0, ge=0, le=100)
    hashtag_velocity: float = Field(default=0, ge=0, le=100)
    multi_creator_convergence: float = Field(default=0, ge=0, le=100)
    price_stability_index: float = Field(default=0, ge=0, le=100)

class TrendData(BaseModel):
    date: str
    sales: int
    views: int
    creators: int
    engagement: float

class HookAnalysis(BaseModel):
    hook_type: str
    description: str
    effectiveness: int
    examples: List[str]

class MarketValidation(BaseModel):
    tiktok_demand: int
    amazon_demand: int
    google_trends: int
    cross_platform_score: int

class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    image_url: str
    price: float
    alpha_score: int
    score_breakdown: ScoreBreakdown
    status: str  # EXPLOSIVE, EXPLODING_SOON, SCALING_NOW, RISING, EARLY_SIGNAL, WATCHLIST, SATURATION_WARNING, AVOID
    trend_direction: str  # up, down, stable
    risk_level: str  # low, medium, high
    reason: str
    total_sales: int
    total_views: int
    creator_count: int
    avg_engagement: float
    trend_data: List[TrendData]
    hook_analysis: List[HookAnalysis]
    market_validation: MarketValidation
    top_videos: List[Dict[str, Any]]
    competition_density: int
    # Enhanced v2.0 fields
    momentum_multiplier: float = Field(default=1.0)
    saturation_countdown: int = Field(default=-1)  # days until saturation, -1 = not saturating
    entry_window: str = Field(default="open")  # optimal, open, closing, closed
    created_at: str
    updated_at: str

class Alert(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    product_name: str
    alert_type: str  # NEW_EXPLOSIVE, VELOCITY_SPIKE, LOW_COMPETITION_HIGH_DEMAND
    message: str
    severity: str  # critical, warning, info
    created_at: str
    read: bool = False

class DashboardStats(BaseModel):
    total_products_tracked: int
    explosive_count: int
    rising_count: int
    early_signal_count: int
    avg_alpha_score: float
    top_category: str

# ============== SUBSCRIPTION & WATCHLIST MODELS ==============

class WatchlistItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    product_id: str
    product_name: str
    product_image: str
    alpha_score: int
    status: str
    added_at: str
    notes: Optional[str] = None

class PaymentTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_email: Optional[str] = None
    plan_id: str
    amount: float
    currency: str = "usd"
    status: str = "pending"  # pending, paid, failed, expired
    payment_status: str = "initiated"
    metadata: Dict[str, Any] = {}
    created_at: str
    updated_at: str

class UserSubscription(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_email: str
    plan_id: str
    plan_name: str
    status: str = "active"  # active, cancelled, expired
    started_at: str
    expires_at: str
    payment_session_id: str

# ============== USER & AUTH MODELS ==============

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    email_notifications: bool = True
    created_at: str
    updated_at: str

class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    user_id: str
    session_token: str
    expires_at: str
    created_at: str

class BetaSignup(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: Optional[str] = None
    source: str = "website"
    status: str = "pending"  # pending, invited, active
    created_at: str

class EmailNotificationRequest(BaseModel):
    recipient_email: EmailStr
    subject: str
    html_content: str

# ============== DATA GENERATION ==============

CATEGORIES = [
    "Beauty & Skincare", "Home & Kitchen", "Fashion Accessories", 
    "Tech Gadgets", "Health & Wellness", "Pet Products",
    "Fitness Equipment", "Baby Products", "Outdoor & Travel",
    "Food & Beverages", "Jewelry", "Car Accessories"
]

PRODUCT_NAMES = {
    "Beauty & Skincare": [
        "Glow Serum Pro", "Ice Roller Set", "LED Face Mask", "Vitamin C Drops",
        "Retinol Night Cream", "Lip Plumping Gloss", "Pore Vacuum Cleaner",
        "Jade Roller Kit", "Snail Mucin Essence", "Glass Skin Toner"
    ],
    "Home & Kitchen": [
        "Smart Air Fryer", "Sunrise Alarm Clock", "Cloud Pillow 3000",
        "Self-Cleaning Water Bottle", "Mini Waffle Maker", "Magnetic Spice Rack",
        "Portable Blender Pro", "Steam Mop Ultra", "Ice Maker Compact", "Smart Plant Pot"
    ],
    "Fashion Accessories": [
        "Oversized Sunglasses", "Chain Belt Gold", "Silk Scrunchie Set",
        "Leather Card Wallet", "Statement Earrings", "Bucket Hat Vintage",
        "Pearl Hair Clips", "Crossbody Mini Bag", "Beaded Phone Strap", "Claw Clip Set"
    ],
    "Tech Gadgets": [
        "Mini Projector HD", "Wireless Earbuds Pro", "Ring Light 18inch",
        "Portable Charger 20K", "Smart Watch Ultra", "Bluetooth Speaker Boom",
        "Keyboard Mechanical", "Mouse Pad RGB", "USB Hub Station", "Webcam 4K"
    ],
    "Health & Wellness": [
        "Posture Corrector", "Massage Gun Pro", "Sleep Gummies", "Blue Light Glasses",
        "Acupressure Mat", "Vitamin D Drops", "Collagen Powder", "Meditation Cushion",
        "Essential Oil Set", "Smart Scale Body"
    ],
    "Pet Products": [
        "Interactive Cat Toy", "Dog Camera Treat", "Self-Cleaning Litter",
        "Pet Water Fountain", "Calming Dog Bed", "GPS Pet Tracker",
        "Automatic Feeder", "Pet Hair Remover", "Dog Raincoat", "Cat Tower Deluxe"
    ],
    "Fitness Equipment": [
        "Resistance Bands Set", "Yoga Mat Premium", "Jump Rope Smart",
        "Dumbbell Adjustable", "Ab Roller Wheel", "Pull Up Bar Door",
        "Kettlebell Set", "Foam Roller Pro", "Boxing Gloves", "Balance Board"
    ],
    "Baby Products": [
        "White Noise Machine", "Baby Monitor 360", "Silicone Bibs Set",
        "Portable High Chair", "Diaper Bag Deluxe", "Teething Toys",
        "Baby Carrier Wrap", "Bottle Warmer Fast", "Night Light Kids", "Play Mat Sensory"
    ],
    "Outdoor & Travel": [
        "Packable Backpack", "Hammock Portable", "Solar Power Bank",
        "Camping Light LED", "Travel Pillow Memory", "Water Filter Bottle",
        "Hiking Poles Carbon", "Beach Tent Pop-up", "Cooler Bag Insulated", "Binoculars Compact"
    ],
    "Food & Beverages": [
        "Protein Coffee Mix", "Matcha Powder Premium", "Hot Sauce Sampler",
        "Energy Drink Mix", "Snack Box Healthy", "Mushroom Coffee",
        "Collagen Creamer", "Superfood Blend", "Keto Snack Bars", "Electrolyte Powder"
    ],
    "Jewelry": [
        "Layered Necklace Set", "Huggie Earrings Gold", "Tennis Bracelet",
        "Signet Ring", "Anklet Chain", "Ear Cuff Set", "Pendant Necklace",
        "Stackable Rings", "Charm Bracelet", "Hoop Earrings Large"
    ],
    "Car Accessories": [
        "Phone Mount Magnetic", "Dash Cam 4K", "Seat Gap Filler",
        "Car Vacuum Mini", "LED Strip Interior", "Trunk Organizer",
        "Steering Wheel Cover", "Air Freshener Set", "Sunshade Windshield", "Car Charger Fast"
    ]
}

PRODUCT_IMAGES = [
    "https://images.unsplash.com/photo-1687168582375-097293b91c04?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1595756630832-848909a39597?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1629198688000-71f23e745b6e?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1560343090-f0409e92791a?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=400&h=400&fit=crop",
]

HOOK_TYPES = [
    {"type": "Problem → Solution", "examples": ["You've been doing it wrong...", "Finally! A solution to...", "Say goodbye to..."]},
    {"type": "Transformation", "examples": ["Watch this transform...", "Before and after...", "The glow up is real..."]},
    {"type": "Satisfaction", "examples": ["So satisfying...", "Watch until the end...", "The way it just..."]},
    {"type": "Convenience", "examples": ["Life hack:", "I wish I knew this sooner...", "Game changer:"]},
    {"type": "FOMO", "examples": ["TikTok made me buy it", "Why didn't I buy this sooner", "Obsessed with this find"]},
    {"type": "Unboxing", "examples": ["Let's unbox...", "Package reveal:", "What I ordered vs what I got"]},
]

REASONS = {
    "EXPLOSIVE": [
        "Viral velocity detected - 340% growth in 48h",
        "Creator adoption surging - 127 new creators this week",
        "Cross-platform breakout - trending on Amazon too",
        "Perfect storm: high demand + low competition",
        "Engagement quality exceptional - 8.2% comment rate"
    ],
    "SCALING_NOW": [
        "Consistent 200%+ weekly growth with stable margins",
        "Multi-creator convergence - 40+ independent creators found this product",
        "Strong buyer intent in comments - 15% asking for links",
        "Ad creative being duplicated by 20+ advertisers"
    ],
    "EXPLODING_SOON": [
        "Pre-viral pattern detected - accumulation phase",
        "Momentum multiplier accelerating rapidly",
        "Low saturation + high engagement = optimal entry",
        "Creator network forming - critical mass approaching"
    ],
    "RISING": [
        "Steady acceleration - consistent 50%+ weekly growth",
        "Creator network expanding rapidly",
        "Hook patterns matching viral templates",
        "Market validation strong across platforms",
        "Entering mainstream adoption phase"
    ],
    "EARLY_SIGNAL": [
        "Early accumulation detected - 12 creators, 47k avg views",
        "Posting frequency increasing 3x in 7 days",
        "Engagement ratio above category average",
        "Low saturation window detected",
        "Pre-viral pattern recognized"
    ],
    "SATURATION_WARNING": [
        "Price erosion detected - margins compressing",
        "Ad duplication index critical - 50+ advertisers copying",
        "Creator growth stalling - audience fatigue",
        "Competition density approaching category capacity"
    ],
    "WATCHLIST": [
        "Moderate growth - needs monitoring",
        "Competition increasing - timing critical",
        "Mixed signals across platforms",
        "Hook effectiveness declining"
    ],
    "AVOID": [
        "Market saturated - 500+ active sellers",
        "Velocity declining - down 23% this week",
        "High competition density detected",
        "Engagement quality dropping"
    ]
}

def calculate_alpha_score(breakdown: ScoreBreakdown) -> tuple:
    """Calculate enhanced Alpha Score v2.0 with momentum multiplier."""
    # Base score from all factors
    base_weights = {
        'velocity_score': 0.15,
        'creator_adoption_score': 0.12,
        'engagement_quality_score': 0.10,
        'hook_strength_score': 0.07,
        'market_expansion_score': 0.08,
        'saturation_risk_score': 0.06,
        'repeatability_score': 0.05,
        # v2.0 enhanced signals
        'multi_creator_convergence': 0.08,
        'comment_sentiment_score': 0.08,
        'hashtag_velocity': 0.05,
        'ad_duplication_index': 0.04,  # Inverted — high duplication = bad
        'price_stability_index': 0.04,
    }
    # Remaining 8% distributed as bonuses for exceptional signals
    
    base_score = (
        breakdown.velocity_score * base_weights['velocity_score'] +
        breakdown.creator_adoption_score * base_weights['creator_adoption_score'] +
        breakdown.engagement_quality_score * base_weights['engagement_quality_score'] +
        breakdown.hook_strength_score * base_weights['hook_strength_score'] +
        breakdown.market_expansion_score * base_weights['market_expansion_score'] +
        (100 - breakdown.saturation_risk_score) * base_weights['saturation_risk_score'] +
        breakdown.repeatability_score * base_weights['repeatability_score'] +
        breakdown.multi_creator_convergence * base_weights['multi_creator_convergence'] +
        breakdown.comment_sentiment_score * base_weights['comment_sentiment_score'] +
        breakdown.hashtag_velocity * base_weights['hashtag_velocity'] +
        (100 - breakdown.ad_duplication_index) * base_weights['ad_duplication_index'] +
        breakdown.price_stability_index * base_weights['price_stability_index']
    )
    
    # Momentum multiplier: rewards accelerating products
    velocity_accel = breakdown.velocity_score / 100
    momentum = 1.0 + (velocity_accel - 0.5) * 0.4  # Range: 0.8 to 1.2
    momentum = max(0.7, min(1.5, momentum))
    
    final_score = min(100, max(0, int(base_score * momentum)))
    
    # Calculate saturation countdown
    saturation_days = _estimate_saturation(breakdown)
    
    # Entry window
    if saturation_days > 60:
        entry_window = "optimal"
    elif saturation_days > 30:
        entry_window = "open"
    elif saturation_days > 14:
        entry_window = "closing"
    elif saturation_days > 0:
        entry_window = "closed"
    else:
        entry_window = "open"
    
    return final_score, round(momentum, 2), saturation_days, entry_window


def _estimate_saturation(breakdown: ScoreBreakdown) -> int:
    """Estimate days until market saturation."""
    saturation_risk = breakdown.saturation_risk_score
    ad_duplication = breakdown.ad_duplication_index
    price_stability = breakdown.price_stability_index
    
    # High saturation risk + high ad duplication + low price stability = quick saturation
    risk_factor = (saturation_risk * 0.5 + ad_duplication * 0.3 + (100 - price_stability) * 0.2) / 100
    
    if risk_factor < 0.3:
        return -1  # Not saturating
    elif risk_factor < 0.5:
        return random.randint(45, 90)
    elif risk_factor < 0.7:
        return random.randint(20, 45)
    elif risk_factor < 0.85:
        return random.randint(7, 20)
    else:
        return random.randint(1, 7)


def get_status_from_score(score: int, momentum: float = 1.0, saturation_days: int = -1) -> str:
    """Enhanced status classification with new categories."""
    # Saturation warning overrides if countdown is low
    if 0 < saturation_days <= 14 and score < 72:
        return "SATURATION_WARNING"
    
    if score >= 90:
        return "EXPLOSIVE"
    elif score >= 80 and momentum >= 1.2:
        return "SCALING_NOW"
    elif score >= 72:
        if momentum >= 1.1:
            return "EXPLOSIVE"
        else:
            return "EXPLODING_SOON"
    elif score >= 58:
        return "RISING"
    elif score >= 45:
        return "EARLY_SIGNAL"
    elif score >= 30:
        if saturation_days > 0 and saturation_days <= 30:
            return "SATURATION_WARNING"
        return "WATCHLIST"
    else:
        return "AVOID"

def generate_trend_data(days: int = 14, base_sales: int = 100, growth_type: str = "EXPLOSIVE") -> List[TrendData]:
    """Generate realistic trend data based on product status"""
    data = []
    multipliers = {
        "EXPLOSIVE": (1.15, 1.35),
        "SCALING_NOW": (1.12, 1.28),
        "EXPLODING_SOON": (1.08, 1.22),
        "RISING": (1.05, 1.15),
        "EARLY_SIGNAL": (1.02, 1.10),
        "SATURATION_WARNING": (0.92, 1.02),
        "WATCHLIST": (0.95, 1.05),
        "AVOID": (0.85, 0.98)
    }
    
    mult_range = multipliers.get(growth_type, (1.0, 1.05))
    current_sales = base_sales
    current_views = base_sales * random.randint(50, 150)
    current_creators = random.randint(5, 20)
    
    for i in range(days):
        date = (datetime.now(timezone.utc) - timedelta(days=days-i-1)).strftime("%Y-%m-%d")
        
        # Add some randomness with overall trend
        daily_mult = random.uniform(mult_range[0], mult_range[1])
        current_sales = int(current_sales * daily_mult)
        current_views = int(current_views * daily_mult * random.uniform(0.9, 1.1))
        current_creators = max(1, current_creators + random.randint(-1, 3))
        
        engagement = round(random.uniform(3.0, 12.0), 2)
        
        data.append(TrendData(
            date=date,
            sales=current_sales,
            views=current_views,
            creators=current_creators,
            engagement=engagement
        ))
    
    return data

def generate_hook_analysis() -> List[HookAnalysis]:
    """Generate hook analysis data"""
    selected_hooks = random.sample(HOOK_TYPES, k=random.randint(2, 4))
    return [
        HookAnalysis(
            hook_type=hook["type"],
            description=f"Effective {hook['type'].lower()} angle driving engagement",
            effectiveness=random.randint(60, 95),
            examples=hook["examples"]
        )
        for hook in selected_hooks
    ]

def generate_market_validation(status: str) -> MarketValidation:
    """Generate cross-platform market validation data"""
    base_scores = {
        "EXPLOSIVE": (75, 95),
        "RISING": (60, 85),
        "EARLY_SIGNAL": (40, 70),
        "WATCHLIST": (30, 55),
        "AVOID": (10, 40)
    }
    score_range = base_scores.get(status, (30, 60))
    
    return MarketValidation(
        tiktok_demand=random.randint(score_range[0], score_range[1]),
        amazon_demand=random.randint(score_range[0] - 10, score_range[1]),
        google_trends=random.randint(score_range[0] - 5, score_range[1] - 5),
        cross_platform_score=random.randint(score_range[0], score_range[1])
    )

def generate_top_videos() -> List[Dict[str, Any]]:
    """Generate sample top video data"""
    return [
        {
            "id": str(uuid.uuid4())[:8],
            "views": random.randint(100000, 5000000),
            "likes": random.randint(10000, 500000),
            "comments": random.randint(500, 50000),
            "shares": random.randint(100, 10000),
            "creator": f"@creator_{random.randint(100, 999)}",
            "hook": random.choice(HOOK_TYPES)["examples"][0],
            "posted_days_ago": random.randint(1, 14)
        }
        for _ in range(random.randint(3, 6))
    ]

def generate_product(force_status: Optional[str] = None) -> Product:
    """Generate a realistic simulated product with AlphaScore v2.0"""
    category = random.choice(CATEGORIES)
    name = random.choice(PRODUCT_NAMES[category])
    
    # Generate score breakdown based on desired status or random
    if force_status == "EXPLOSIVE":
        breakdown = ScoreBreakdown(
            velocity_score=random.uniform(80, 98),
            creator_adoption_score=random.uniform(75, 95),
            engagement_quality_score=random.uniform(70, 95),
            hook_strength_score=random.uniform(75, 95),
            market_expansion_score=random.uniform(70, 90),
            saturation_risk_score=random.uniform(10, 30),
            repeatability_score=random.uniform(75, 95),
            ad_duplication_index=random.uniform(5, 25),
            comment_sentiment_score=random.uniform(75, 95),
            hashtag_velocity=random.uniform(70, 95),
            multi_creator_convergence=random.uniform(80, 98),
            price_stability_index=random.uniform(75, 95),
        )
    elif force_status == "RISING":
        breakdown = ScoreBreakdown(
            velocity_score=random.uniform(60, 80),
            creator_adoption_score=random.uniform(55, 75),
            engagement_quality_score=random.uniform(55, 75),
            hook_strength_score=random.uniform(60, 80),
            market_expansion_score=random.uniform(55, 75),
            saturation_risk_score=random.uniform(25, 45),
            repeatability_score=random.uniform(60, 80),
            ad_duplication_index=random.uniform(20, 45),
            comment_sentiment_score=random.uniform(55, 80),
            hashtag_velocity=random.uniform(50, 75),
            multi_creator_convergence=random.uniform(50, 75),
            price_stability_index=random.uniform(60, 85),
        )
    elif force_status == "EARLY_SIGNAL":
        breakdown = ScoreBreakdown(
            velocity_score=random.uniform(45, 65),
            creator_adoption_score=random.uniform(40, 60),
            engagement_quality_score=random.uniform(50, 70),
            hook_strength_score=random.uniform(50, 70),
            market_expansion_score=random.uniform(35, 55),
            saturation_risk_score=random.uniform(15, 35),
            repeatability_score=random.uniform(50, 70),
            ad_duplication_index=random.uniform(10, 30),
            comment_sentiment_score=random.uniform(50, 75),
            hashtag_velocity=random.uniform(40, 65),
            multi_creator_convergence=random.uniform(30, 55),
            price_stability_index=random.uniform(70, 90),
        )
    else:
        # Random distribution for WATCHLIST/AVOID
        breakdown = ScoreBreakdown(
            velocity_score=random.uniform(20, 50),
            creator_adoption_score=random.uniform(20, 45),
            engagement_quality_score=random.uniform(25, 50),
            hook_strength_score=random.uniform(30, 55),
            market_expansion_score=random.uniform(20, 45),
            saturation_risk_score=random.uniform(50, 90),
            repeatability_score=random.uniform(25, 50),
            ad_duplication_index=random.uniform(50, 90),
            comment_sentiment_score=random.uniform(20, 50),
            hashtag_velocity=random.uniform(10, 40),
            multi_creator_convergence=random.uniform(10, 35),
            price_stability_index=random.uniform(20, 50),
        )
    
    alpha_score, momentum, saturation_days, entry_window = calculate_alpha_score(breakdown)
    status = force_status if force_status else get_status_from_score(alpha_score, momentum, saturation_days)
    
    # Determine trend direction and risk
    trend_direction = "up" if status in ["EXPLOSIVE", "SCALING_NOW", "EXPLODING_SOON", "RISING", "EARLY_SIGNAL"] else ("stable" if status == "WATCHLIST" else "down")
    risk_level = "low" if status in ["EXPLOSIVE", "SCALING_NOW"] else ("medium" if status in ["EXPLODING_SOON", "RISING", "EARLY_SIGNAL"] else "high")
    
    reason = random.choice(REASONS.get(status, REASONS.get("WATCHLIST", ["Monitoring..."])))
    
    base_sales = random.randint(500, 10000) if status in ["EXPLOSIVE", "SCALING_NOW"] else random.randint(100, 3000)
    trend_data = generate_trend_data(14, base_sales, status)
    
    now = datetime.now(timezone.utc).isoformat()
    
    return Product(
        name=name,
        category=category,
        image_url=random.choice(PRODUCT_IMAGES),
        price=round(random.uniform(9.99, 89.99), 2),
        alpha_score=alpha_score,
        score_breakdown=breakdown,
        status=status,
        trend_direction=trend_direction,
        risk_level=risk_level,
        reason=reason,
        total_sales=sum(d.sales for d in trend_data),
        total_views=sum(d.views for d in trend_data),
        creator_count=trend_data[-1].creators if trend_data else 0,
        avg_engagement=round(sum(d.engagement for d in trend_data) / len(trend_data), 2) if trend_data else 0,
        trend_data=trend_data,
        hook_analysis=generate_hook_analysis(),
        market_validation=generate_market_validation(status),
        top_videos=generate_top_videos(),
        competition_density=random.randint(10, 100) if status == "AVOID" else random.randint(5, 50),
        momentum_multiplier=momentum,
        saturation_countdown=saturation_days,
        entry_window=entry_window,
        created_at=now,
        updated_at=now
    )

def generate_alert(product: Product, alert_type: str) -> Alert:
    """Generate an alert for a product"""
    messages = {
        "NEW_EXPLOSIVE": f"🔥 {product.name} just entered EXPLOSIVE zone with Alpha Score {product.alpha_score}!",
        "VELOCITY_SPIKE": f"⚡ Velocity spike detected on {product.name} - {random.randint(150, 400)}% growth in 24h!",
        "LOW_COMPETITION_HIGH_DEMAND": f"💎 Opportunity: {product.name} shows high demand with only {product.competition_density} competitors"
    }
    
    severities = {
        "NEW_EXPLOSIVE": "critical",
        "VELOCITY_SPIKE": "warning",
        "LOW_COMPETITION_HIGH_DEMAND": "info"
    }
    
    return Alert(
        product_id=product.id,
        product_name=product.name,
        alert_type=alert_type,
        message=messages.get(alert_type, f"Alert for {product.name}"),
        severity=severities.get(alert_type, "info"),
        created_at=datetime.now(timezone.utc).isoformat()
    )

# ============== API ENDPOINTS ==============

@api_router.get("/")
async def root():
    return {"message": "ALPHA DROP API - Product Intelligence Engine", "version": "1.0.0"}


async def require_subscription(request: Request):
    """Verify the caller has an active subscription. Raises 403 if not."""
    # Check admin JWT first (admin has full bypass)
    try:
        admin = await get_admin_user(request)
        if admin:
            # Return a lightweight user-like object for admin
            class AdminUser:
                email = admin["email"]
                user_id = "admin"
                name = "Admin"
            return AdminUser()
    except HTTPException:
        pass
    
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    sub = await db.user_subscriptions.find_one(
        {"user_email": user.email, "status": "active"}, {"_id": 0}
    )
    if not sub:
        raise HTTPException(status_code=403, detail="Active subscription required")
    return user


async def _ensure_products_exist():
    """Seed products if the DB is empty."""
    count = await db.products.count_documents({})
    if count < 50:
        products_to_insert = []
        for _ in range(6):
            products_to_insert.append(generate_product("EXPLOSIVE").model_dump())
        for _ in range(6):
            products_to_insert.append(generate_product("RISING").model_dump())
        for _ in range(6):
            products_to_insert.append(generate_product("EARLY_SIGNAL").model_dump())
        for _ in range(10):
            products_to_insert.append(generate_product("WATCHLIST").model_dump())
        for _ in range(8):
            products_to_insert.append(generate_product("AVOID").model_dump())
        # New v2.0 categories will be auto-classified by score
        for _ in range(14):
            products_to_insert.append(generate_product().model_dump())
        await db.products.insert_many(products_to_insert)


@api_router.get("/products", response_model=List[Product])
async def get_products(
    request: Request,
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    max_score: Optional[int] = Query(None, ge=0, le=100),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    """Get products with optional filters — requires active subscription"""
    await require_subscription(request)
    await _ensure_products_exist()
    
    # Build query
    query = {}
    if status:
        query["status"] = status
    if category:
        query["category"] = category
    if min_score is not None:
        query["alpha_score"] = {"$gte": min_score}
    if max_score is not None:
        if "alpha_score" in query:
            query["alpha_score"]["$lte"] = max_score
        else:
            query["alpha_score"] = {"$lte": max_score}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"category": {"$regex": search, "$options": "i"}}
        ]
    
    products = await db.products.find(query, {"_id": 0}).sort("alpha_score", -1).limit(limit).to_list(limit)
    return products

@api_router.get("/products/dashboard")
async def get_dashboard_products(request: Request):
    """Get products organized for dashboard display — requires active subscription"""
    await require_subscription(request)
    # Ensure products exist
    count = await db.products.count_documents({})
    if count < 50:
        await _ensure_products_exist()
    
    explosive = await db.products.find(
        {"status": {"$in": ["EXPLOSIVE", "SCALING_NOW"]}}, {"_id": 0}
    ).sort("alpha_score", -1).limit(5).to_list(5)
    
    exploding_soon = await db.products.find(
        {"status": "EXPLODING_SOON"}, {"_id": 0}
    ).sort("alpha_score", -1).limit(5).to_list(5)
    
    rising = await db.products.find(
        {"status": "RISING"}, {"_id": 0}
    ).sort("alpha_score", -1).limit(5).to_list(5)
    
    early_signals = await db.products.find(
        {"status": "EARLY_SIGNAL"}, {"_id": 0}
    ).sort("alpha_score", -1).limit(5).to_list(5)
    
    saturation_warnings = await db.products.find(
        {"status": "SATURATION_WARNING"}, {"_id": 0}
    ).sort("saturation_countdown", 1).limit(5).to_list(5)
    
    return {
        "explosive": explosive,
        "exploding_soon": exploding_soon,
        "rising": rising,
        "early_signals": early_signals,
        "saturation_warnings": saturation_warnings,
    }

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str, request: Request):
    """Get a single product by ID — requires active subscription"""
    await require_subscription(request)
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@api_router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(request: Request):
    """Get dashboard statistics — requires active subscription"""
    await require_subscription(request)
    total = await db.products.count_documents({})
    
    if total == 0:
        await _ensure_products_exist()
        total = await db.products.count_documents({})
    
    explosive_count = await db.products.count_documents({"status": "EXPLOSIVE"})
    rising_count = await db.products.count_documents({"status": "RISING"})
    early_signal_count = await db.products.count_documents({"status": "EARLY_SIGNAL"})
    
    # Calculate average alpha score
    pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$alpha_score"}}}]
    result = await db.products.aggregate(pipeline).to_list(1)
    avg_score = result[0]["avg"] if result else 0
    
    # Get top category
    category_pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    top_cat = await db.products.aggregate(category_pipeline).to_list(1)
    top_category = top_cat[0]["_id"] if top_cat else "N/A"
    
    return DashboardStats(
        total_products_tracked=total,
        explosive_count=explosive_count,
        rising_count=rising_count,
        early_signal_count=early_signal_count,
        avg_alpha_score=round(avg_score, 1),
        top_category=top_category
    )


@api_router.get("/ticker")
async def get_ticker(request: Request):
    """Get real-time ticker data — top movers for scrolling display. Requires subscription."""
    await require_subscription(request)
    products = await db.products.find(
        {"status": {"$in": ["EXPLOSIVE", "SCALING_NOW", "EXPLODING_SOON", "SATURATION_WARNING"]}},
        {"_id": 0, "id": 1, "name": 1, "alpha_score": 1, "status": 1, "momentum_multiplier": 1, "saturation_countdown": 1, "entry_window": 1}
    ).sort("alpha_score", -1).limit(20).to_list(20)
    return {"ticker": products}



@api_router.get("/alerts", response_model=List[Alert])
async def get_alerts(request: Request, limit: int = Query(20, ge=1, le=50)):
    """Get recent alerts — requires active subscription"""
    await require_subscription(request)
    # Generate alerts if none exist
    count = await db.alerts.count_documents({})
    
    if count < 10:
        # Generate some alerts based on explosive/rising products
        products = await db.products.find(
            {"status": {"$in": ["EXPLOSIVE", "RISING"]}}, {"_id": 0}
        ).limit(10).to_list(10)
        
        alerts_to_insert = []
        alert_types = ["NEW_EXPLOSIVE", "VELOCITY_SPIKE", "LOW_COMPETITION_HIGH_DEMAND"]
        
        for product in products:
            product_obj = Product(**product)
            alert = generate_alert(product_obj, random.choice(alert_types))
            alerts_to_insert.append(alert.model_dump())
        
        if alerts_to_insert:
            await db.alerts.insert_many(alerts_to_insert)
    
    alerts = await db.alerts.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return alerts

@api_router.post("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str, request: Request):
    """Mark an alert as read — requires active subscription"""
    await require_subscription(request)
    result = await db.alerts.update_one({"id": alert_id}, {"$set": {"read": True}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True}

@api_router.get("/categories")
async def get_categories():
    """Get all product categories"""
    return {"categories": CATEGORIES}

@api_router.post("/products/refresh")
async def refresh_products(request: Request):
    """Refresh product data — requires active subscription"""
    await require_subscription(request)
    # Clear existing products
    await db.products.delete_many({})
    await db.alerts.delete_many({})
    
    # Generate fresh data
    products_to_insert = []
    for _ in range(8):
        products_to_insert.append(generate_product("EXPLOSIVE").model_dump())
    for _ in range(10):
        products_to_insert.append(generate_product("RISING").model_dump())
    for _ in range(10):
        products_to_insert.append(generate_product("EARLY_SIGNAL").model_dump())
    for _ in range(12):
        products_to_insert.append(generate_product("WATCHLIST").model_dump())
    for _ in range(10):
        products_to_insert.append(generate_product("AVOID").model_dump())
    
    await db.products.insert_many(products_to_insert)
    
    return {"message": "Products refreshed", "count": len(products_to_insert)}

@api_router.get("/data-status")
async def get_data_status():
    """Check data source configuration status"""
    return {
        "scrape_creators_configured": bool(SCRAPE_CREATORS_API_KEY),
        "sociavault_configured": bool(SOCIAVAULT_API_KEY),
        "using_real_data": bool(SCRAPE_CREATORS_API_KEY or SOCIAVAULT_API_KEY),
        "data_mode": "LIVE" if (SCRAPE_CREATORS_API_KEY or SOCIAVAULT_API_KEY) else "SIMULATED",
        "message": "Add SCRAPE_CREATORS_API_KEY or SOCIAVAULT_API_KEY to .env for real TikTok Shop data"
    }


# ============== HOOK INTELLIGENCE ENDPOINTS ==============

@api_router.get("/hooks/intelligence")
async def get_hook_intelligence(request: Request):
    """Aggregate hook analysis data across all products — requires subscription"""
    await require_subscription(request)

    products = await db.products.find(
        {"status": {"$in": ["EXPLOSIVE", "RISING", "EARLY_SIGNAL"]}},
        {"_id": 0, "hook_analysis": 1, "top_videos": 1, "name": 1, "alpha_score": 1, "status": 1, "id": 1}
    ).limit(500).to_list(500)

    # Aggregate hooks by type
    hook_map = {}
    for p in products:
        for hook in p.get("hook_analysis", []):
            ht = hook["hook_type"]
            if ht not in hook_map:
                hook_map[ht] = {
                    "hook_type": ht,
                    "total_uses": 0,
                    "avg_effectiveness": 0,
                    "max_effectiveness": 0,
                    "effectiveness_sum": 0,
                    "examples": set(),
                    "top_products": [],
                }
            entry = hook_map[ht]
            entry["total_uses"] += 1
            entry["effectiveness_sum"] += hook["effectiveness"]
            entry["max_effectiveness"] = max(entry["max_effectiveness"], hook["effectiveness"])
            for ex in hook.get("examples", []):
                entry["examples"].add(ex)
            if len(entry["top_products"]) < 5:
                entry["top_products"].append({
                    "id": p["id"],
                    "name": p["name"],
                    "alpha_score": p["alpha_score"],
                    "status": p["status"],
                    "effectiveness": hook["effectiveness"],
                })

    hook_types = []
    for ht, data in hook_map.items():
        data["avg_effectiveness"] = round(data["effectiveness_sum"] / data["total_uses"], 1) if data["total_uses"] else 0
        data["examples"] = list(data["examples"])[:6]
        data["top_products"] = sorted(data["top_products"], key=lambda x: x["effectiveness"], reverse=True)[:5]
        del data["effectiveness_sum"]
        hook_types.append(data)

    hook_types.sort(key=lambda x: x["avg_effectiveness"], reverse=True)

    # Emotional triggers analysis
    emotional_triggers = [
        {"trigger": "Fear of Missing Out", "hook_types": ["FOMO", "Unboxing"], "power_score": 0, "count": 0},
        {"trigger": "Problem Awareness", "hook_types": ["Problem → Solution", "Convenience"], "power_score": 0, "count": 0},
        {"trigger": "Desire / Aspiration", "hook_types": ["Transformation", "Satisfaction"], "power_score": 0, "count": 0},
    ]
    for et in emotional_triggers:
        for ht in et["hook_types"]:
            if ht in hook_map:
                et["power_score"] += hook_map[ht].get("avg_effectiveness", 0)
                et["count"] += hook_map[ht]["total_uses"]
        et["power_score"] = round(et["power_score"] / max(len(et["hook_types"]), 1), 1)

    # Top performing videos with hooks
    top_videos = []
    for p in sorted(products, key=lambda x: x["alpha_score"], reverse=True)[:10]:
        for v in p.get("top_videos", [])[:2]:
            top_videos.append({
                "product_name": p["name"],
                "product_id": p["id"],
                "alpha_score": p["alpha_score"],
                "views": v.get("views", 0),
                "likes": v.get("likes", 0),
                "comments": v.get("comments", 0),
                "creator": v.get("creator", "unknown"),
                "hook": v.get("hook", ""),
            })
    top_videos.sort(key=lambda x: x["views"], reverse=True)

    return {
        "hook_types": hook_types,
        "emotional_triggers": emotional_triggers,
        "top_videos": top_videos[:20],
        "total_products_analyzed": len(products),
        "total_hooks_detected": sum(h["total_uses"] for h in hook_types),
    }


# ============== MARKET VALIDATION ENDPOINTS ==============

@api_router.get("/market/validation")
async def get_market_validation(request: Request):
    """Aggregate cross-platform market validation data — requires subscription"""
    await require_subscription(request)

    products = await db.products.find(
        {"status": {"$in": ["EXPLOSIVE", "RISING", "EARLY_SIGNAL"]}},
        {"_id": 0, "market_validation": 1, "name": 1, "alpha_score": 1, "status": 1, "category": 1, "id": 1, "price": 1, "total_sales": 1}
    ).limit(500).to_list(500)

    # Cross-platform opportunity matrix
    opportunities = []
    category_scores = {}
    platform_totals = {"tiktok_demand": 0, "amazon_demand": 0, "google_trends": 0}
    count = len(products) or 1

    for p in products:
        mv = p.get("market_validation", {})
        td = mv.get("tiktok_demand", 0)
        ad = mv.get("amazon_demand", 0)
        gt = mv.get("google_trends", 0)
        cps = mv.get("cross_platform_score", 0)

        platform_totals["tiktok_demand"] += td
        platform_totals["amazon_demand"] += ad
        platform_totals["google_trends"] += gt

        cat = p.get("category", "Unknown")
        if cat not in category_scores:
            category_scores[cat] = {"tiktok": 0, "amazon": 0, "google": 0, "cross_platform": 0, "count": 0}
        category_scores[cat]["tiktok"] += td
        category_scores[cat]["amazon"] += ad
        category_scores[cat]["google"] += gt
        category_scores[cat]["cross_platform"] += cps
        category_scores[cat]["count"] += 1

        # High-opportunity products: strong on TikTok but underrepresented on Amazon (arbitrage)
        gap = td - ad
        opportunities.append({
            "id": p["id"],
            "name": p["name"],
            "category": cat,
            "alpha_score": p["alpha_score"],
            "status": p["status"],
            "price": p.get("price", 0),
            "total_sales": p.get("total_sales", 0),
            "tiktok_demand": td,
            "amazon_demand": ad,
            "google_trends": gt,
            "cross_platform_score": cps,
            "arbitrage_gap": gap,
        })

    opportunities.sort(key=lambda x: x["arbitrage_gap"], reverse=True)

    # Category averages
    category_breakdown = []
    for cat, data in category_scores.items():
        c = data["count"] or 1
        category_breakdown.append({
            "category": cat,
            "avg_tiktok": round(data["tiktok"] / c, 1),
            "avg_amazon": round(data["amazon"] / c, 1),
            "avg_google": round(data["google"] / c, 1),
            "avg_cross_platform": round(data["cross_platform"] / c, 1),
            "product_count": data["count"],
        })
    category_breakdown.sort(key=lambda x: x["avg_cross_platform"], reverse=True)

    return {
        "platform_averages": {
            "tiktok_demand": round(platform_totals["tiktok_demand"] / count, 1),
            "amazon_demand": round(platform_totals["amazon_demand"] / count, 1),
            "google_trends": round(platform_totals["google_trends"] / count, 1),
        },
        "top_arbitrage_opportunities": opportunities[:15],
        "category_breakdown": category_breakdown,
        "total_products_analyzed": len(products),
    }

@api_router.post("/products/collect-live")
async def collect_live_products(query: str = Query("trending", description="Search query")):
    """Collect products from live TikTok Shop data (requires API keys)"""
    if not SCRAPE_CREATORS_API_KEY and not SOCIAVAULT_API_KEY:
        raise HTTPException(
            status_code=400, 
            detail="No data API keys configured. Add SCRAPE_CREATORS_API_KEY or SOCIAVAULT_API_KEY to backend/.env"
        )
    
    collected = []
    
    # Try Scrape Creators
    if SCRAPE_CREATORS_API_KEY:
        async with httpx.AsyncClient() as http_client:
            try:
                # Correct endpoint: /v1/tiktok/shop/search
                response = await http_client.get(
                    "https://api.scrapecreators.com/v1/tiktok/shop/search",
                    headers={"x-api-key": SCRAPE_CREATORS_API_KEY},
                    params={"query": query, "amount": 50},
                    timeout=60.0
                )
                logger.info(f"Scrape Creators response status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    # Handle different response formats
                    if isinstance(data, list):
                        collected.extend(data)
                    elif isinstance(data, dict):
                        collected.extend(data.get('products', data.get('results', data.get('data', []))))
                else:
                    logger.error(f"Scrape Creators error: {response.text}")
            except Exception as e:
                logger.error(f"Scrape Creators API error: {e}")
    
    # Fallback to SociaVault
    if not collected and SOCIAVAULT_API_KEY:
        async with httpx.AsyncClient() as http_client:
            try:
                response = await http_client.get(
                    "https://api.sociavault.com/v1/scrape/tiktok-shop/search",
                    headers={"x-api-key": SOCIAVAULT_API_KEY},
                    params={"query": query},
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    collected.extend(data.get('results', []))
            except Exception as e:
                logger.error(f"SociaVault API error: {e}")
    
    if not collected:
        return {
            "collected": 0,
            "products": [],
            "message": f"No products found for query: {query}. API may require different parameters or the query returned no results.",
            "api_configured": True
        }
    
    return {
        "collected": len(collected),
        "products": collected[:20],  # Return first 20 as preview
        "message": f"Collected {len(collected)} products for query: {query}"
    }


def transform_live_product(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Transform raw API product data to our Product schema"""
    
    # Extract data from API response
    sold_count = raw.get('sold_info', {}).get('sold_count', 0) if isinstance(raw.get('sold_info'), dict) else 0
    
    # Get video stats if available
    video_data = raw.get('video', {}) or {}
    stats = video_data.get('statistics', {}) if isinstance(video_data, dict) else {}
    views = stats.get('play_count', 0)
    likes = stats.get('digg_count', 0)
    comments = stats.get('comment_count', 0)
    shares = stats.get('share_count', 0)
    
    # Get price
    price_info = raw.get('product_price_info', {}) or {}
    price = float(price_info.get('sale_price_decimal', 0) or 0)
    
    # Get rating
    rate_info = raw.get('rate_info', {}) or {}
    rating = rate_info.get('score', 0)
    
    # Get category
    breadcrumb = raw.get('category_breadcrumb', []) or []
    category = breadcrumb[0].get('category_name', 'Uncategorized') if breadcrumb else 'Beauty & Skincare'
    
    # Get image
    image_info = raw.get('image', {}) or {}
    image_urls = image_info.get('url_list', [])
    image_url = image_urls[0] if image_urls else ""
    
    # Calculate Alpha Score based on real metrics (adjusted for better distribution)
    # Velocity based on sold count - more generous thresholds
    if sold_count >= 100000:
        velocity_score = 95
    elif sold_count >= 50000:
        velocity_score = 85
    elif sold_count >= 10000:
        velocity_score = 75
    elif sold_count >= 5000:
        velocity_score = 65
    elif sold_count >= 1000:
        velocity_score = 55
    else:
        velocity_score = 40
    
    # Engagement score based on video metrics
    if views > 0:
        engagement_rate = (likes + comments) / views
        if engagement_rate >= 0.05:  # 5%+ engagement
            engagement_score = 95
        elif engagement_rate >= 0.03:
            engagement_score = 85
        elif engagement_rate >= 0.01:
            engagement_score = 70
        else:
            engagement_score = 55
    else:
        engagement_score = 55
    
    # Views score - more generous
    if views >= 1000000:
        views_bonus = 25
    elif views >= 500000:
        views_bonus = 20
    elif views >= 100000:
        views_bonus = 15
    elif views >= 50000:
        views_bonus = 10
    else:
        views_bonus = 5
    
    creator_score = min(100, 65 + views_bonus)  # Base + views bonus
    hook_score = min(100, (comments / max(likes, 1)) * 400 + 55) if likes > 0 else 55
    saturation_score = 30  # Assume lower saturation (better)
    market_score = 70  # Higher base market score
    repeatability_score = min(100, (rating or 4.0) * 22) if rating else 75
    
    # Weighted Alpha Score - adjusted for more Explosive products
    alpha_score = int(
        velocity_score * 0.35 +      # Sales volume most important
        engagement_score * 0.20 +     # Engagement quality
        creator_score * 0.15 +        # Creator adoption
        hook_score * 0.08 +           # Hook effectiveness
        market_score * 0.08 +         # Market expansion
        (100 - saturation_score) * 0.07 +  # Low saturation bonus
        repeatability_score * 0.07    # Repeatability
    )
    alpha_score = min(100, max(0, alpha_score))
    
    # Determine status with MORE GENEROUS thresholds for more Explosive products
    if alpha_score >= 72:
        status = "EXPLOSIVE"
    elif alpha_score >= 58:
        status = "RISING"
    elif alpha_score >= 45:
        status = "EARLY_SIGNAL"
    elif alpha_score >= 35:
        status = "WATCHLIST"
    else:
        status = "AVOID"
    
    # Generate reason based on real data
    reasons = []
    if sold_count > 100000:
        reasons.append(f"Massive sales: {sold_count:,} units sold")
    elif sold_count > 10000:
        reasons.append(f"Strong sales: {sold_count:,} units")
    elif sold_count > 1000:
        reasons.append(f"Growing sales: {sold_count:,} units")
    if views > 1000000:
        reasons.append(f"Viral reach: {views/1000000:.1f}M views")
    elif views > 100000:
        reasons.append(f"Strong views: {views/1000:.0f}K")
    if rating and rating >= 4.5:
        reasons.append(f"Highly rated: {rating}⭐")
    if not reasons:
        reasons.append("Trending on TikTok Shop")
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Build trend data from stats
    trend_data = []
    base_sales = max(1, sold_count // 14)
    for i in range(14):
        mult = 1 + (i * 0.05) + random.uniform(-0.1, 0.1)
        trend_data.append({
            "date": (datetime.now(timezone.utc) - timedelta(days=14-i-1)).strftime("%Y-%m-%d"),
            "sales": int(base_sales * mult),
            "views": int((views / 14) * mult) if views else random.randint(1000, 10000),
            "creators": random.randint(5, 50),
            "engagement": round(random.uniform(3, 12), 2)
        })
    
    # Extract hook from video description
    video_desc = video_data.get('desc', '') if isinstance(video_data, dict) else ''
    hook_examples = [video_desc[:100] + "..."] if video_desc else ["Check out this product!"]
    
    return {
        "id": raw.get('product_id', str(uuid.uuid4())),
        "name": raw.get('title', 'Unknown Product')[:100],
        "category": category,
        "image_url": image_url,
        "price": price,
        "alpha_score": alpha_score,
        "score_breakdown": {
            "velocity_score": velocity_score,
            "creator_adoption_score": creator_score,
            "engagement_quality_score": engagement_score,
            "hook_strength_score": hook_score,
            "market_expansion_score": market_score,
            "saturation_risk_score": saturation_score,
            "repeatability_score": repeatability_score
        },
        "status": status,
        "trend_direction": "up" if sold_count > 10000 else ("stable" if sold_count > 1000 else "down"),
        "risk_level": "low" if status == "EXPLOSIVE" else ("medium" if status in ["RISING", "EARLY_SIGNAL"] else "high"),
        "reason": " • ".join(reasons),
        "total_sales": sold_count,
        "total_views": views,
        "creator_count": random.randint(10, 100),
        "avg_engagement": round((likes + comments) / max(views, 1) * 100, 2) if views else 5.0,
        "trend_data": trend_data,
        "hook_analysis": [
            {
                "hook_type": "Transformation",
                "description": "Before/after demonstration driving engagement",
                "effectiveness": random.randint(70, 95),
                "examples": hook_examples
            },
            {
                "hook_type": "Problem → Solution",
                "description": "Addressing common pain points",
                "effectiveness": random.randint(65, 90),
                "examples": ["Finally a solution that works!", "Say goodbye to..."]
            }
        ],
        "market_validation": {
            "tiktok_demand": min(100, int(sold_count / 5000) + 40) if sold_count else 50,
            "amazon_demand": random.randint(40, 80),
            "google_trends": random.randint(30, 70),
            "cross_platform_score": random.randint(50, 85)
        },
        "top_videos": [
            {
                "id": video_data.get('aweme_id', 'unknown') if isinstance(video_data, dict) else 'unknown',
                "views": views,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "creator": video_data.get('author', {}).get('nickname', 'Unknown') if isinstance(video_data, dict) else 'Unknown',
                "hook": video_desc[:50] if video_desc else "Product showcase",
                "posted_days_ago": random.randint(1, 14)
            }
        ],
        "competition_density": random.randint(20, 80),
        "tiktok_shop_url": raw.get('seo_url', {}).get('canonical_url', '') if isinstance(raw.get('seo_url'), dict) else '',
        "created_at": now,
        "updated_at": now
    }


@api_router.post("/products/load-real-data")
async def load_real_data():
    """Load real TikTok Shop data and replace simulated data"""
    if not SCRAPE_CREATORS_API_KEY:
        raise HTTPException(status_code=400, detail="SCRAPE_CREATORS_API_KEY not configured")
    
    all_products = []
    search_queries = ["skincare", "beauty", "gadgets", "home kitchen", "fashion", "wellness"]
    
    async with httpx.AsyncClient() as http_client:
        for query in search_queries:
            try:
                response = await http_client.get(
                    "https://api.scrapecreators.com/v1/tiktok/shop/search",
                    headers={"x-api-key": SCRAPE_CREATORS_API_KEY},
                    params={"query": query, "amount": 20},
                    timeout=60.0
                )
                if response.status_code == 200:
                    data = response.json()
                    products = data if isinstance(data, list) else data.get('products', data.get('results', []))
                    for raw_product in products:
                        try:
                            transformed = transform_live_product(raw_product)
                            all_products.append(transformed)
                        except Exception as e:
                            logger.error(f"Failed to transform product: {e}")
            except Exception as e:
                logger.error(f"Failed to fetch {query}: {e}")
    
    if not all_products:
        raise HTTPException(status_code=500, detail="Failed to load any real data")
    
    # Clear old data and insert new
    await db.products.delete_many({})
    await db.alerts.delete_many({})
    await db.products.insert_many(all_products)
    
    # Generate alerts for top products
    explosive_products = [p for p in all_products if p['status'] == 'EXPLOSIVE'][:5]
    alerts_to_insert = []
    for product in explosive_products:
        alert = {
            "id": str(uuid.uuid4()),
            "product_id": product['id'],
            "product_name": product['name'],
            "alert_type": "NEW_EXPLOSIVE",
            "message": f"🔥 {product['name'][:50]} is EXPLOSIVE with {product['total_sales']:,} sales!",
            "severity": "critical",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "read": False
        }
        alerts_to_insert.append(alert)
    
    if alerts_to_insert:
        await db.alerts.insert_many(alerts_to_insert)
    
    return {
        "message": "Real data loaded successfully!",
        "total_products": len(all_products),
        "explosive": len([p for p in all_products if p['status'] == 'EXPLOSIVE']),
        "rising": len([p for p in all_products if p['status'] == 'RISING']),
        "early_signals": len([p for p in all_products if p['status'] == 'EARLY_SIGNAL']),
        "data_source": "TikTok Shop (via Scrape Creators API)"
    }


# ============== STRIPE SUBSCRIPTION ENDPOINTS ==============

@api_router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    return {"plans": SUBSCRIPTION_PLANS}


@api_router.get("/subscription/check")
async def check_subscription(email: str = Query(...)):
    """Check if a user has an active subscription"""
    sub = await db.user_subscriptions.find_one(
        {"user_email": email, "status": "active"},
        {"_id": 0}
    )
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription")
    
    # Check if subscription has expired
    expires_at = sub.get("expires_at", "")
    if expires_at:
        try:
            exp_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            if exp_dt < datetime.now(timezone.utc):
                await db.user_subscriptions.update_one(
                    {"user_email": email, "status": "active"},
                    {"$set": {"status": "expired"}}
                )
                raise HTTPException(status_code=404, detail="Subscription expired")
        except ValueError:
            pass
    
    return {
        "status": sub["status"],
        "plan_id": sub.get("plan_id"),
        "plan_name": sub.get("plan_name"),
        "expires_at": sub.get("expires_at")
    }



@api_router.post("/checkout/create")
async def create_checkout_session(
    request: Request,
    plan_id: str = Query(..., description="Plan ID: scout, hunter, or predator"),
    user_email: Optional[str] = Query(None, description="User email for subscription")
):
    """Create a Stripe checkout session for subscription"""
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan ID")
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    plan = SUBSCRIPTION_PLANS[plan_id]
    
    # Get origin URL from request
    origin_url = str(request.base_url).rstrip('/')
    # Handle preview URLs
    if 'preview.emergentagent.com' in origin_url:
        # Use the frontend URL pattern
        frontend_origin = origin_url.replace('/api', '').replace(':8001', '')
    else:
        frontend_origin = origin_url
    
    success_url = f"{frontend_origin}/?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{frontend_origin}/?payment=cancelled"
    webhook_url = f"{origin_url}api/webhook/stripe"
    
    try:
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        checkout_request = CheckoutSessionRequest(
            amount=plan['price'],
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "plan_id": plan_id,
                "plan_name": plan['name'],
                "user_email": user_email or "anonymous"
            }
        )
        
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        transaction = {
            "id": str(uuid.uuid4()),
            "session_id": session.session_id,
            "user_email": user_email,
            "plan_id": plan_id,
            "amount": plan['price'],
            "currency": "usd",
            "status": "pending",
            "payment_status": "initiated",
            "metadata": {"plan_name": plan['name']},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.payment_transactions.insert_one(transaction)
        
        return {
            "checkout_url": session.url,
            "session_id": session.session_id,
            "plan": plan
        }
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/checkout/status/{session_id}")
async def get_checkout_status(request: Request, session_id: str):
    """Get the status of a checkout session"""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    try:
        origin_url = str(request.base_url).rstrip('/')
        webhook_url = f"{origin_url}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction in database
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "status": status.status,
                    "payment_status": status.payment_status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # If payment successful, create subscription
        if status.payment_status == "paid":
            transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
            if transaction:
                # Check if subscription already exists
                existing = await db.user_subscriptions.find_one({"payment_session_id": session_id})
                if not existing:
                    subscription = {
                        "id": str(uuid.uuid4()),
                        "user_email": transaction.get("user_email") or status.metadata.get("user_email"),
                        "plan_id": transaction["plan_id"],
                        "plan_name": SUBSCRIPTION_PLANS[transaction["plan_id"]]["name"],
                        "status": "active",
                        "started_at": datetime.now(timezone.utc).isoformat(),
                        "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                        "payment_session_id": session_id
                    }
                    await db.user_subscriptions.insert_one(subscription)
        
        return {
            "status": status.status,
            "payment_status": status.payment_status,
            "amount_total": status.amount_total,
            "currency": status.currency,
            "metadata": status.metadata
        }
    except Exception as e:
        logger.error(f"Checkout status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        origin_url = str(request.base_url).rstrip('/')
        webhook_url = f"{origin_url}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Update transaction based on webhook
        if webhook_response.session_id:
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {
                    "$set": {
                        "status": webhook_response.event_type,
                        "payment_status": webhook_response.payment_status,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
        
        return {"received": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"received": True, "error": str(e)}


# ============== WATCHLIST ENDPOINTS ==============

@api_router.get("/watchlist/{user_id}")
async def get_watchlist(user_id: str):
    """Get user's watchlist"""
    items = await db.watchlist.find({"user_id": user_id}, {"_id": 0}).to_list(100)
    return {"watchlist": items}

@api_router.post("/watchlist/add")
async def add_to_watchlist(
    user_id: str = Query(...),
    product_id: str = Query(...),
    notes: Optional[str] = Query(None)
):
    """Add a product to user's watchlist"""
    # Check if already in watchlist
    existing = await db.watchlist.find_one({"user_id": user_id, "product_id": product_id})
    if existing:
        raise HTTPException(status_code=400, detail="Product already in watchlist")
    
    # Get product details
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    watchlist_item = WatchlistItem(
        user_id=user_id,
        product_id=product_id,
        product_name=product["name"],
        product_image=product["image_url"],
        alpha_score=product["alpha_score"],
        status=product["status"],
        added_at=datetime.now(timezone.utc).isoformat(),
        notes=notes
    )
    
    # Insert using model_dump to ensure proper serialization
    await db.watchlist.insert_one(watchlist_item.model_dump())
    return {"message": "Added to watchlist", "item": watchlist_item.model_dump()}

@api_router.delete("/watchlist/remove")
async def remove_from_watchlist(
    user_id: str = Query(...),
    product_id: str = Query(...)
):
    """Remove a product from user's watchlist"""
    result = await db.watchlist.delete_one({"user_id": user_id, "product_id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found in watchlist")
    return {"message": "Removed from watchlist"}

@api_router.put("/watchlist/notes")
async def update_watchlist_notes(
    user_id: str = Query(...),
    product_id: str = Query(...),
    notes: str = Query(...)
):
    """Update notes for a watchlist item"""
    result = await db.watchlist.update_one(
        {"user_id": user_id, "product_id": product_id},
        {"$set": {"notes": notes}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found in watchlist")
    return {"message": "Notes updated"}


# ============== CRON JOB ENDPOINT ==============

@api_router.post("/cron/refresh-data")
async def cron_refresh_data(api_key: str = Query(None)):
    """Endpoint for cron job to refresh data daily - can be called by external scheduler"""
    # Simple API key check for cron security
    expected_key = os.environ.get('CRON_API_KEY', 'alpha-drop-cron-2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid cron API key")
    
    if not SCRAPE_CREATORS_API_KEY:
        return {"error": "No data API configured"}
    
    # Reuse the load real data logic
    all_products = []
    search_queries = ["skincare", "beauty", "gadgets", "home kitchen", "fashion", "wellness", "tech", "fitness"]
    
    async with httpx.AsyncClient() as http_client:
        for query in search_queries:
            try:
                response = await http_client.get(
                    "https://api.scrapecreators.com/v1/tiktok/shop/search",
                    headers={"x-api-key": SCRAPE_CREATORS_API_KEY},
                    params={"query": query, "amount": 25},
                    timeout=60.0
                )
                if response.status_code == 200:
                    data = response.json()
                    products = data if isinstance(data, list) else data.get('products', data.get('results', []))
                    for raw_product in products:
                        try:
                            transformed = transform_live_product(raw_product)
                            all_products.append(transformed)
                        except Exception as e:
                            logger.error(f"Failed to transform product: {e}")
            except Exception as e:
                logger.error(f"Failed to fetch {query}: {e}")
    
    if all_products:
        await db.products.delete_many({})
        await db.products.insert_many(all_products)
        
        # Send email alerts for new explosive products
        explosive_products = [p for p in all_products if p['status'] == 'EXPLOSIVE'][:5]
        if explosive_products and RESEND_API_KEY:
            await send_explosive_alerts_to_subscribers(explosive_products)
        
        logger.info(f"Cron job refreshed {len(all_products)} products")

        # Take daily snapshot for historical tracking
        try:
            from routes.history import router as _hr
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            existing_snap = await db.daily_snapshots.find_one({"date": date_str})
            if not existing_snap:
                snap = {
                    "date": date_str,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_products": len(all_products),
                    "explosive": len([p for p in all_products if p.get("status") == "EXPLOSIVE"]),
                    "rising": len([p for p in all_products if p.get("status") == "RISING"]),
                    "early_signal": len([p for p in all_products if p.get("status") == "EARLY_SIGNAL"]),
                    "avg_alpha_score": round(sum(p.get("alpha_score", 0) for p in all_products) / max(len(all_products), 1), 1),
                    "active_subscribers": await db.user_subscriptions.count_documents({"status": "active"}),
                }
                await db.daily_snapshots.insert_one(snap)
                history_docs = [{
                    "product_id": p["id"], "date": date_str,
                    "alpha_score": p.get("alpha_score", 0), "status": p.get("status", ""),
                    "total_sales": p.get("total_sales", 0), "creator_count": p.get("creator_count", 0),
                    "price": p.get("price", 0),
                } for p in all_products]
                if history_docs:
                    await db.product_history.insert_many(history_docs)
                logger.info(f"Daily snapshot taken: {date_str}")
        except Exception as snap_err:
            logger.error(f"Snapshot error: {snap_err}")

        return {
            "success": True,
            "products_loaded": len(all_products),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    return {"success": False, "error": "No products loaded"}


# ============== WEEKLY WINNERS REPORT ==============

def generate_weekly_report_email(
    top_explosive: List[Dict],
    biggest_movers: List[Dict],
    new_early_signals: List[Dict],
    hook_of_the_week: Dict,
    app_url: str = "",
) -> str:
    """Generate rich HTML email for the Weekly Winners Report."""

    def product_row(p, highlight_field=None):
        extra = ""
        if highlight_field == "velocity":
            vel = p.get("score_breakdown", {}).get("velocity_score", 0)
            extra = f'<span style="color:#FFD700;font-size:12px;">Velocity {vel}/100</span>'
        elif highlight_field == "early":
            extra = '<span style="color:#00BFFF;font-size:12px;">New signal</span>'
        return f"""
        <tr>
            <td style="padding:12px 15px;border-bottom:1px solid #222;">
                <h3 style="margin:0;color:#fff;font-size:14px;">{p['name'][:55]}</h3>
                <p style="margin:4px 0 0;color:#888;font-size:11px;">{p.get('category','')} &middot; ${p.get('price',0):.2f}</p>
            </td>
            <td style="padding:12px 15px;border-bottom:1px solid #222;text-align:center;">
                <span style="background:rgba(0,255,148,0.1);color:#00FF94;padding:6px 14px;font-weight:bold;font-size:18px;">
                    {p.get('alpha_score',0)}
                </span>
            </td>
            <td style="padding:12px 15px;border-bottom:1px solid #222;text-align:right;">
                <span style="color:#fff;">{p.get('total_sales',0):,} sold</span><br>
                {extra}
            </td>
        </tr>"""

    def section(title, subtitle, rows_html, accent="#00FF94"):
        return f"""
        <tr>
            <td style="padding:25px 15px 10px;">
                <h2 style="margin:0;color:{accent};font-size:18px;text-transform:uppercase;letter-spacing:2px;">{title}</h2>
                <p style="margin:4px 0 0;color:#888;font-size:12px;">{subtitle}</p>
            </td>
        </tr>
        <tr>
            <td style="padding:0 15px;">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr style="background:#111;">
                        <td style="padding:8px 15px;color:#666;font-size:10px;text-transform:uppercase;letter-spacing:1px;">Product</td>
                        <td style="padding:8px 15px;color:#666;font-size:10px;text-transform:uppercase;text-align:center;">Alpha</td>
                        <td style="padding:8px 15px;color:#666;font-size:10px;text-transform:uppercase;text-align:right;">Data</td>
                    </tr>
                    {rows_html}
                </table>
            </td>
        </tr>"""

    explosive_rows = "".join(product_row(p) for p in top_explosive[:5])
    mover_rows = "".join(product_row(p, "velocity") for p in biggest_movers[:5])
    early_rows = "".join(product_row(p, "early") for p in new_early_signals[:5])

    hook_section = ""
    if hook_of_the_week:
        examples_html = "".join(
            f'<li style="color:#ccc;margin:4px 0;font-style:italic;">"{ex}"</li>'
            for ex in hook_of_the_week.get("examples", [])[:3]
        )
        hook_section = f"""
        <tr>
            <td style="padding:25px 15px 10px;">
                <h2 style="margin:0;color:#FFD700;font-size:18px;text-transform:uppercase;letter-spacing:2px;">Hook of the Week</h2>
                <p style="margin:4px 0 0;color:#888;font-size:12px;">The highest-performing content angle this week</p>
            </td>
        </tr>
        <tr>
            <td style="padding:0 15px 20px;">
                <div style="background:#111;border:1px solid #333;padding:20px;">
                    <h3 style="margin:0;color:#FFD700;font-size:16px;">{hook_of_the_week.get('hook_type','')}</h3>
                    <p style="color:#aaa;font-size:13px;margin:8px 0;">
                        Avg effectiveness: <strong style="color:#00FF94;">{hook_of_the_week.get('avg_effectiveness',0)}%</strong>
                        &middot; Used by {hook_of_the_week.get('total_uses',0)} products
                    </p>
                    <ul style="padding-left:20px;margin:10px 0 0;">{examples_html}</ul>
                </div>
            </td>
        </tr>"""

    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
    <body style="margin:0;padding:0;background:#000;font-family:Arial,Helvetica,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#000;">
            <tr><td align="center" style="padding:40px 20px;">
                <table width="600" cellpadding="0" cellspacing="0" style="background:#050505;border:1px solid #222;">
                    <!-- Header -->
                    <tr>
                        <td style="padding:30px;border-bottom:2px solid #00FF94;">
                            <h1 style="margin:0;color:#00FF94;font-size:22px;letter-spacing:2px;text-transform:uppercase;">
                                ALPHA DROP &mdash; Weekly Winners
                            </h1>
                            <p style="margin:8px 0 0;color:#888;font-size:13px;">
                                Your weekly intelligence briefing &middot; {datetime.now(timezone.utc).strftime('%B %d, %Y')}
                            </p>
                        </td>
                    </tr>

                    {section("Top 5 Explosive Products", "Highest Alpha Scores this week", explosive_rows, "#00FF94")}
                    {section("Biggest Movers", "Fastest velocity acceleration", mover_rows, "#FFD700")}
                    {section("New Early Signals", "Fresh opportunities entering the radar", early_rows, "#00BFFF")}
                    {hook_section}

                    <!-- CTA -->
                    <tr>
                        <td style="padding:30px;text-align:center;">
                            <a href="{app_url}"
                               style="display:inline-block;background:#00FF94;color:#000;padding:14px 32px;text-decoration:none;font-weight:bold;text-transform:uppercase;letter-spacing:1px;">
                                Open Full Dashboard
                            </a>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding:20px;border-top:1px solid #222;text-align:center;">
                            <p style="margin:0;color:#666;font-size:11px;">
                                You're receiving this because you have an active ALPHA DROP subscription.<br>
                                <a href="#" style="color:#888;">Unsubscribe</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td></tr>
        </table>
    </body>
    </html>
    """


@api_router.post("/cron/weekly-report")
async def cron_weekly_report(api_key: str = Query(None)):
    """Send weekly winners report to all active subscribers. Trigger manually via cron-job.org."""
    expected_key = os.environ.get('CRON_API_KEY', 'alpha-drop-cron-2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid cron API key")

    if not RESEND_API_KEY:
        raise HTTPException(status_code=500, detail="Email service not configured")

    # 1) Top 5 explosive
    top_explosive = await db.products.find(
        {"status": "EXPLOSIVE"}, {"_id": 0}
    ).sort("alpha_score", -1).limit(5).to_list(5)

    # 2) Biggest movers — highest velocity score
    biggest_movers = await db.products.find(
        {"status": {"$in": ["EXPLOSIVE", "RISING"]}}, {"_id": 0}
    ).sort("score_breakdown.velocity_score", -1).limit(5).to_list(5)

    # 3) New early signals
    new_early_signals = await db.products.find(
        {"status": "EARLY_SIGNAL"}, {"_id": 0}
    ).sort("alpha_score", -1).limit(5).to_list(5)

    # 4) Hook of the week — aggregate best hook type
    products_for_hooks = await db.products.find(
        {"status": {"$in": ["EXPLOSIVE", "RISING"]}},
        {"_id": 0, "hook_analysis": 1}
    ).to_list(500)

    hook_agg = {}
    for p in products_for_hooks:
        for h in p.get("hook_analysis", []):
            ht = h["hook_type"]
            if ht not in hook_agg:
                hook_agg[ht] = {"hook_type": ht, "total_uses": 0, "eff_sum": 0, "examples": set()}
            hook_agg[ht]["total_uses"] += 1
            hook_agg[ht]["eff_sum"] += h["effectiveness"]
            for ex in h.get("examples", []):
                hook_agg[ht]["examples"].add(ex)

    hook_of_the_week = None
    if hook_agg:
        for v in hook_agg.values():
            v["avg_effectiveness"] = round(v["eff_sum"] / v["total_uses"], 1) if v["total_uses"] else 0
            v["examples"] = list(v["examples"])[:4]
        hook_of_the_week = max(hook_agg.values(), key=lambda x: x["avg_effectiveness"])

    # Build email
    html = generate_weekly_report_email(top_explosive, biggest_movers, new_early_signals, hook_of_the_week, app_url=APP_URL)

    # Send to all active subscribers
    active_subs = await db.user_subscriptions.find(
        {"status": "active"}, {"_id": 0, "user_email": 1}
    ).to_list(5000)

    sent_count = 0
    errors = []
    seen_emails = set()
    for sub in active_subs:
        email = sub.get("user_email")
        if not email or email in seen_emails or email == "anonymous":
            continue
        seen_emails.add(email)
        success = await send_email(email, "ALPHA DROP Weekly Winners Report", html)
        if success:
            sent_count += 1
        else:
            errors.append(email)

    # Log the send
    await db.weekly_reports.insert_one({
        "id": str(uuid.uuid4()),
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "recipients": sent_count,
        "errors": len(errors),
        "top_explosive_count": len(top_explosive),
        "hook_of_week": hook_of_the_week.get("hook_type") if hook_of_the_week else None,
    })

    logger.info(f"Weekly report sent to {sent_count} subscribers ({len(errors)} errors)")
    return {
        "success": True,
        "sent_to": sent_count,
        "errors": len(errors),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ============== AUTHENTICATION ENDPOINTS ==============

async def get_current_user(request: Request) -> Optional[User]:
    """Get current user from session token in cookie or header"""
    # Check cookie first
    session_token = request.cookies.get("session_token")
    
    # Fallback to Authorization header
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    
    if not session_token:
        return None
    
    # Find session
    session_doc = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session_doc:
        return None
    
    # Check expiry
    expires_at = session_doc.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return None
    
    # Get user
    user_doc = await db.users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
    if not user_doc:
        return None
    
    return User(**user_doc)


@api_router.post("/auth/session")
async def exchange_session(request: Request, response: Response, session_id: str = Query(...)):
    """Exchange session_id from OAuth callback for session_token"""
    try:
        # Call Emergent Auth to get user data
        async with httpx.AsyncClient() as http_client:
            auth_response = await http_client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id},
                timeout=30.0
            )
            
            if auth_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session")
            
            user_data = auth_response.json()
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_data["email"]}, {"_id": 0})
        
        now = datetime.now(timezone.utc).isoformat()
        
        if existing_user:
            user_id = existing_user["user_id"]
            # Update user data
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {
                    "name": user_data["name"],
                    "picture": user_data.get("picture"),
                    "updated_at": now
                }}
            )
        else:
            # Create new user
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            new_user = {
                "user_id": user_id,
                "email": user_data["email"],
                "name": user_data["name"],
                "picture": user_data.get("picture"),
                "email_notifications": True,
                "created_at": now,
                "updated_at": now
            }
            await db.users.insert_one(new_user)
        
        # Create session
        session_token = user_data.get("session_token", f"sess_{uuid.uuid4().hex}")
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        
        session_doc = {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at,
            "created_at": now
        }
        
        # Remove old sessions for this user
        await db.user_sessions.delete_many({"user_id": user_id})
        await db.user_sessions.insert_one(session_doc)
        
        # Set cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=7 * 24 * 60 * 60,
            path="/"
        )
        
        # Get full user data
        user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
        
        return {"user": user_doc, "session_token": session_token}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/auth/me")
async def get_me(request: Request):
    """Get current authenticated user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user.model_dump()


@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout user and clear session"""
    session_token = request.cookies.get("session_token")
    
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    
    return {"message": "Logged out successfully"}


@api_router.put("/auth/settings")
async def update_user_settings(
    request: Request,
    email_notifications: Optional[bool] = Query(None)
):
    """Update user settings"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    updates = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if email_notifications is not None:
        updates["email_notifications"] = email_notifications
    
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": updates}
    )
    
    return {"message": "Settings updated"}


# ============== EMAIL NOTIFICATION ENDPOINTS ==============

async def send_email(recipient: str, subject: str, html_content: str) -> bool:
    """Send email using Resend API"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not configured")
        return False
    
    try:
        params = {
            "from": SENDER_EMAIL,
            "to": [recipient],
            "subject": subject,
            "html": html_content
        }
        
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {recipient}: {email.get('id')}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}")
        return False


def generate_explosive_alert_email(products: List[Dict], app_url: str = "") -> str:
    """Generate HTML email for explosive product alerts"""
    products_html = ""
    for p in products[:5]:
        products_html += f"""
        <tr>
            <td style="padding: 15px; border-bottom: 1px solid #222;">
                <div style="display: flex; align-items: center;">
                    <div>
                        <h3 style="margin: 0; color: #00FF94; font-size: 16px;">{p['name'][:50]}</h3>
                        <p style="margin: 5px 0 0; color: #888; font-size: 12px;">{p['category']}</p>
                    </div>
                </div>
            </td>
            <td style="padding: 15px; border-bottom: 1px solid #222; text-align: center;">
                <span style="background: rgba(0,255,148,0.1); color: #00FF94; padding: 8px 16px; font-weight: bold; font-size: 20px;">
                    {p['alpha_score']}
                </span>
            </td>
            <td style="padding: 15px; border-bottom: 1px solid #222; text-align: right; color: #fff;">
                ${p['price']:.2f}<br>
                <span style="color: #888; font-size: 12px;">{p['total_sales']:,} sold</span>
            </td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #000; font-family: Arial, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #000;">
            <tr>
                <td align="center" style="padding: 40px 20px;">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #050505; border: 1px solid #222;">
                        <!-- Header -->
                        <tr>
                            <td style="padding: 30px; border-bottom: 1px solid #222;">
                                <h1 style="margin: 0; color: #00FF94; font-size: 24px;">
                                    🔥 ALPHA DROP Alert
                                </h1>
                                <p style="margin: 10px 0 0; color: #888;">
                                    New EXPLOSIVE products detected!
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Products Table -->
                        <tr>
                            <td style="padding: 0;">
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr style="background: #111;">
                                        <td style="padding: 10px 15px; color: #666; font-size: 12px; text-transform: uppercase;">Product</td>
                                        <td style="padding: 10px 15px; color: #666; font-size: 12px; text-transform: uppercase; text-align: center;">Alpha Score</td>
                                        <td style="padding: 10px 15px; color: #666; font-size: 12px; text-transform: uppercase; text-align: right;">Price / Sales</td>
                                    </tr>
                                    {products_html}
                                </table>
                            </td>
                        </tr>
                        
                        <!-- CTA -->
                        <tr>
                            <td style="padding: 30px; text-align: center;">
                                <p style="color: #888; margin: 0 0 20px;">
                                    These products are showing viral signals. Consider testing within 24-48 hours.
                                </p>
                                <a href="{app_url}" 
                                   style="display: inline-block; background: #00FF94; color: #000; padding: 15px 30px; text-decoration: none; font-weight: bold; text-transform: uppercase;">
                                    View Full Analysis
                                </a>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 20px; border-top: 1px solid #222; text-align: center;">
                                <p style="margin: 0; color: #666; font-size: 12px;">
                                    You're receiving this because you enabled email alerts on ALPHA DROP.<br>
                                    <a href="#" style="color: #888;">Unsubscribe</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


async def send_explosive_alerts_to_subscribers(products: List[Dict]):
    """Send email alerts to all subscribers with email notifications enabled"""
    subscribers = await db.users.find(
        {"email_notifications": True},
        {"_id": 0, "email": 1}
    ).to_list(1000)
    
    if not subscribers:
        logger.info("No subscribers with email notifications enabled")
        return
    
    subject = f"🔥 {len(products)} New EXPLOSIVE Products Detected!"
    html_content = generate_explosive_alert_email(products, app_url=APP_URL)
    
    for subscriber in subscribers:
        await send_email(subscriber["email"], subject, html_content)
    
    logger.info(f"Sent explosive alerts to {len(subscribers)} subscribers")


@api_router.post("/notifications/test")
async def send_test_notification(request: Request):
    """Send a test email notification to the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get some explosive products for the test
    products = await db.products.find(
        {"status": "EXPLOSIVE"},
        {"_id": 0}
    ).limit(3).to_list(3)
    
    if not products:
        products = [{"name": "Test Product", "category": "Test", "alpha_score": 85, "price": 29.99, "total_sales": 10000}]
    
    subject = "🔥 ALPHA DROP Test Alert"
    html_content = generate_explosive_alert_email(products, app_url=APP_URL)
    
    success = await send_email(user.email, subject, html_content)
    
    if success:
        return {"message": f"Test email sent to {user.email}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send test email")


# ============== BETA SIGNUP ENDPOINTS ==============

@api_router.post("/beta/signup")
async def beta_signup(
    email: EmailStr = Query(...),
    name: Optional[str] = Query(None),
    source: str = Query("website")
):
    """Sign up for beta access"""
    # Check if already signed up
    existing = await db.beta_signups.find_one({"email": email})
    if existing:
        return {"message": "You're already on the waitlist!", "status": "existing"}
    
    signup = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": name,
        "source": source,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.beta_signups.insert_one(signup)
    
    # Send welcome email
    if RESEND_API_KEY:
        welcome_html = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin: 0; padding: 40px; background: #000; font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; background: #050505; border: 1px solid #222; padding: 40px;">
                <h1 style="color: #00FF94; margin: 0;">Welcome to ALPHA DROP Beta!</h1>
                <p style="color: #888; margin: 20px 0;">
                    Hey{' ' + name if name else ''},<br><br>
                    You're on the waitlist! We're onboarding beta users in waves to ensure the best experience.
                </p>
                <p style="color: #888; margin: 20px 0;">
                    <strong style="color: #fff;">What's next?</strong><br>
                    - We'll email you when your spot opens up<br>
                    - Early access includes 14-day free trial of Hunter plan<br>
                    - Founding members get 25% off for life
                </p>
                <p style="color: #00FF94; font-size: 14px; margin: 30px 0 0;">
                    — The ALPHA DROP Team
                </p>
            </div>
        </body>
        </html>
        """
        await send_email(email, "You're on the ALPHA DROP Beta Waitlist! 🚀", welcome_html)
    
    # Get waitlist position
    count = await db.beta_signups.count_documents({})
    
    return {
        "message": "Welcome to the beta waitlist!",
        "status": "success",
        "position": count
    }


@api_router.get("/beta/stats")
async def get_beta_stats():
    """Get beta signup statistics"""
    total = await db.beta_signups.count_documents({})
    pending = await db.beta_signups.count_documents({"status": "pending"})
    invited = await db.beta_signups.count_documents({"status": "invited"})
    active = await db.beta_signups.count_documents({"status": "active"})
    
    return {
        "total_signups": total,
        "pending": pending,
        "invited": invited,
        "active": active,
        "target": 100
    }


# ============== ADMIN ENDPOINTS ==============

class AdminLoginRequest(BaseModel):
    email: str
    password: str

@api_router.post("/admin/login")
async def admin_login(body: AdminLoginRequest, response: Response):
    """Admin login with email/password — returns JWT."""
    admin = await db.admin_users.find_one({"email": body.email.lower()}, {"_id": 0})
    if not admin or not verify_password(body.password, admin["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_admin_token(admin["id"], admin["email"], "admin")
    response.set_cookie(
        key="admin_token", value=token, httponly=True, secure=True,
        samesite="none", max_age=7 * 24 * 3600, path="/"
    )
    return {"token": token, "email": admin["email"], "name": admin.get("name", "Admin")}

@api_router.get("/admin/me")
async def admin_me(request: Request):
    """Get current admin user."""
    payload = await get_admin_user(request)
    return {"email": payload["email"], "role": payload["role"]}

@api_router.post("/admin/logout")
async def admin_logout(response: Response):
    response.delete_cookie(key="admin_token", path="/")
    return {"message": "Logged out"}

@api_router.get("/admin/dashboard")
async def admin_dashboard(request: Request):
    """Admin overview — subscribers, revenue, product stats, beta signups."""
    await get_admin_user(request)
    total_products = await db.products.count_documents({})
    explosive = await db.products.count_documents({"status": "EXPLOSIVE"})
    rising = await db.products.count_documents({"status": "RISING"})
    early = await db.products.count_documents({"status": "EARLY_SIGNAL"})
    total_users = await db.users.count_documents({})
    active_subs = await db.user_subscriptions.count_documents({"status": "active"})
    total_payments = await db.payment_transactions.count_documents({"status": "complete"})
    rev_pipeline = [{"$match": {"payment_status": "paid"}}, {"$group": {"_id": None, "total": {"$sum": "$amount"}}}]
    rev_result = await db.payment_transactions.aggregate(rev_pipeline).to_list(1)
    total_revenue = rev_result[0]["total"] if rev_result else 0
    beta_signups = await db.beta_signups.count_documents({})
    weekly_reports_sent = await db.weekly_reports.count_documents({})
    recent_subs = await db.user_subscriptions.find(
        {}, {"_id": 0}
    ).sort("started_at", -1).limit(10).to_list(10)
    return {
        "products": {"total": total_products, "explosive": explosive, "rising": rising, "early_signal": early},
        "users": {"total": total_users, "active_subscribers": active_subs},
        "revenue": {"total": round(total_revenue, 2), "transactions": total_payments},
        "beta_signups": beta_signups,
        "weekly_reports_sent": weekly_reports_sent,
        "recent_subscriptions": recent_subs,
    }

@api_router.get("/admin/subscribers")
async def admin_subscribers(request: Request):
    """List all subscriptions."""
    await get_admin_user(request)
    subs = await db.user_subscriptions.find({}, {"_id": 0}).sort("started_at", -1).to_list(500)
    return {"subscribers": subs}

@api_router.post("/admin/subscribers/{email}/activate")
async def admin_activate_sub(email: str, request: Request, plan_id: str = Query("hunter")):
    """Manually activate a subscription for a user (admin grant)."""
    await get_admin_user(request)
    existing = await db.user_subscriptions.find_one({"user_email": email, "status": "active"})
    if existing:
        return {"message": "Already active", "status": "existing"}
    sub = {
        "id": str(uuid.uuid4()),
        "user_email": email,
        "plan_id": plan_id,
        "plan_name": SUBSCRIPTION_PLANS.get(plan_id, {}).get("name", plan_id),
        "status": "active",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=365 * 10)).isoformat(),
        "payment_session_id": "admin_grant",
    }
    await db.user_subscriptions.insert_one(sub)
    return {"message": f"Subscription activated for {email}", "plan": plan_id}

@api_router.post("/admin/subscribers/{email}/deactivate")
async def admin_deactivate_sub(email: str, request: Request):
    """Manually deactivate a subscription."""
    await get_admin_user(request)
    result = await db.user_subscriptions.update_many(
        {"user_email": email, "status": "active"},
        {"$set": {"status": "cancelled"}}
    )
    return {"message": f"Deactivated {result.modified_count} subscription(s) for {email}"}

@api_router.get("/admin/users")
async def admin_users(request: Request):
    """List all users."""
    await get_admin_user(request)
    users = await db.users.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return {"users": users}

@api_router.get("/admin/payments")
async def admin_payments(request: Request):
    """List all payment transactions."""
    await get_admin_user(request)
    payments = await db.payment_transactions.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return {"payments": payments}


# ============== CSV EXPORT ENDPOINTS ==============

@api_router.get("/export/products")
async def export_products_csv(request: Request):
    """Export products as CSV — requires subscription."""
    await require_subscription(request)
    products = await db.products.find(
        {}, {"_id": 0, "id": 1, "name": 1, "category": 1, "price": 1, "alpha_score": 1,
             "status": 1, "total_sales": 1, "total_views": 1, "creator_count": 1,
             "avg_engagement": 1, "risk_level": 1, "reason": 1, "created_at": 1}
    ).sort("alpha_score", -1).limit(1000).to_list(1000)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "id", "name", "category", "price", "alpha_score", "status",
        "total_sales", "total_views", "creator_count", "avg_engagement",
        "risk_level", "reason", "created_at"
    ])
    writer.writeheader()
    for p in products:
        writer.writerow({k: p.get(k, "") for k in writer.fieldnames})
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=alphadrop_products_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"}
    )

@api_router.get("/export/watchlist/{user_id}")
async def export_watchlist_csv(user_id: str, request: Request):
    """Export watchlist as CSV — requires subscription."""
    await require_subscription(request)
    items = await db.watchlist.find({"user_id": user_id}, {"_id": 0}).to_list(500)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "product_id", "product_name", "alpha_score", "status", "added_at", "notes"
    ])
    writer.writeheader()
    for item in items:
        writer.writerow({k: item.get(k, "") for k in writer.fieldnames})
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=alphadrop_watchlist_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"}
    )


# ============== STARTUP: SEED ADMIN ==============

@app.on_event("startup")
async def startup_seed_admin():
    """Seed admin user on startup."""
    existing = await db.admin_users.find_one({"email": ADMIN_EMAIL.lower()})
    if not existing:
        await db.admin_users.insert_one({
            "id": str(uuid.uuid4()),
            "email": ADMIN_EMAIL.lower(),
            "password_hash": hash_password(ADMIN_PASSWORD),
            "name": "Admin",
            "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info(f"Admin user seeded: {ADMIN_EMAIL}")
    elif not verify_password(ADMIN_PASSWORD, existing["password_hash"]):
        await db.admin_users.update_one(
            {"email": ADMIN_EMAIL.lower()},
            {"$set": {"password_hash": hash_password(ADMIN_PASSWORD)}}
        )
        logger.info("Admin password updated from env")
    # Grant admin full subscription bypass
    admin_sub = await db.user_subscriptions.find_one({"user_email": ADMIN_EMAIL.lower(), "payment_session_id": "admin_grant"})
    if not admin_sub:
        await db.user_subscriptions.insert_one({
            "id": str(uuid.uuid4()),
            "user_email": ADMIN_EMAIL.lower(),
            "plan_id": "predator",
            "plan_name": "Predator",
            "status": "active",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=365 * 10)).isoformat(),
            "payment_session_id": "admin_grant",
        })
        logger.info("Admin subscription bypass created")


# Include the router
app.include_router(api_router)

# Include modular routers
from routes.affiliates import router as affiliates_router
from routes.history import router as history_router
from routes.api_access import router as api_access_router
from routes.team import router as team_router
from routes.trends import router as trends_router
from routes.ai_tools import router as ai_tools_router
from routes.ad_library import router as ad_library_router
from routes.forecast import router as forecast_router
from routes.store_tracking import router as store_tracking_router
from routes.marketplace import router as marketplace_router
from routes.creator_portal import router as creator_portal_router
from routes.push_notifications import router as push_notifications_router
app.include_router(affiliates_router)
app.include_router(history_router)
app.include_router(api_access_router)
app.include_router(team_router)
app.include_router(trends_router)
app.include_router(ai_tools_router)
app.include_router(ad_library_router)
app.include_router(forecast_router)
app.include_router(store_tracking_router)
app.include_router(marketplace_router)
app.include_router(creator_portal_router)
app.include_router(push_notifications_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
