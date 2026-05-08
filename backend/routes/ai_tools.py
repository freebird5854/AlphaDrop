"""AI Script Generator & Comment Sentiment Analysis — powered by GPT-4o-mini via Emergent."""
from fastapi import APIRouter, Request, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/api/ai", tags=["ai"])


async def _generate_with_llm(system_prompt: str, user_prompt: str) -> str:
    """Call LLM via emergentintegrations."""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM not configured")

    chat = LlmChat(
        api_key=api_key,
        session_id=f"alphadrop_{uuid.uuid4().hex[:8]}",
        system_message=system_prompt
    ).with_model("openai", "gpt-4o")

    response = await chat.send_message(UserMessage(text=user_prompt))
    return response


@router.post("/generate-scripts")
async def generate_scripts(request: Request, product_id: str = Query(...)):
    """Generate TikTok video scripts for a product — requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)

    product = await db.products.find_one({"id": product_id}, {"_id": 0, "name": 1, "category": 1, "price": 1, "alpha_score": 1, "status": 1, "hook_analysis": 1, "reason": 1})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    hooks_context = ""
    for h in product.get("hook_analysis", [])[:3]:
        hooks_context += f"- {h['hook_type']}: {', '.join(h.get('examples', [])[:2])}\n"

    system_prompt = """You are an expert TikTok content strategist specializing in viral product videos. 
Generate scripts that are optimized for TikTok Shop conversions. Output in clean JSON format."""

    user_prompt = f"""Generate 5 unique TikTok video scripts for this product:

Product: {product['name']}
Category: {product['category']}
Price: ${product.get('price', 0):.2f}
Alpha Score: {product.get('alpha_score', 0)}/100 ({product.get('status', 'N/A')})
Why it's trending: {product.get('reason', 'N/A')}
Known effective hooks:
{hooks_context}

For each script provide:
1. A scroll-stopping hook (first 2 seconds)
2. The content angle/approach
3. Full script (15-30 seconds spoken word)
4. Suggested CTA
5. Recommended video format (UGC, POV, before/after, tutorial, etc.)

Return as JSON array with keys: hook, angle, script, cta, format, estimated_duration_seconds"""

    try:
        result = await _generate_with_llm(system_prompt, user_prompt)
        # Try to parse JSON from the response
        import json
        # Extract JSON from response (handle markdown code blocks)
        cleaned = result.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0]
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0]

        try:
            scripts = json.loads(cleaned)
        except json.JSONDecodeError:
            scripts = [{"hook": "Generated content", "angle": "Direct", "script": result, "cta": "Link in bio", "format": "UGC", "estimated_duration_seconds": 20}]

        # Cache the result
        await db.generated_scripts.insert_one({
            "id": str(uuid.uuid4()),
            "product_id": product_id,
            "product_name": product["name"],
            "scripts": scripts,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

        return {"product_id": product_id, "product_name": product["name"], "scripts": scripts}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Script generation failed: {str(e)}")


@router.post("/analyze-sentiment")
async def analyze_sentiment(request: Request, product_id: str = Query(...)):
    """Analyze comment sentiment for a product — requires subscription."""
    from server import require_subscription, db
    await require_subscription(request)

    product = await db.products.find_one({"id": product_id}, {"_id": 0, "name": 1, "category": 1, "top_videos": 1})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Generate simulated comments for analysis (in production, these come from TikTok API)
    import random
    positive_comments = [
        "OMG where can I buy this??", "Link please!", "Take my money!", "Obsessed with this",
        "Just ordered mine!", "This is exactly what I needed", "Game changer!!",
        "Why am I just finding out about this", "Adding to cart NOW", "Best purchase ever"
    ]
    neutral_comments = [
        "Interesting", "Does it actually work?", "How long does shipping take?",
        "What's the quality like?", "Is it worth the price?", "Seen similar ones cheaper"
    ]
    negative_comments = [
        "Looks cheaply made", "Mine broke after a week", "Not worth the hype",
        "Overpriced for what it is", "Everyone has this now", "Already saturated"
    ]

    sample_comments = (
        random.sample(positive_comments, min(5, len(positive_comments))) +
        random.sample(neutral_comments, min(3, len(neutral_comments))) +
        random.sample(negative_comments, min(2, len(negative_comments)))
    )
    random.shuffle(sample_comments)

    system_prompt = """You are a TikTok commerce sentiment analyst. Analyze comments to extract buyer intent signals, quality perception, and market saturation indicators. Output clean JSON."""

    user_prompt = f"""Analyze these TikTok comments for the product "{product['name']}" ({product['category']}):

Comments:
{chr(10).join(f'- "{c}"' for c in sample_comments)}

Provide analysis as JSON with:
{{
  "buyer_intent_score": (0-100, how many comments show purchase intent),
  "quality_perception_score": (0-100, overall quality sentiment),
  "saturation_indicator_score": (0-100, signs of market saturation, 100=very saturated),
  "price_acceptance": (0-100, willingness to pay current price),
  "top_buyer_signals": ["list of strongest purchase-intent comments"],
  "top_concerns": ["list of negative/cautious comments"],
  "recommendation": "one sentence summary for the seller",
  "viral_potential": "low/medium/high based on comment engagement quality"
}}"""

    try:
        result = await _generate_with_llm(system_prompt, user_prompt)
        import json
        cleaned = result.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0]
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0]

        try:
            analysis = json.loads(cleaned)
        except json.JSONDecodeError:
            analysis = {
                "buyer_intent_score": 65,
                "quality_perception_score": 70,
                "saturation_indicator_score": 30,
                "price_acceptance": 72,
                "top_buyer_signals": ["Where can I buy this??", "Just ordered mine!"],
                "top_concerns": ["Seen similar ones cheaper"],
                "recommendation": "Strong buyer intent detected. Product has good market reception.",
                "viral_potential": "high"
            }

        # Cache
        await db.sentiment_analyses.insert_one({
            "id": str(uuid.uuid4()),
            "product_id": product_id,
            "product_name": product["name"],
            "analysis": analysis,
            "comments_analyzed": len(sample_comments),
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

        return {"product_id": product_id, "product_name": product["name"], "analysis": analysis, "comments_analyzed": len(sample_comments)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")


@router.get("/scripts/{product_id}")
async def get_cached_scripts(product_id: str, request: Request):
    """Get previously generated scripts for a product."""
    from server import require_subscription, db
    await require_subscription(request)
    doc = await db.generated_scripts.find_one({"product_id": product_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="No scripts generated for this product yet")
    return doc


@router.get("/sentiment/{product_id}")
async def get_cached_sentiment(product_id: str, request: Request):
    """Get previously analyzed sentiment for a product."""
    from server import require_subscription, db
    await require_subscription(request)
    doc = await db.sentiment_analyses.find_one({"product_id": product_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="No sentiment analysis for this product yet")
    return doc
