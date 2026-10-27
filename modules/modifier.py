"""
Tab 3: Vibe Customization & Dynamic Activity Swap (Epic 4).
Allows modifying specific slots or regenerating single days without wiping the rest of the plan,
preserving geographic clustering and recalculating all budget totals.
"""

from typing import Dict, Any, Tuple, Optional
import copy
from config import EXCHANGE_RATES
from modules.ai_engine import AIEngine


def recalculate_itinerary_totals(itinerary: Dict[str, Any]) -> Dict[str, Any]:
    """Recalculates day totals, running balances, and trip totals across an itinerary."""
    inr_rate = itinerary.get("exchange_rate_to_inr", EXCHANGE_RATES.get("INR", 86.5))
    usd_rate = itinerary.get("exchange_rate_to_usd", 1.0)
    
    running_usd = 0.0
    for day in itinerary.get("days", []):
        day_usd = 0.0
        slots = day.get("slots", {})
        for slot_key in ["morning", "lunch", "afternoon", "evening"]:
            if slot_key in slots:
                slot = slots[slot_key]
                c_usd = float(slot.get("cost_usd", 0.0))
                slot["cost_usd"] = round(c_usd, 1)
                slot["cost_inr"] = round(c_usd * inr_rate, 0)
                slot["cost_local"] = round(c_usd * usd_rate, 0)
                day_usd += c_usd
        
        day["day_total_usd"] = round(day_usd, 1)
        day["day_total_inr"] = round(day_usd * inr_rate, 0)
        running_usd += day_usd
        day["running_total_usd"] = round(running_usd, 1)

    itinerary["total_estimated_usd"] = round(running_usd, 1)
    itinerary["total_estimated_inr"] = round(running_usd * inr_rate, 0)
    return itinerary


def swap_activity_slot(
    itinerary: Dict[str, Any],
    day_number: int,
    slot_key: str,
    modification_prompt: str,
    ai_engine: AIEngine
) -> Tuple[Dict[str, Any], bool, str]:
    """
    Swaps a single activity slot in the itinerary while preserving geographic cluster.
    Returns (updated_itinerary, success_boolean, message).
    """
    new_itin = copy.deepcopy(itinerary)
    days = new_itin.get("days", [])
    
    target_day = None
    for d in days:
        if d.get("day_number") == day_number:
            target_day = d
            break

    if not target_day:
        return itinerary, False, f"Day {day_number} not found."

    slots = target_day.get("slots", {})
    if slot_key not in slots:
        return itinerary, False, f"Slot '{slot_key}' not found in Day {day_number}."

    current_slot = slots[slot_key]
    cluster = target_day.get("cluster_neighborhood", "City Center")
    destination = new_itin.get("destination", "City")
    budget_level = new_itin.get("budget_level", "Moderate")

    # If in Demo Mode or AI fails, provide high-quality context-aware replacement
    if ai_engine.is_demo():
        replacement_slot = _generate_mock_replacement(
            slot_key, modification_prompt, cluster, destination, current_slot
        )
        slots[slot_key] = replacement_slot
        recalculate_itinerary_totals(new_itin)
        return new_itin, True, f"Successfully customized Day {day_number} ({slot_key.capitalize()}) to: '{replacement_slot['title']}'."

    # Call AI Engine
    prompt = f"""
Act as a senior travel logistics architect.
The user wants to swap or customize a single time slot in their travel itinerary:
- Destination: {destination}
- Day Number: {day_number}
- Day Theme / Cluster: {cluster}
- Current Slot: {slot_key} (Title: "{current_slot.get('title')}", Description: "{current_slot.get('description')}")
- Modification Instruction: "{modification_prompt}"
- Budget Tier: {budget_level}

CRITICAL REQUIREMENT:
The replacement activity MUST remain in or adjacent to the geographic cluster "{cluster}" to avoid transit fatigue and preserve the day's route flow.

Return ONLY a JSON object representing the replacement slot with this schema:
{{
  "time": "{current_slot.get('time', '10:00 - 12:00')}",
  "title": "Compelling Title for Replacement Activity",
  "category": "{current_slot.get('category', 'Sightseeing')}",
  "description": "Engaging description fulfilling the user instruction",
  "location_name": "Specific venue or landmark name in {cluster}",
  "lat": {current_slot.get('lat', 0.0)},
  "lng": {current_slot.get('lng', 0.0)},
  "cost_usd": {current_slot.get('cost_usd', 25.0)},
  "pro_tip": "Insider tip or dietary info"
}}
"""
    system_instruction = "You are a master travel optimizer. Return strictly valid JSON for the replacement slot."
    parsed, error = ai_engine.generate_json(prompt, system_instruction)

    if parsed and "title" in parsed:
        # Fill missing attributes from existing slot
        parsed["time"] = current_slot.get("time", "12:00 - 14:00")
        if "lat" not in parsed or not parsed["lat"]:
            parsed["lat"] = current_slot.get("lat", 0.0)
        if "lng" not in parsed or not parsed["lng"]:
            parsed["lng"] = current_slot.get("lng", 0.0)
        
        slots[slot_key] = parsed
        recalculate_itinerary_totals(new_itin)
        return new_itin, True, f"Updated Day {day_number} ({slot_key.capitalize()}): '{parsed['title']}'"

    # Fallback to smart mock replacement if AI fails
    print(f"Swap AI fallback triggered: {error}")
    replacement_slot = _generate_mock_replacement(
        slot_key, modification_prompt, cluster, destination, current_slot
    )
    slots[slot_key] = replacement_slot
    recalculate_itinerary_totals(new_itin)
    return new_itin, True, f"Customized Day {day_number} ({slot_key.capitalize()}): '{replacement_slot['title']}' (Demo Mode fallback)."


