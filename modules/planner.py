"""
Tab 2: Day-by-Day Optimized Itinerary Generator (Epic 4).
Generates structured day-wise plans with sequential time slots,
strict geographic clustering, and dual-currency cost tracking.
Supports 100% dynamic generation via Groq SDK.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
import math
from config import EXCHANGE_RATES, CURRENCY_SYMBOLS
from modules.ai_engine import AIEngine


def detect_destination_currency(destination: str) -> str:
    """Guesses local currency code based on destination country/city name."""
    dest_lower = destination.lower()
    if any(k in dest_lower for k in ["japan", "tokyo", "kyoto", "osaka"]):
        return "JPY"
    if any(k in dest_lower for k in ["italy", "rome", "florence", "france", "paris", "spain", "barcelona", "madrid", "germany", "greece", "amsterdam", "netherlands", "portugal", "lisbon"]):
        return "EUR"
    if any(k in dest_lower for k in ["uk", "london", "edinburgh", "britain", "england", "scotland"]):
        return "GBP"
    if any(k in dest_lower for k in ["india", "delhi", "mumbai", "goa", "kerala", "jaipur", "bangalore"]):
        return "INR"
    if any(k in dest_lower for k in ["thailand", "bangkok", "phuket", "chiang mai"]):
        return "THB"
    if any(k in dest_lower for k in ["dubai", "abu dhabi", "uae"]):
        return "AED"
    if any(k in dest_lower for k in ["bali", "indonesia", "jakarta", "ubud"]):
        return "IDR"
    if any(k in dest_lower for k in ["australia", "sydney", "melbourne"]):
        return "AUD"
    if any(k in dest_lower for k in ["singapore"]):
        return "SGD"
    if any(k in dest_lower for k in ["canada", "toronto", "vancouver", "banff"]):
        return "CAD"
    if any(k in dest_lower for k in ["switzerland", "zurich", "geneva"]):
        return "CHF"
    return "USD"


def _get_base_coordinates(destination: str) -> tuple:
    """Gets approximate center coordinates for common cities or fallback."""
    base_coords = {
        "paris": (48.8566, 2.3522),
        "rome": (41.9028, 12.4964),
        "tokyo": (35.6762, 139.6503),
        "kyoto": (35.0116, 135.7681),
        "barcelona": (41.3879, 2.1699),
        "london": (51.5074, -0.1278),
        "dubai": (25.2048, 55.2708),
        "bali": (-8.4095, 115.1889),
        "bangkok": (13.7563, 100.5018),
        "new york": (40.7128, -74.0060),
        "san francisco": (37.7749, -122.4194),
        "singapore": (1.3521, 103.8198),
        "amsterdam": (52.3676, 4.9041),
        "mumbai": (19.0760, 72.8777),
        "delhi": (28.6139, 77.2090),
        "lisbon": (38.7223, -9.1393),
        "vienna": (48.2082, 16.3738),
        "prague": (50.0755, 14.4378),
        "sydney": (-33.8688, 151.2093),
    }
    dest_lower = destination.lower()
    for k, coords in base_coords.items():
        if k in dest_lower:
            return coords
    return (41.9028, 12.4964)


def _build_procedural_itinerary(
    destination: str,
    duration_days: int,
    start_date: Any,
    budget_level: str,
    travel_party: str,
    pace: str,
    interests: List[str],
    dietary: str
) -> Dict[str, Any]:
    """Generates high-fidelity structured itinerary procedurally with geographic clusters."""
    currency = detect_destination_currency(destination)
    usd_rate = EXCHANGE_RATES.get(currency, 1.0)
    inr_rate = EXCHANGE_RATES.get("INR", 86.5)

    if "Budget" in budget_level:
        cost_mult = 0.6
    elif "Luxury" in budget_level:
        cost_mult = 2.4
    else:
        cost_mult = 1.0

    cluster_templates = [
        ("Historic Core & Ancient Quarter", "Low (Walking distance within 1.2 km radius, pedestrianized streets)"),
        ("Waterfront, Harbor & Marine Promenade", "Low (Scenic waterfront promenade & water taxi links)"),
        ("Arts, Fashion & Contemporary Design District", "Low (Compact gallery zone with cafe pauses)"),
        ("Bohemian Heights, Gardens & Panoramic Viewpoints", "Moderate (Incline tram or scenic cable car link)"),
        ("Culinary Alleyways & Artisan Craft Quarter", "Low (Interlinked market lanes & tasting hubs)"),
        ("Modern Financial Skyline & High-tech Hub", "Low (Direct modern metro line connections)"),
        ("Island Gateway or Coastal Cliffside Pockets", "Moderate (Scenic coastal shuttle link)"),
    ]

    center_lat, center_lng = _get_base_coordinates(destination)
    primary_interest = interests[0] if interests else "Iconic Landmarks"
    secondary_interest = interests[1] if len(interests) > 1 else "Local Cuisine"

    if isinstance(start_date, (datetime, date)):
        s_date = start_date
    else:
        try:
            s_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()
        except Exception:
            s_date = date.today()

    days = []
    running_usd = 0.0

    for i in range(1, duration_days + 1):
        c_name, fatigue = cluster_templates[(i - 1) % len(cluster_templates)]
        day_date = (s_date + timedelta(days=i - 1)).strftime("%b %d, %Y")
        
        angle = (i * 0.9)
        cluster_center_lat = center_lat + 0.015 * math.cos(angle)
        cluster_center_lng = center_lng + 0.015 * math.sin(angle)

        m_cost_usd = round(20 * cost_mult, 1)
        l_cost_usd = round(25 * cost_mult, 1)
        a_cost_usd = round(22 * cost_mult, 1)
        e_cost_usd = round(55 * cost_mult, 1)
        day_usd = m_cost_usd + l_cost_usd + a_cost_usd + e_cost_usd
        day_inr = round(day_usd * inr_rate, 0)
        running_usd += day_usd

        slots = {
            "morning": {
                "time": "09:00 - 12:00",
                "title": f"Iconic Heritage & Architecture Walk in {c_name.split('&')[0].strip()}",
                "category": "Sightseeing / Culture",
                "description": f"Immerse yourself in the rich architectural history of {destination}. Explore iconic landmarks and historic courtyards focused on {primary_interest}.",
                "location_name": f"{destination} Heritage Site ({c_name})",
                "lat": round(cluster_center_lat + 0.003, 4),
                "lng": round(cluster_center_lng + 0.002, 4),
                "cost_local": round(m_cost_usd * usd_rate, 0),
                "cost_usd": m_cost_usd,
                "cost_inr": round(m_cost_usd * inr_rate, 0),
                "pro_tip": "Arrive early before 9:30 AM to beat tour groups and capture morning golden hour lighting."
            },
            "lunch": {
                "time": "12:30 - 14:00",
                "title": f"Artisan Lunch Bistro & Regional Specialties",
                "category": "Dining / Food Experience",
                "cuisine": f"Authentic Regional Cuisine ({dietary})",
                "description": f"Enjoy a curated lunch spotlighting seasonal local ingredients and {secondary_interest}. Tailored with options for {dietary}.",
                "location_name": f"Trattoria & Bistro {c_name.split()[0]}",
                "lat": round(cluster_center_lat - 0.002, 4),
                "lng": round(cluster_center_lng + 0.001, 4),
                "cost_local": round(l_cost_usd * usd_rate, 0),
                "cost_usd": l_cost_usd,
                "cost_inr": round(l_cost_usd * inr_rate, 0),
                "dietary_tags": f"{dietary} friendly, Chef's seasonal market specials"
            },
            "afternoon": {
                "time": "14:30 - 17:30",
                "title": f"Cultural Immersion & Hidden Alleys of {c_name.split('&')[0].strip()}",
                "category": "Leisure / Immersion",
                "description": f"Stroll picturesque cobblestone streets, artisan workshops, and boutique galleries. Experience local craftsmen and scenic garden courtyards.",
                "location_name": f"{c_name} Promenade",
                "lat": round(cluster_center_lat + 0.001, 4),
                "lng": round(cluster_center_lng - 0.003, 4),
                "cost_local": round(a_cost_usd * usd_rate, 0),
                "cost_usd": a_cost_usd,
                "cost_inr": round(a_cost_usd * inr_rate, 0),
                "pro_tip": "Keep an eye out for family-run artisan studios tucked just off the main plaza."
            },
            "evening": {
                "time": "18:30 - 21:30",
                "title": f"Sunset Viewpoint & Vibrant Dinner Atmosphere",
                "category": "Dining & Nightlife",
                "description": f"Watch the twilight glow over {destination} from an elevated terrace viewpoint, followed by a multi-course dinner with music or social ambiance.",
                "location_name": f"Panorama Terrace & Dining in {c_name}",
                "lat": round(cluster_center_lat - 0.004, 4),
                "lng": round(cluster_center_lng - 0.001, 4),
                "cost_local": round(e_cost_usd * usd_rate, 0),
                "cost_usd": e_cost_usd,
                "cost_inr": round(e_cost_usd * inr_rate, 0),
                "pro_tip": "Book an outdoor terrace table 20 minutes before sunset for the best twilight view."
            }
        }

        days.append({
            "day_number": i,
            "date_str": day_date,
            "day_theme": f"Day {i}: {c_name}",
            "cluster_neighborhood": f"{c_name} Geographic Cluster",
            "transit_fatigue_score": fatigue,
            "day_total_usd": day_usd,
            "day_total_inr": day_inr,
            "running_total_usd": round(running_usd, 1),
            "slots": slots
        })

    total_usd = round(running_usd, 1)
    total_inr = round(total_usd * inr_rate, 0)

    return {
        "trip_title": f"{destination} {duration_days}-Day Curated Journey",
        "destination": destination,
        "duration_days": duration_days,
        "start_date": str(s_date),
        "end_date": str(s_date + timedelta(days=duration_days - 1)),
        "budget_level": budget_level,
        "travel_party": travel_party,
        "pace": pace,
        "interests": interests,
        "dietary": dietary,
        "currency": currency,
        "exchange_rate_to_usd": usd_rate,
        "exchange_rate_to_inr": inr_rate,
        "total_estimated_usd": total_usd,
        "total_estimated_inr": total_inr,
        "is_dynamic": False,
        "ai_engine_note": "Procedural baseline model",
        "overview": (
            f"A masterfully orchestrated {duration_days}-day itinerary in {destination} "
            f"crafted for a {travel_party} travelling at a {pace} tempo with {budget_level} accommodations. "
            f"Every single day is geographically clustered to maximize exploration and prevent cross-city transit fatigue."
        ),
        "emergency_contacts": {
            "police": "112 / 911 / Local Emergency",
            "ambulance": "Dial Local 112 / Hotel Concierge Medical Desk",
            "tourist_helpline": "National Tourist Information & Assistance Line",
            "embassy_note": "Ensure your passport has at least 6 months validity from date of entry."
        },
        "packing_tips": [
            "Comfortable, broken-in walking shoes for cobblestones",
            "Compact universal travel adapter & portable powerbank",
            "Light rain layer or windbreaker depending on forecast",
            "Digital and printed copies of travel medical insurance"
        ],
        "days": days
    }


def generate_itinerary(
    destination: str,
    duration_days: int,
    start_date: Any,
    budget_level: str,
    travel_party: str,
    pace: str,
    interests: List[str],
    dietary: str,
    ai_engine: AIEngine
) -> Dict[str, Any]:
    """Generates day-by-day optimized itinerary with geographic clustering dynamically via AI."""
    if ai_engine.is_demo():
        return _build_procedural_itinerary(
            destination, duration_days, start_date, budget_level, travel_party, pace, interests, dietary
        )

    interests_str = ", ".join(interests) if interests else "Sightseeing, Culture, and Local Food"
    currency = detect_destination_currency(destination)
    usd_rate = EXCHANGE_RATES.get(currency, 1.0)
    inr_rate = EXCHANGE_RATES.get("INR", 86.5)
    default_lat, default_lng = _get_base_coordinates(destination)

    prompt = f"""
