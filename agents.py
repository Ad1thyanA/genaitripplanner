# agents.py

from typing import Dict, Any, List
from config import get_llm
from rag_pipeline import TourismRAGPipeline
from utils import score_attraction, estimate_daily_cost

llm = get_llm()
rag = TourismRAGPipeline()

# 1. Preference Extraction Agent

PREFERENCE_EXTRACTION_SYSTEM_PROMPT = """
You are a travel preference extraction assistant.
Given a user's free-form text about a trip, extract structured fields as JSON:
- destination (string, city/state/region)
- days (integer number of days)
- budget_level (one of: low, medium, high)
- trip_type (one of: family, friends, couple, solo; choose closest)
- interests (list of 3-6 keywords like: nature, adventure, temples, beaches, food, nightlife, culture, history)

If something is not explicitly given, make a reasonable assumption.
Return ONLY valid JSON, no explanation.
"""

def extract_preferences(user_input: str) -> Dict[str, Any]:
    prompt = f"{PREFERENCE_EXTRACTION_SYSTEM_PROMPT}\n\nUser Input:\n{user_input}"
    response = llm.invoke(prompt)
    import json
    try:
        data = json.loads(response.content)
    except Exception:
        # fallback: simple default
        data = {
            "destination": "Goa",
            "days": 3,
            "budget_level": "medium",
            "trip_type": "friends",
            "interests": ["beach", "nightlife"]
        }
    return data


# 2. RAG Retrieval Agent

def retrieve_attractions(preferences: Dict[str, Any], max_results: int = 15) -> List[Dict[str, Any]]:
    destination = preferences.get("destination", "")
    interests = preferences.get("interests", [])
    if not isinstance(interests, list):
        interests = [interests]
    raw_results = rag.search_attractions(destination, interests, k=max_results)

    # Re-score based on preferences
    scored = []
    for a in raw_results:
        s = score_attraction(a, interests, preferences.get("trip_type", ""), preferences.get("budget_level", "medium"))
        a["score"] = s
        scored.append(a)
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


# 3. Itinerary Planning Agent

ITINERARY_PLANNER_SYSTEM_PROMPT = """
You are an expert travel planner.
You receive:
- a destination
- number of days
- list of candidate attractions with metadata (name, city, tags, duration hours, cost_level)
- user preferences (trip type, interests, budget level)

Goal:
Create a realistic, day-wise itinerary.
Rules:
- 2 to 4 main attractions per day depending on duration hours.
- Group nearby attractions (same city/region) in the same day if possible.
- Respect budget_level and avoid too many 'high' cost_level attractions for low budget.
- Mix experiences (e.g., not all temples in one day if possible).
- Make sure each day is not overloaded in total hours (>8 hours).

Return the itinerary in structured JSON:
{
  "days": [
    {
      "day": 1,
      "title": "Short text title",
      "attractions": [
        {
          "name": "...",
          "city": "...",
          "state": "...",
          "typical_duration_hours": 3,
          "cost_level": "medium",
          "notes": "short explanation for this attraction in context of trip"
        }
      ]
    }
  ]
}
No extra text, only JSON.
"""

