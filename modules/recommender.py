"""
Tab 1: Smart Destination Recommender (Epic 3).
Recommends top 3 matching destination cities based on budget, season, and travel mood.
Powered dynamically by Groq SDK with curated fallback.
"""

from typing import List, Dict, Any, Optional
import random
from config import DESTINATION_CATALOG, EXCHANGE_RATES
from modules.ai_engine import AIEngine


def get_curated_fallback_recommendations(
    vibe: str,
    budget_level: str,
    season: str,
    party: str,
    interests: List[str]
) -> List[Dict[str, Any]]:
    """Intelligently matches destinations from catalog when in demo mode or offline."""
    vibe_clean = vibe.split(" ")[1] if " " in vibe else vibe
    budget_clean = "Budget" if "Budget" in budget_level else ("Luxury" if "Luxury" in budget_level else "Moderate")

    scored = []
    for item in DESTINATION_CATALOG:
        score = 70
        if vibe_clean.lower() in item["vibe"].lower():
            score += 20
        if budget_clean.lower() in item["budget_level"].lower():
            score += 15
        
        tags_str = " ".join(item["highlight_tags"]).lower()
        for interest in interests:
            if any(w in tags_str for w in interest.lower().split() if len(w) > 3):
                score += 5
        
        score = min(98, score)
        copy_item = dict(item)
        copy_item["match_score"] = f"{score}%"
        copy_item["is_dynamic"] = False
        copy_item["why_matched"] = (
            f"Aligned with your {vibe_clean} vibe and {budget_clean} expectations. "
            f"Tailored for {party} seeking exceptional {', '.join(item['highlight_tags'][:2])}."
        )
        scored.append((score, copy_item))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_3 = [x[1] for x in scored[:3]]

    if len(top_3) < 3:
        for item in DESTINATION_CATALOG:
            if item not in top_3:
                top_3.append(item)
            if len(top_3) >= 3:
                break

    return top_3[:3]


def recommend_destinations(
    vibe: str,
    budget_level: str,
    season: str,
    party: str,
    interests: List[str],
    ai_engine: AIEngine
) -> List[Dict[str, Any]]:
    """
    Returns top 3 destination recommendations dynamically using Groq SDK with fallback.
    """
    if ai_engine.is_demo():
        return get_curated_fallback_recommendations(vibe, budget_level, season, party, interests)

    interests_str = ", ".join(interests) if interests else "Sightseeing, Culture, and Local Food"
    prompt = f"""
Act as an elite world-class travel curator and destination recommender.
User Travel Profile:
- Desired Travel Vibe/Mood: {vibe}
- Target Budget Tier: {budget_level}
- Target Travel Timing / Season: {season}
- Travel Party: {party}
- Specific Interests: {interests_str}

Task:
Generate the TOP 3 most exciting, highly tailored travel destinations (City & Country) that strictly match this unique user profile. Be highly creative, authentic, and diverse.

For each destination, return a JSON object with this exact structure:
{{
  "recommendations": [
    {{
      "city": "Name of City",
      "country": "Name of Country",
      "vibe": "Short vibe tagline",
      "highlight_tags": ["Tag 1", "Tag 2", "Tag 3", "Tag 4"],
      "match_score": "98%",
      "why_matched": "2 concise sentences explaining why this specifically fits their budget, vibe, and season.",
      "best_season": "e.g. April to June & September",
      "avg_daily_usd": 120,
      "avg_daily_inr": 10380,
      "currency": "EUR",
      "signature_experiences": [
        "Experience 1 description",
        "Experience 2 description",
        "Experience 3 description"
      ],
      "transit_style": "How visitors navigate the city efficiently",
      "center_coords": [latitude_float, longitude_float]
    }}
  ]
}}
Strict Requirement: Return ONLY valid JSON containing exactly 3 recommendations.
"""
    system_instruction = "You are a master travel curator. Always provide realistic, high-precision recommendations in pure JSON."
    parsed, error = ai_engine.generate_json(prompt, system_instruction)

    if parsed and "recommendations" in parsed and isinstance(parsed["recommendations"], list) and len(parsed["recommendations"]) >= 3:
        for rec in parsed["recommendations"]:
            usd = rec.get("avg_daily_usd", 120)
            rec["avg_daily_inr"] = rec.get("avg_daily_inr", int(usd * EXCHANGE_RATES.get("INR", 86.5)))
            rec["is_dynamic"] = True
            if "center_coords" not in rec or not isinstance(rec["center_coords"], list) or len(rec["center_coords"]) != 2:
                rec["center_coords"] = [25.2048, 55.2708]
        return parsed["recommendations"][:3]

    print(f"Recommender fallback triggered: {error}")
    return get_curated_fallback_recommendations(vibe, budget_level, season, party, interests)
