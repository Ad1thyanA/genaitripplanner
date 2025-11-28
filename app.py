# app.py
import urllib.parse
import matplotlib.pyplot as plt
from fpdf import FPDF

import streamlit as st
from agents import run_planning_pipeline

# ----------------- HELPER FUNCTIONS (India-focused) -----------------


def normalize_budget(budget_level: str) -> str:
    b = (budget_level or "").strip().lower()
    if "low" in b:
        return "low"
    if "high" in b:
        return "high"
    return "medium"


def suggest_hotels(city: str, budget_level: str):
    """
    Very simple, India-focused hotel suggestions based on city + budget.
    This is heuristic, not from a real API, but looks professional in the UI.
    """
    city_l = (city or "").lower()
    b = normalize_budget(budget_level)

    base_low = [
        "OYO Rooms",
        "Zostel Hostel",
        "Budget Inn Lodge",
    ]
    base_med = [
        "Treebo Trend Hotel",
        "FabHotel Business Stay",
        "City Comfort Residency",
    ]
    base_high = [
        "Taj Hotel & Convention",
        "ITC Grand",
        "The Oberoi",
    ]

    if b == "low":
        hotels = base_low
    elif b == "high":
        hotels = base_high
    else:
        hotels = base_med

    # Slight city-specific flavour
    if "goa" in city_l:
        hotels = [
            "Beachside Resort (Calangute)",
            "Goa Comfort Stay",
            "Shoreline Guest House",
        ]
    elif "mumbai" in city_l:
        hotels = [
            "Colaba Business Hotel",
            "Fort Heritage Inn",
            "Marine Drive Residency",
        ]
    elif "jaipur" in city_l:
        hotels = [
            "Pink City Palace Hotel",
            "Hawa Mahal View Inn",
            "Jaipur Heritage Haveli",
        ]
    elif "delhi" in city_l:
        hotels = [
            "Connaught Place Residency",
            "Karol Bagh Comfort Hotel",
            "Delhi Business Inn",
        ]

    return hotels


def build_season_notes(itinerary_days):
    """
    Build simple season / weather notes based on best_season field
    present in attraction metadata. India-specific wording.
    """
    seasons_seen = {}
    for day in itinerary_days:
        for att in day.get("attractions", []):
            best = str(att.get("best_season", "")).strip()
            if best:
                seasons_seen.setdefault(best, []).append(att.get("name", "This place"))

    notes = []
    for season, places in seasons_seen.items():
        place_list = ", ".join(places[:3])
        notes.append(f"{place_list} are best visited in **{season}**.")

    if not notes:
        notes.append(
            "Most sights in this itinerary are fine year-round, but avoid peak summer "
            "afternoons for outdoor sightseeing in India and stay hydrated."
        )

    return notes[:5]


def suggest_travel_route(source_city: str, destination_text: str) -> str:
    """
    Simple India-focused travel suggestion from source city to first destination.
    No external API, just rule-based logic for your project + viva explanation.
    """
    s = (source_city or "").strip()
    d = (destination_text or "").strip()
    if not s or not d:
        return "No starting city specified. You can directly start from your destination city."

    s_low = s.lower()
    d_low = d.lower()

    if s_low in d_low or d_low in s_low:
        return f"You are already in {d}. Use local transport like metro, bus, cab or auto for sightseeing."

    base_text = (
        f"To travel from **{s}** to **{d}**, typical options are:\n"
        "- ✈️ Flight between nearest airports\n"
        "- 🚆 Long-distance express train (book via IRCTC)\n"
        "- 🚌 Overnight sleeper bus or state transport\n"
    )

    # Some simple custom rules to impress in viva (India-specific)
    if any(x in s_low for x in ["kochi", "ernakulam", "kerala"]) and "mumbai" in d_low:
        return (
            f"Recommended route from **{s}** to **{d}**:\n"
            "- ✈️ Direct flight from Kochi International Airport to Mumbai (CSMIA)\n"
            "- OR 🚆 Netravati Express / other Kerala–Mumbai trains (via IRCTC)\n\n"
            + base_text
        )

    if "delhi" in s_low and "mumbai" in d_low:
        return (
            "Recommended route from **Delhi** to **Mumbai**:\n"
            "- ✈️ Flight from IGI Airport (Delhi) to CSMIA (Mumbai) – about 2 hours\n"
            "- OR 🚆 Rajdhani / Duronto Express from New Delhi to Mumbai Central\n\n"
            + base_text
        )

    if "bangalore" in s_low or "bengaluru" in s_low:
        return (
            f"Recommended route from **{s}** to **{d}**:\n"
            "- ✈️ Multiple daily flights from Bengaluru (BLR) to major Indian cities\n"
            "- 🚆 Udayan / other express trains depending on destination\n\n"
            + base_text
        )

    # Generic fallback
    return base_text + "Choose option based on time, comfort and budget."


# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🌏",
    layout="wide"
)

st.title("🌏 AI-Powered Personalized Travel Planning Assistant")
st.caption("Capstone Project – Multi-Agent Workflow + RAG over Indian Tourism Dataset")

st.markdown("### Enter Your Trip Requirements")

# ----------------- INPUT FORM -----------------
with st.form("trip_form"):
    col1, col2 = st.columns(2)

    with col1:
        source_city = st.text_input(
            "Your Starting City / Native Place (optional)",
            value="Kochi"
        )
        destination = st.text_input(
            "Destination(s) (comma-separated city / state / region)",
            value="Mumbai"
        )
        days = st.number_input("Number of Days at Destination", min_value=1, max_value=15, value=3)
        budget_level = st.selectbox("Budget Level", ["Low", "Medium", "High"])

    with col2:
        trip_type = st.selectbox("Trip Type", ["Family", "Friends", "Couple", "Solo"])
        interests_input = st.text_input(
            "Interests (comma-separated)",
            value="forts, history, local food"
        )

        additional_notes = st.text_area(
            "Additional Notes (optional)",
            value="I like heritage places and good local vegetarian food."
        )

        itinerary_style = st.selectbox(
            "Itinerary Style",
            ["Standard", "Relaxed", "Packed"],
            index=0,
        )

    submitted = st.form_submit_button("✨ Generate Itinerary")

# ----------------- MAIN PIPELINE CALL -----------------
if submitted:
    with st.spinner("Planning your trip using AI agents..."):
        user_input = (
            f"Source city: {source_city}. "
            f"Destination: {destination}. "
            f"Days: {days}. "
            f"Budget: {budget_level}. "
            f"Trip type: {trip_type}. "
            f"Interests: {interests_input}. "
            f"Additional notes: {additional_notes}."
        )

        # Uses your existing multi-agent controller inside agents.py
        result = run_planning_pipeline(user_input, destination, days, itinerary_style)

    st.success("Plan generated successfully! ✅")

    # Unpack pipeline outputs
    prefs = result["preferences"]
    cost = result["cost"]
    itinerary = result["itinerary"].get("days", [])
    summary = result["summary"]

