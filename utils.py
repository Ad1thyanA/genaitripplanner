# utils.py
from typing import List, Dict, Any

def normalize_budget_level(budget_level: str) -> str:
    bl = (budget_level or "").strip().lower()
    if "low" in bl:
        return "low"
    if "high" in bl:
        return "high"
    return "medium"

def score_attraction(
    attraction: Dict[str, Any],
    interests: List[str],
    trip_type: str,
    budget_level: str
) -> float:
    """
    Scoring combines:
    - interest tag match
    - budget suitability
    - Google rating
    - number of reviews
    """
    score = 0.0
    tags = (attraction.get("tags") or "").lower()
    bl = normalize_budget_level(budget_level)

    # Interest match
    for interest in interests:
        if interest.lower().strip() in tags:
            score += 2.0

    # Trip type (very light influence)
    tt = (trip_type or "").lower()
    if "family" in tt and "nightlife" in tags:
        score -= 1.0
    if "couple" in tt and "romantic" in tags:
        score += 1.0

    # Budget influence
    cost_level = str(attraction.get("cost_level", "")).lower()
    if bl == "low" and cost_level == "low":
        score += 1.5
    elif bl == "high" and cost_level == "high":
        score += 1.5

    # Rating & reviews
    try:
        rating = float(attraction.get("rating", 0.0))
    except:
        rating = 0.0
    try:
        reviews_lakhs = float(attraction.get("review_count_lakhs", 0.0))
    except:
        reviews_lakhs = 0.0

    score += rating * 0.8           # 0–4 extra approx
    score += min(reviews_lakhs, 5) * 0.5  # cap influence

    return score

def estimate_daily_cost(budget_level: str) -> int:
    bl = normalize_budget_level(budget_level)
    if bl == "low":
        return 1500
    if bl == "high":
        return 4000
    return 2500