Act as an elite full-stack travel SaaS architect and itinerary optimizer.
Create a structured, 100% realistic {duration_days}-day itinerary for:
- Destination: {destination}
- Duration: {duration_days} days
- Budget Tier: {budget_level}
- Travel Party: {travel_party}
- Travel Pace: {pace}
- Core Interests: {interests_str}
- Dietary Preference: {dietary}

CRITICAL ARCHITECTURAL CONSTRAINTS:
1. STRICT GEOGRAPHIC CLUSTERING: Each day MUST focus on ONE distinct neighborhood / district cluster (e.g. "Day 1: Historic Old Town & Waterfront Cluster"). All 4 activities (morning, lunch, afternoon, evening) for that day MUST be located within that same neighborhood to prevent backtracking and transit fatigue.
2. SEQUENTIAL TIME SLOTS: Exactly 4 slots per day: 'morning', 'lunch', 'afternoon', 'evening'.
3. ACCURATE REAL-WORLD COORDINATES: Provide realistic latitude and longitude coordinates for each location so it accurately renders on interactive PyDeck maps.
4. ESTIMATED COSTS IN USD: Realistic cost for each activity.

Return ONLY a JSON object matching this schema:
{{
  "trip_title": "Catchy Trip Title",
  "overview": "2-3 sentences summarizing the trip route and clustering philosophy",
  "currency": "{currency}",
  "days": [
    {{
      "day_number": 1,
      "day_theme": "Theme title for the day",
      "cluster_neighborhood": "Specific Neighborhood or District Cluster",
      "transit_fatigue_score": "Low (e.g. All spots within 1km walking)",
      "slots": {{
        "morning": {{
          "time": "09:00 - 12:00",
          "title": "Morning Activity Name",
          "category": "Sightseeing / Culture",
          "description": "Engaging, practical description",
          "location_name": "Landmark name",
          "lat": {default_lat},
          "lng": {default_lng},
          "cost_usd": 20.0,
          "pro_tip": "Actionable insider tip"
        }},
        "lunch": {{
          "time": "12:30 - 14:00",
          "title": "Restaurant Name",
          "category": "Dining / Food Experience",
          "cuisine": "Cuisine type",
          "description": "What to eat and ambiance",
          "location_name": "Restaurant name & street",
          "lat": {default_lat},
          "lng": {default_lng},
          "cost_usd": 25.0,
          "dietary_tags": "Dietary notes ({dietary})"
        }},
        "afternoon": {{
          "time": "14:30 - 17:30",
          "title": "Afternoon Activity Name",
          "category": "Leisure / Immersion",
          "description": "Engaging activity description",
          "location_name": "Landmark name",
          "lat": {default_lat},
          "lng": {default_lng},
          "cost_usd": 15.0,
          "pro_tip": "Insider recommendation"
        }},
        "evening": {{
          "time": "18:30 - 21:30",
          "title": "Evening Venue / Dinner & Entertainment",
          "category": "Dining & Nightlife",
          "description": "Evening dining and nightlife/sunset",
          "location_name": "Venue or street name",
          "lat": {default_lat},
          "lng": {default_lng},
          "cost_usd": 45.0,
          "pro_tip": "Reservation or timing tip"
        }}
      }}
    }}
  ],
  "emergency_contacts": {{
    "police": "Local Police Number",
    "ambulance": "Local Ambulance Number",
    "tourist_helpline": "Local Tourist Assistance Number",
    "embassy_note": "Consular guidance for travelers"
  }},
  "packing_tips": [
    "Tip 1",
    "Tip 2",
    "Tip 3",
    "Tip 4"
  ]
}}
Strict: Ensure exactly {duration_days} days are provided in the 'days' array.
"""
    system_instruction = "You are a master travel logistics architect. Always respond with mathematically sound, geographically clustered travel plans strictly formatted as valid JSON."

    parsed, error = ai_engine.generate_json(prompt, system_instruction)

    if parsed and "days" in parsed and isinstance(parsed["days"], list) and len(parsed["days"]) > 0:
        try:
            if isinstance(start_date, (datetime, date)):
                s_date = start_date
            else:
                try:
                    s_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()
                except Exception:
                    s_date = date.today()

            running_usd = 0.0
            processed_days = []

            for idx, day in enumerate(parsed["days"]):
                day_num = idx + 1
                day["day_number"] = day_num
                day["date_str"] = (s_date + timedelta(days=idx)).strftime("%b %d, %Y")
                
                day_usd = 0.0
                slots = day.get("slots", {})
                for slot_idx, slot_key in enumerate(["morning", "lunch", "afternoon", "evening"]):
                    slot = slots.get(slot_key, {})
                    c_usd = float(slot.get("cost_usd", 20.0))
                    slot["cost_usd"] = c_usd
                    slot["cost_inr"] = round(c_usd * inr_rate, 0)
                    slot["cost_local"] = round(c_usd * usd_rate, 0)
                    
                    # Ensure valid coordinates
                    try:
                        slot_lat = float(slot.get("lat", default_lat))
                        slot_lng = float(slot.get("lng", default_lng))
                    except (ValueError, TypeError):
                        slot_lat = default_lat + (idx * 0.01)
                        slot_lng = default_lng + (slot_idx * 0.005)

                    if slot_lat == 0.0 or slot_lng == 0.0:
                        slot_lat = default_lat + (idx * 0.01)
                        slot_lng = default_lng + (slot_idx * 0.005)

                    slot["lat"] = round(slot_lat, 4)
                    slot["lng"] = round(slot_lng, 4)

                    day_usd += c_usd
                    slots[slot_key] = slot

                day["slots"] = slots
                day["day_total_usd"] = round(day_usd, 1)
                day["day_total_inr"] = round(day_usd * inr_rate, 0)
                running_usd += day_usd
                day["running_total_usd"] = round(running_usd, 1)
                processed_days.append(day)

            parsed["days"] = processed_days
            parsed["destination"] = destination
            parsed["duration_days"] = len(processed_days)
            parsed["start_date"] = str(s_date)
            parsed["end_date"] = str(s_date + timedelta(days=len(processed_days) - 1))
            parsed["budget_level"] = budget_level
            parsed["travel_party"] = travel_party
            parsed["pace"] = pace
            parsed["interests"] = interests
            parsed["dietary"] = dietary
            parsed["currency"] = currency
            parsed["exchange_rate_to_usd"] = usd_rate
            parsed["exchange_rate_to_inr"] = inr_rate
            parsed["total_estimated_usd"] = round(running_usd, 1)
            parsed["total_estimated_inr"] = round(running_usd * inr_rate, 0)
            parsed["is_dynamic"] = True
            parsed["ai_engine_note"] = f"Live Groq Dynamic Generation ({ai_engine.model_name or 'llama-3.3-70b-versatile'})"

            return parsed
        except Exception as e:
            print(f"Error post-processing AI itinerary: {e}")

    # Fallback if AI generation failed
    print(f"Planner fallback triggered: {error}")
    fb = _build_procedural_itinerary(
        destination, duration_days, start_date, budget_level, travel_party, pace, interests, dietary
    )
    fb["fallback_notice"] = error or "AI generation issue"
    return fb