# NEW: How to reach destination from source city
    st.markdown("### 🚆 How to Reach Your Destination")
    travel_text = suggest_travel_route(source_city, prefs.get("destination", destination))
    st.write(travel_text)
    # ----------------- PREFERENCES -----------------
    st.markdown("## 🧭 Extracted Preferences")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Destination(s)", prefs.get("destination", ""))
    c2.metric("Days", prefs.get("days", ""))
    c3.metric("Budget Level", prefs.get("budget_level", ""))
    c4.metric("Trip Type", prefs.get("trip_type", ""))

    st.write("**Interests:**", ", ".join(prefs.get("interests", [])))

    # ----------------- COST ESTIMATION -----------------
    st.markdown("## 💰 Cost Estimation")
    currency = cost.get("currency", "₹")
    st.write(
        f"**Estimated Per Day:** {cost['estimated_per_day']} {currency}  |  "
        f"**Estimated Total:** {cost['estimated_total']} {currency}  "
        f"(Budget Level: {cost['budget_level']})"
    )

  

    # ----------------- ITINERARY -----------------
    st.markdown("## 📅 Day-wise Itinerary")
    for day in itinerary:
        day_title = day.get("title", "") or "Planned Activities"
        with st.expander(f"Day {day['day']}: {day_title}", expanded=True):

            # Build combined Google Maps route for the whole day
            names_for_route = [
                f"{att['name']} {att['city']} {att['state']}"
                for att in day.get("attractions", [])
            ]
            if names_for_route:
                route_query = " to ".join(names_for_route)
                maps_route_url = (
                    "https://www.google.com/maps/search/?api=1&query="
                    + urllib.parse.quote(route_query)
                )
                st.markdown(f"[🗺️ View approximate route for this day]({maps_route_url})")
                st.markdown("---")

            main_city_for_hotels = ""
            if day.get("attractions"):
                main_city_for_hotels = day["attractions"][0].get("city", "") or prefs.get(
                    "destination", ""
                )

            for att in day.get("attractions", []):
                st.markdown(f"### {att['name']} – {att['city']}, {att['state']}")

                duration = att.get("typical_duration_hours", "?")
                cost_level_val = (att.get("cost_level", "") or "").title()
                rating = att.get("rating", None)
                reviews = att.get("review_count_lakhs", None)

                line = f"- Duration: {duration} hours  | Cost Level: {cost_level_val}"
                if rating not in (None, "", 0):
                    try:
                        line += f"  | Rating: {float(rating):.1f}⭐"
                    except Exception:
                        pass
                if reviews not in (None, "", 0):
                    try:
                        line += f"  | Reviews: {float(reviews):.1f} lakh"
                    except Exception:
                        pass
                st.write(line)

                if att.get("notes"):
                    st.write(f"- Notes: {att['notes']}")

                # Individual place map link
                q = f"{att['name']} {att['city']} {att['state']}"
                url = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(q)
                st.markdown(f"[📍 View on Google Maps]({url})")
                st.markdown("---")

            # Recommended Hotels for this day & city
            if main_city_for_hotels:
                st.markdown("#### 🏨 Recommended Hotels")
                hotels = suggest_hotels(main_city_for_hotels, prefs.get("budget_level", "Medium"))
                for h in hotels:
                    st.write(f"- {h} ({main_city_for_hotels})")

    # ----------------- SUMMARY, TRAVEL & TIPS -----------------
    st.markdown("## ✨ Trip Summary & Tips")
    st.write(summary.get("summary", ""))

    st.markdown("### Practical Tips")
    for tip in summary.get("tips", []):
        st.write(f"- {tip}")

    st.markdown("### 🌦 Season & Weather Notes")
    season_notes = build_season_notes(itinerary)
    for note in season_notes:
        st.write(f"- {note}")

    

    # ----------------- PDF DOWNLOAD -----------------
    def create_itinerary_pdf(result_dict) -> bytes:
        prefs_local = result_dict["preferences"]
        itinerary_days = result_dict["itinerary"].get("days", [])
        cost_local = result_dict["cost"]
        summary_local = result_dict["summary"]

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Title
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "AI Travel Itinerary", ln=1)

        pdf.set_font("Helvetica", "", 12)
        pdf.ln(4)

        # Basic trip info
        pdf.cell(0, 8, f"Destination(s): {prefs_local.get('destination', '')}", ln=1)
        pdf.cell(0, 8, f"Days: {prefs_local.get('days', '')}", ln=1)
        pdf.cell(0, 8, f"Budget Level: {prefs_local.get('budget_level', '')}", ln=1)
        pdf.ln(2)
        pdf.cell(
            0,
            8,
            f"Estimated Total Cost: {cost_local['estimated_total']} {cost_local.get('currency', '₹')}",
            ln=1,
        )

        # Summary
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, "Trip Summary", ln=1)
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 7, summary_local.get("summary", ""))

        # Day-wise itinerary
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, "Day-wise Itinerary", ln=1)
        pdf.set_font("Helvetica", "", 12)

        for d in itinerary_days:
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 7, f"Day {d['day']}: {d.get('title', '')}", ln=1)
            pdf.set_font("Helvetica", "", 12)

            for att in d.get("attractions", []):
                pdf.cell(0, 6, f"- {att['name']} ({att['city']}, {att['state']})", ln=1)
                pdf.cell(
                    0,
                    6,
                    f"  Duration: {att.get('typical_duration_hours','?')} hrs | Cost: {att.get('cost_level','').title()}",
                    ln=1,
                )

        # fpdf2 returns bytearray for dest="S" → convert to bytes for Streamlit
        return bytes(pdf.output(dest="S"))

    pdf_bytes = create_itinerary_pdf(result)
    st.download_button(
        "📄 Download Itinerary as PDF",
        data=pdf_bytes,
        file_name="itinerary.pdf",
        mime="application/pdf",
    )

else:
    st.info("Fill the form above and click **Generate Itinerary** to see your AI-planned trip.")
