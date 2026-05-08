# ALPHA DROP - Data Sources Integration Guide

## Quick Start: Get Real Data in 30 Minutes

### Step 1: Get API Keys

#### Option A: Scrape Creators (Recommended)
1. Go to https://scrapecreators.com
2. Sign up for account
3. Get API key from dashboard
4. Add to `/app/backend/.env`:
```
SCRAPE_CREATORS_API_KEY=your_key_here
```

#### Option B: SociaVault
1. Go to https://sociavault.com
2. Sign up for account
3. Get API key
4. Add to `/app/backend/.env`:
```
SOCIAVAULT_API_KEY=your_key_here
```

### Step 2: Data Collection Endpoints

The backend is ready to integrate. Here are the API endpoints you'll call:

#### Scrape Creators API

**Search Products:**
```
GET https://api.scrapecreators.com/v1/tiktok/product/search
Headers: x-api-key: YOUR_KEY
Params: query=led+face+mask&limit=50
```

**Get Product Details:**
```
GET https://api.scrapecreators.com/v1/tiktok/product
Params: url={product_url}&get_related_videos=true
```

**Response includes:**
- Product name, price, sold_count
- Seller info (name, rating, total_products)
- Related TikTok videos promoting the product
- Stock levels

#### SociaVault API

**Search Products:**
```
GET https://api.sociavault.com/v1/scrape/tiktok-shop/search
Headers: x-api-key: YOUR_KEY
Params: query=skincare
```

**Get Product Details:**
```
GET https://api.sociavault.com/v1/scrape/tiktok-shop/product-details
Params: url={product_url}
```

### Step 3: TikTok Creative Center (Free!)

No API key needed - scrape directly:
```
URL: https://ads.tiktok.com/business/creativecenter/top-products/pc/en
```

Data available:
- Top products by category
- Trending products (last 7/30 days)
- Bestsellers
- Fast movers

### Step 4: Calculate Real Alpha Score

Once you have real data, calculate Alpha Score like this:

```python
def calculate_real_alpha_score(product_data):
    # Velocity: Sales growth rate
    velocity = (product_data['sales_today'] - product_data['sales_yesterday']) / max(product_data['sales_yesterday'], 1)
    velocity_score = min(100, velocity * 50)  # Normalize to 0-100
    
    # Creator Adoption: Number of unique creators
    creator_count = product_data['creator_count']
    creator_score = min(100, creator_count * 2)  # 50 creators = 100
    
    # Engagement: Combined engagement rate
    engagement = (product_data['likes'] + product_data['comments']) / max(product_data['views'], 1)
    engagement_score = min(100, engagement * 1000)  # 10% engagement = 100
    
    # Market Expansion: Cross-platform presence
    on_amazon = product_data.get('amazon_match', False)
    on_google_trends = product_data.get('google_trending', False)
    expansion_score = (50 if on_amazon else 0) + (50 if on_google_trends else 0)
    
    # Saturation Risk: Competition level (inverted)
    competitor_count = product_data.get('competitor_count', 50)
    saturation_score = max(0, 100 - competitor_count)  # Fewer = better
    
    # Weighted Alpha Score
    alpha = (
        velocity_score * 0.25 +
        creator_score * 0.20 +
        engagement_score * 0.15 +
        expansion_score * 0.15 +
        saturation_score * 0.15 +
        product_data.get('hook_score', 50) * 0.10
    )
    
    return int(min(100, max(0, alpha)))
```

### Step 5: Data Collection Schedule

Set up cron jobs to collect data:

```bash
# Every 6 hours - Search trending products
0 */6 * * * python /app/backend/jobs/collect_products.py

# Every hour - Update sales data for tracked products
0 * * * * python /app/backend/jobs/update_sales.py

# Daily - Calculate Alpha Scores
0 0 * * * python /app/backend/jobs/calculate_scores.py
```

---

## Alternative Free Data Sources

### 1. TikTok Creative Center (Manual or Scrape)
- URL: ads.tiktok.com/business/creativecenter
- Data: Top products, trending items, bestsellers
- Cost: Free

### 2. Google Trends API (PyTrends)
```python
from pytrends.request import TrendReq
pytrends = TrendReq()
pytrends.build_payload(['led face mask'], timeframe='now 7-d')
trends = pytrends.interest_over_time()
```

### 3. Amazon Product Data
- Use Amazon PA-API 5.0 (requires affiliate account)
- Or use Keepa API for price history

### 4. Social Listening
- Track TikTok hashtags related to products
- Monitor Reddit r/tiktokshop, r/dropshipping
- Twitter/X mentions

---

## Environment Variables Needed

Add these to `/app/backend/.env`:

```env
# Existing
MONGO_URL="mongodb://localhost:27017"
DB_NAME="alpha_drop"

# Data APIs
SCRAPE_CREATORS_API_KEY=your_key
SOCIAVAULT_API_KEY=your_key

# Optional - Cross-platform
AMAZON_ACCESS_KEY=your_key
AMAZON_SECRET_KEY=your_key
AMAZON_PARTNER_TAG=your_tag

# Monetization
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
```

---

## Data Schema for Real Products

```python
class RealProduct(BaseModel):
    # Core Info
    id: str
    tiktok_shop_url: str
    name: str
    price: float
    category: str
    image_url: str
    
    # Sales Data (from API)
    sold_count: int  # Total sold
    daily_sales: List[int]  # Last 14 days
    sales_velocity: float  # Growth rate
    
    # Creator Data
    creator_count: int
    top_creators: List[dict]  # [{name, followers, views}]
    
    # Engagement Data
    total_views: int
    total_likes: int
    total_comments: int
    engagement_rate: float
    
    # Video Data
    viral_videos: List[dict]  # [{url, views, hook_type}]
    
    # Competition
    competitor_count: int
    avg_competitor_price: float
    
    # Cross-Platform
    amazon_asin: Optional[str]
    amazon_bsr: Optional[int]
    google_trend_score: Optional[int]
    
    # Calculated
    alpha_score: int
    status: str  # EXPLOSIVE, RISING, etc.
    
    # Timestamps
    first_seen: datetime
    last_updated: datetime
```

---

## Next Steps

1. **Sign up for one API** (Scrape Creators or SociaVault)
2. **Add API key to .env**
3. **Run data collection job**
4. **Replace simulated data with real data**
5. **Launch beta with real products!**

The app is architected to easily swap simulated data for real API data. The Alpha Score algorithm, UI, and all features remain the same - only the data source changes.