def plan_itinerary(
    preferences: Dict[str, Any],
    attractions: List[Dict[str, Any]],
    itinerary_style: str = "standard",
) -> Dict[str, Any]:
    import json

    days = max(int(preferences.get("days", 3)), 1)

    # Limit to top N attractions depending on style
    base_per_day = 3
    style = (itinerary_style or "standard").lower()
    if "relaxed" in style:
        per_day = 2
    elif "packed" in style:
        per_day = 4
    else:
        per_day = base_per_day

    top_attractions = attractions[: max(days * per_day, days * 2)]


    # Prepare a compact list for the LLM
    compact_list = []
    for a in top_attractions:
        compact_list.append(
            {
                "name": a.get("name"),
                "city": a.get("city"),
                "state": a.get("state"),
                "tags": a.get("tags"),
                "typical_duration_hours": a.get("typical_duration_hours"),
                "cost_level": a.get("cost_level"),
            }
        )

    planner_input = {
        "destination": preferences.get("destination"),
        "days": days,
        "trip_type": preferences.get("trip_type"),
        "budget_level": preferences.get("budget_level"),
        "interests": preferences.get("interests"),
        "itinerary_style": itinerary_style,
        "candidate_attractions": compact_list,
    }

    prompt = ITINERARY_PLANNER_SYSTEM_PROMPT + "\n\nData:\n" + json.dumps(planner_input, indent=2)
    response = llm.invoke(prompt)
    try:
        itinerary = json.loads(response.content)
    except Exception:
        # Fallback very simple itinerary if parsing fails
        fallback_days = []
        per_day = max(1, len(top_attractions) // days)
        idx = 0
        for d in range(1, days + 1):
            day_atts = top_attractions[idx:idx+per_day]
            idx += per_day
            day_obj = {
                "day": d,
                "title": f"Day {d} in {preferences.get('destination', '')}",
                "attractions": []
            }
            for a in day_atts:
                day_obj["attractions"].append(
                    {
                        "name": a.get("name"),
                        "city": a.get("city"),
                        "state": a.get("state"),
                        "typical_duration_hours": a.get("typical_duration_hours"),
                        "cost_level": a.get("cost_level"),
                        "notes": ""
                    }
                )
            fallback_days.append(day_obj)
        itinerary = {"days": fallback_days}
    return itinerary


# 4. Cost Estimation Agent

def estimate_cost(preferences: Dict[str, Any], itinerary: Dict[str, Any]) -> Dict[str, Any]:
    days = max(int(preferences.get("days", 3)), 1)
    budget_level = preferences.get("budget_level", "medium")
    per_day = estimate_daily_cost(budget_level)
    total = per_day * days

    return {
        "budget_level": budget_level,
        "estimated_per_day": per_day,
        "estimated_total": total,
        "currency": "INR"
    }


# 5. Response Generation Agent

RESPONSE_SUMMARY_SYSTEM_PROMPT = """
You are a helpful travel assistant.
Given:
- user preferences
- a day-wise itinerary
- a cost estimation

Generate:
- A concise trip summary paragraph (3-6 sentences)
- 4-6 practical travel tips for this destination and trip type.

Return response as JSON:
{
  "summary": "...",
  "tips": ["...", "..."]
}
No extra explanation.
"""

def generate_summary_and_tips(preferences: Dict[str, Any], itinerary: Dict[str, Any], cost_info: Dict[str, Any]) -> Dict[str, Any]:
    import json
    data = {
        "preferences": preferences,
        "itinerary": itinerary,
        "cost": cost_info,
    }
    prompt = RESPONSE_SUMMARY_SYSTEM_PROMPT + "\n\nData:\n" + json.dumps(data, indent=2)
    response = llm.invoke(prompt)
    try:
        obj = json.loads(response.content)
    except Exception:
        obj = {
            "summary": "This is a multi-day trip plan generated based on your preferences.",
            "tips": [
                "Carry basic medicines and a water bottle.",
                "Check local weather before packing.",
            ],
        }
    return obj


# 6. Orchestrator function

def run_planning_pipeline(user_input: str) -> Dict[str, Any]:
    """
    High-level orchestration: acts as the 'multi-agent' controller.
    """
    preferences = extract_preferences(user_input)
    attractions = retrieve_attractions(preferences)
    itinerary = plan_itinerary(preferences, attractions)
    cost_info = estimate_cost(preferences, itinerary)
    summary_info = generate_summary_and_tips(preferences, itinerary, cost_info)

    return {
        "preferences": preferences,
        "attractions": attractions,
        "itinerary": itinerary,
        "cost": cost_info,
        "summary": summary_info,
    }
def run_planning_pipeline(
    user_input: str,
    explicit_destination: str,
    explicit_days: int,
    itinerary_style: str,
) -> Dict[str, Any]:
    """
    High-level orchestration: acts as the 'multi-agent' controller.
    We override destination and days from the UI, and pass itinerary_style
    to the planner.
    """
    preferences = extract_preferences(user_input)

    # Override from UI
    if explicit_destination:
        preferences["destination"] = explicit_destination
    if explicit_days:
        try:
            preferences["days"] = int(explicit_days)
        except Exception:
            pass
    preferences["itinerary_style"] = itinerary_style

    attractions = retrieve_attractions(preferences)
    itinerary = plan_itinerary(preferences, attractions, itinerary_style)
    cost_info = estimate_cost(preferences, itinerary)
    summary_info = generate_summary_and_tips(preferences, itinerary, cost_info)

    return {
        "preferences": preferences,
        "attractions": attractions,
        "itinerary": itinerary,
        "cost": cost_info,
        "summary": summary_info,
    }