def regenerate_single_day(
    itinerary: Dict[str, Any],
    day_number: int,
    vibe_shift_prompt: str,
    ai_engine: AIEngine
) -> Tuple[Dict[str, Any], bool, str]:
    """Regenerates an entire single day according to a new vibe or constraint without touching others."""
    new_itin = copy.deepcopy(itinerary)
    days = new_itin.get("days", [])
    
    target_idx = None
    for idx, d in enumerate(days):
        if d.get("day_number") == day_number:
            target_idx = idx
            break

    if target_idx is None:
        return itinerary, False, f"Day {day_number} not found."

    old_day = days[target_idx]
    destination = new_itin.get("destination", "City")
    budget_level = new_itin.get("budget_level", "Moderate")
    cluster = old_day.get("cluster_neighborhood", "City District")

    # If demo mode
    if ai_engine.is_demo():
        for slot_key in ["morning", "lunch", "afternoon", "evening"]:
            curr = old_day["slots"][slot_key]
            old_day["slots"][slot_key] = _generate_mock_replacement(
                slot_key, vibe_shift_prompt, cluster, destination, curr
            )
        old_day["day_theme"] = f"Day {day_number}: Custom {vibe_shift_prompt[:25]}"
        recalculate_itinerary_totals(new_itin)
        return new_itin, True, f"Day {day_number} regenerated with focus: '{vibe_shift_prompt}'."

    prompt = f"""
Act as a travel architect. Regenerate ALL 4 time slots for Day {day_number} of a trip to {destination}:
- Day Cluster: {cluster}
- New Focus/Theme: "{vibe_shift_prompt}"
- Budget Tier: {budget_level}

Keep all activities clustered in/around {cluster}.
Return ONLY a JSON object:
{{
  "day_theme": "Theme title reflecting the new focus",
  "transit_fatigue_score": "Low (All locations within cluster)",
  "slots": {{
    "morning": {{ "time": "09:00 - 12:00", "title": "...", "category": "...", "description": "...", "location_name": "...", "lat": {old_day['slots']['morning'].get('lat', 0.0)}, "lng": {old_day['slots']['morning'].get('lng', 0.0)}, "cost_usd": 20.0, "pro_tip": "..." }},
    "lunch": {{ "time": "12:30 - 14:00", "title": "...", "category": "...", "cuisine": "...", "description": "...", "location_name": "...", "lat": {old_day['slots']['lunch'].get('lat', 0.0)}, "lng": {old_day['slots']['lunch'].get('lng', 0.0)}, "cost_usd": 25.0, "dietary_tags": "..." }},
    "afternoon": {{ "time": "14:30 - 17:30", "title": "...", "category": "...", "description": "...", "location_name": "...", "lat": {old_day['slots']['afternoon'].get('lat', 0.0)}, "lng": {old_day['slots']['afternoon'].get('lng', 0.0)}, "cost_usd": 15.0, "pro_tip": "..." }},
    "evening": {{ "time": "18:30 - 21:30", "title": "...", "category": "...", "description": "...", "location_name": "...", "lat": {old_day['slots']['evening'].get('lat', 0.0)}, "lng": {old_day['slots']['evening'].get('lng', 0.0)}, "cost_usd": 40.0, "pro_tip": "..." }}
  }}
}}
"""
    system_instruction = "Return strictly valid JSON with 4 time slots."
    parsed, error = ai_engine.generate_json(prompt, system_instruction)

    if parsed and "slots" in parsed:
        old_day["day_theme"] = parsed.get("day_theme", f"Day {day_number}: Custom Overhaul")
        old_day["slots"] = parsed["slots"]
        recalculate_itinerary_totals(new_itin)
        return new_itin, True, f"Day {day_number} successfully refreshed with: {vibe_shift_prompt}"

    # Fallback
    for slot_key in ["morning", "lunch", "afternoon", "evening"]:
        curr = old_day["slots"][slot_key]
        old_day["slots"][slot_key] = _generate_mock_replacement(
            slot_key, vibe_shift_prompt, cluster, destination, curr
        )
    old_day["day_theme"] = f"Day {day_number}: {vibe_shift_prompt[:25]}"
    recalculate_itinerary_totals(new_itin)
    return new_itin, True, f"Day {day_number} updated with fallback logic."


