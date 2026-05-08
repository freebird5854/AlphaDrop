"""
ALPHA DROP - Real Data Collection Service
Integrates with Scrape Creators, SociaVault, and TikTok Creative Center
"""

import os
import httpx
import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# API Configuration
SCRAPE_CREATORS_BASE = "https://api.scrapecreators.com/v1"
SOCIAVAULT_BASE = "https://api.sociavault.com/v1"

class TikTokDataService:
    """Service to collect real TikTok Shop product data"""
    
    def __init__(self):
        self.scrape_creators_key = os.environ.get('SCRAPE_CREATORS_API_KEY')
        self.sociavault_key = os.environ.get('SOCIAVAULT_API_KEY')
        
    async def search_products_scrape_creators(
        self, 
        query: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search products using Scrape Creators API"""
        if not self.scrape_creators_key:
            logger.warning("SCRAPE_CREATORS_API_KEY not set")
            return []
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{SCRAPE_CREATORS_BASE}/tiktok/product/search",
                    headers={"x-api-key": self.scrape_creators_key},
                    params={"query": query, "limit": limit},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get('products', [])
            except Exception as e:
                logger.error(f"Scrape Creators search failed: {e}")
                return []
    
    async def get_product_details_scrape_creators(
        self, 
        product_url: str,
        get_videos: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Get detailed product info with related viral videos"""
        if not self.scrape_creators_key:
            return None
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{SCRAPE_CREATORS_BASE}/tiktok/product",
                    headers={"x-api-key": self.scrape_creators_key},
                    params={
                        "url": product_url,
                        "get_related_videos": str(get_videos).lower()
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Scrape Creators product fetch failed: {e}")
                return None
    
    async def search_products_sociavault(
        self, 
        query: str
    ) -> List[Dict[str, Any]]:
        """Search products using SociaVault API"""
        if not self.sociavault_key:
            logger.warning("SOCIAVAULT_API_KEY not set")
            return []
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{SOCIAVAULT_BASE}/scrape/tiktok-shop/search",
                    headers={"x-api-key": self.sociavault_key},
                    params={"query": query},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get('results', [])
            except Exception as e:
                logger.error(f"SociaVault search failed: {e}")
                return []
    
    async def get_product_details_sociavault(
        self, 
        product_url: str
    ) -> Optional[Dict[str, Any]]:
        """Get product details from SociaVault"""
        if not self.sociavault_key:
            return None
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{SOCIAVAULT_BASE}/scrape/tiktok-shop/product-details",
                    headers={"x-api-key": self.sociavault_key},
                    params={"url": product_url},
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"SociaVault product fetch failed: {e}")
                return None
    
    def calculate_alpha_score(self, product_data: Dict[str, Any]) -> int:
        """Calculate Alpha Score from real product data"""
        
        # Extract metrics with defaults
        sales_today = product_data.get('sales_today', 0)
        sales_yesterday = product_data.get('sales_yesterday', 1)
        sold_count = product_data.get('sold_count', 0)
        creator_count = product_data.get('creator_count', 0)
        views = product_data.get('total_views', 1)
        likes = product_data.get('total_likes', 0)
        comments = product_data.get('total_comments', 0)
        competitor_count = product_data.get('competitor_count', 50)
        
        # Velocity Score (25% weight) - Sales growth rate
        if sales_yesterday > 0:
            velocity = (sales_today - sales_yesterday) / sales_yesterday
        else:
            velocity = 0.5 if sales_today > 0 else 0
        velocity_score = min(100, max(0, velocity * 50 + 50))
        
        # Creator Adoption Score (20% weight)
        # 50+ creators = max score
        creator_score = min(100, creator_count * 2)
        
        # Engagement Quality Score (15% weight)
        engagement_rate = (likes + comments) / max(views, 1)
        engagement_score = min(100, engagement_rate * 1000)
        
        # Hook Strength Score (10% weight) - Based on comment ratio
        if likes > 0:
            comment_ratio = comments / likes
            hook_score = min(100, comment_ratio * 500)  # Higher comments = better hooks
        else:
            hook_score = 50
        
        # Market Expansion Score (10% weight)
        has_amazon = product_data.get('amazon_match', False)
        has_google = product_data.get('google_trending', False)
        expansion_score = (50 if has_amazon else 0) + (50 if has_google else 0)
        
        # Saturation Risk Score (10% weight) - Inverted
        saturation_score = max(0, 100 - min(competitor_count, 100))
        
        # Repeatability Score (10% weight) - Based on consistent sales
        if sold_count > 1000:
            repeatability_score = min(100, (sold_count / 1000) * 10)
        else:
            repeatability_score = min(100, sold_count / 10)
        
        # Weighted Alpha Score
        alpha = (
            velocity_score * 0.25 +
            creator_score * 0.20 +
            engagement_score * 0.15 +
            hook_score * 0.10 +
            expansion_score * 0.10 +
            saturation_score * 0.10 +
            repeatability_score * 0.10
        )
        
        return int(min(100, max(0, alpha)))
    
    def get_status_from_score(self, score: int) -> str:
        """Determine product status from Alpha Score"""
        if score >= 80:
            return "EXPLOSIVE"
        elif score >= 60:
            return "RISING"
        elif score >= 45:
            return "EARLY_SIGNAL"
        elif score >= 40:
            return "WATCHLIST"
        else:
            return "AVOID"
    
    def transform_to_product(self, raw_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Transform raw API data to our Product schema"""
        
        # Calculate Alpha Score
        alpha_score = self.calculate_alpha_score(raw_data)
        status = self.get_status_from_score(alpha_score)
        
        # Determine trend direction
        sales_today = raw_data.get('sales_today', 0)
        sales_yesterday = raw_data.get('sales_yesterday', 0)
        if sales_today > sales_yesterday * 1.1:
            trend_direction = "up"
        elif sales_today < sales_yesterday * 0.9:
            trend_direction = "down"
        else:
            trend_direction = "stable"
        
        # Risk level
        if status == "EXPLOSIVE":
            risk_level = "low"
        elif status in ["RISING", "EARLY_SIGNAL"]:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "id": raw_data.get('id', str(hash(raw_data.get('url', '')))),
            "name": raw_data.get('name', 'Unknown Product'),
            "category": raw_data.get('category', 'Uncategorized'),
            "image_url": raw_data.get('image_url', ''),
            "price": float(raw_data.get('price', 0)),
            "alpha_score": alpha_score,
            "status": status,
            "trend_direction": trend_direction,
            "risk_level": risk_level,
            "reason": self._generate_reason(raw_data, alpha_score, status),
            "total_sales": raw_data.get('sold_count', 0),
            "total_views": raw_data.get('total_views', 0),
            "creator_count": raw_data.get('creator_count', 0),
            "avg_engagement": round(
                (raw_data.get('total_likes', 0) + raw_data.get('total_comments', 0)) / 
                max(raw_data.get('total_views', 1), 1) * 100, 2
            ),
            "competition_density": raw_data.get('competitor_count', 0),
            "tiktok_shop_url": raw_data.get('url', ''),
            "source": source,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _generate_reason(self, data: Dict, score: int, status: str) -> str:
        """Generate human-readable reason for the product's status"""
        reasons = []
        
        sold_count = data.get('sold_count', 0)
        creator_count = data.get('creator_count', 0)
        views = data.get('total_views', 0)
        
        if status == "EXPLOSIVE":
            if sold_count > 10000:
                reasons.append(f"High sales volume ({sold_count:,} units)")
            if creator_count > 30:
                reasons.append(f"Strong creator adoption ({creator_count} creators)")
            if views > 1000000:
                reasons.append(f"Viral reach ({views/1000000:.1f}M views)")
        elif status == "RISING":
            if sold_count > 5000:
                reasons.append(f"Growing sales momentum")
            if creator_count > 15:
                reasons.append(f"Creator network expanding")
        elif status == "EARLY_SIGNAL":
            if creator_count >= 5:
                reasons.append(f"Early creator accumulation ({creator_count} creators)")
            reasons.append("Pre-viral pattern detected")
        else:
            if data.get('competitor_count', 0) > 50:
                reasons.append("Market saturation risk")
            reasons.append("Monitor for changes")
        
        return " • ".join(reasons) if reasons else f"Alpha Score: {score}"


# Singleton instance
data_service = TikTokDataService()


# ============== COLLECTION FUNCTIONS ==============

async def collect_trending_products(categories: List[str] = None) -> List[Dict]:
    """Collect trending products from all sources"""
    
    if categories is None:
        categories = [
            "beauty skincare",
            "led gadgets",
            "health wellness",
            "home kitchen",
            "fashion accessories",
            "pet products"
        ]
    
    all_products = []
    
    for category in categories:
        # Try Scrape Creators first
        products = await data_service.search_products_scrape_creators(category)
        if not products:
            # Fallback to SociaVault
            products = await data_service.search_products_sociavault(category)
        
        for raw_product in products:
            transformed = data_service.transform_to_product(raw_product, "api")
            all_products.append(transformed)
    
    # Sort by Alpha Score
    all_products.sort(key=lambda x: x['alpha_score'], reverse=True)
    
    return all_products


async def update_product_data(product_url: str) -> Optional[Dict]:
    """Update data for a single product"""
    
    details = await data_service.get_product_details_scrape_creators(product_url)
    if not details:
        details = await data_service.get_product_details_sociavault(product_url)
    
    if details:
        return data_service.transform_to_product(details, "api")
    
    return None


# ============== EXAMPLE USAGE ==============

if __name__ == "__main__":
    async def test():
        print("Testing data collection...")
        
        # Check for API keys
        if data_service.scrape_creators_key:
            print("✓ Scrape Creators API key found")
        else:
            print("✗ Scrape Creators API key not set")
            
        if data_service.sociavault_key:
            print("✓ SociaVault API key found")
        else:
            print("✗ SociaVault API key not set")
        
        # Test Alpha Score calculation
        test_product = {
            'sales_today': 150,
            'sales_yesterday': 100,
            'sold_count': 5000,
            'creator_count': 25,
            'total_views': 500000,
            'total_likes': 50000,
            'total_comments': 5000,
            'competitor_count': 30,
            'amazon_match': True,
            'google_trending': False
        }
        
        score = data_service.calculate_alpha_score(test_product)
        status = data_service.get_status_from_score(score)
        print(f"\nTest Product Alpha Score: {score} ({status})")
    
    asyncio.run(test())