def _generate_mock_replacement(
    slot_key: str,
    prompt: str,
    cluster: str,
    destination: str,
    current_slot: Dict[str, Any]
) -> Dict[str, Any]:
    """Generates a realistic contextual replacement activity for demo mode."""
    p_lower = prompt.lower()
    rep = copy.deepcopy(current_slot)

    if "market" in p_lower or "outdoor" in p_lower:
        rep["title"] = f"Bustling Artisan & Farmers' Market in {cluster.split()[0]}"
        rep["category"] = "Local Markets & Craft"
        rep["description"] = f"Immerse yourself in open-air stalls filled with local crafts, fresh seasonal fruits, artisan souvenirs, and friendly local street vendors."
        rep["cost_usd"] = 15.0
        rep["pro_tip"] = "Carry small cash bills for local vendors and arrive by 10 AM for freshest goods."
    elif "vegetarian" in p_lower or "vegan" in p_lower or "plant" in p_lower:
        rep["title"] = f"Organic Garden Plant-Based Bistro in {cluster.split()[0]}"
        rep["category"] = "Dining / Food Experience"
        rep["cuisine"] = "100% Plant-Based & Organic Farm-to-Table"
        rep["description"] = f"Delight in creative vegetarian culinary creations featuring seasonal local vegetables, heritage grains, fresh herb emulsions, and raw pressed juices."
        rep["cost_usd"] = 28.0
        rep["dietary_tags"] = "Certified 100% Vegan & Vegetarian, Gluten-Free options"
    elif "adventure" in p_lower or "hiking" in p_lower or "active" in p_lower:
        rep["title"] = f"High-Energy Scenic Ridge Hike & Viewpoint Challenge"
        rep["category"] = "Adventure & Outdoors"
        rep["description"] = f"Take an invigorating trek along scenic trailheads bordering {destination}, climbing to panoramic overlooks with sweeping valley and sea views."
        rep["cost_usd"] = 20.0
        rep["pro_tip"] = "Wear sturdy trail shoes and carry at least 1 liter of water."
    elif "rain" in p_lower or "indoor" in p_lower or "museum" in p_lower:
        rep["title"] = f"Interactive Cultural Pavilion & Historic Exhibition"
        rep["category"] = "Arts & Heritage"
        rep["description"] = f"Stay dry inside an award-winning covered heritage museum featuring interactive audio guides, centuries-old artifacts, and warm cafe lounges."
        rep["cost_usd"] = 22.0
        rep["pro_tip"] = "Cloakroom and luggage lockers are free at the visitor welcome desk."
    elif "kid" in p_lower or "family" in p_lower:
        rep["title"] = f"Family-Friendly Interactive Science & Discovery Garden"
        rep["category"] = "Family & Kids Fun"
        rep["description"] = f"Enjoy hands-on exhibits, shaded botanical play lawns, and sweet local pastry treats beloved by travelers of all ages."
        rep["cost_usd"] = 18.0
        rep["pro_tip"] = "Stroller accessible with clean nursery facilities on site."
    else:
        rep["title"] = f"Curated Experience: {prompt.capitalize()}"
        rep["category"] = "Custom Immersion"
        rep["description"] = f"Tailored activity in {cluster} designed specifically for your preference: {prompt}. Perfectly integrated into your day's walking flow."
        rep["cost_usd"] = current_slot.get("cost_usd", 25.0)

    return rep
