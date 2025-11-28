AI Travel Planner + Smart Route & Budget Advisor (Multi-Agent RAG System)

Project: AI-Powered Personalized Tourism Planning Assistant
Author: Adithyan A
Course: BCA 5th Sem — Capstone Project
Guide: Mr. Anirudha S I
Technologies: RAG + Multi-Agent AI + Streamlit
Status: Fully working prototype (PDF Export + Routing)
Repo: AI-Travel-Planner/

🔍 Overview

This project generates a personalized travel plan based on:

Destination(s)

Number of days

Budget level (Low / Medium / High)

Travel group (Family / Solo / Couple / Friends)

Interests (Beaches, History, Food, Adventure, etc.)

It uses:

Component	Role
Preference Agent	Understands user needs
RAG Retrieval	Finds real attractions using embeddings + FAISS
Planning Agent	Builds day-wise itinerary
Costing Agent	Estimates trip cost
Route Advisor	Suggests how to reach destination

✔ Hotel suggestions included
✔ Google Maps link for each attraction
✔ PDF itinerary download
✔ Multi-city routing support
✔ Tested with multiple Indian destinations

🧠 Architecture
User Input →
Preference Agent →
RAG Search (FAISS + Embeddings) →
Planning Agent →
Streamlit UI (Maps + PDF Export)


Vector Model → sentence-transformers/all-mpnet-base-v2
Frontend → Streamlit
Backend → Python (LangChain Multi-Agent)

✨ Key Features

Day-wise itinerary with duration & best timings

Ratings + Review count

Cost estimation (budget-aware)

Hotels near each location

Live Google Maps directions

Downloadable PDF itinerary

📦 Dataset

processed_tourism_data.json
→ Curated from India Tourism datasets
→ Contains 350+ real attractions with:

State, City & Tags

Review rating

Duration needed

Entry fee / cost factor

Supports fast similarity search using embeddings.

▶️ Quickstart (Windows)

1️⃣ Activate virtual environment

python -m venv venv
.\venv\Scripts\activate


2️⃣ Install dependencies

pip install -r requirements.txt


3️⃣ Run application

streamlit run app.py

📂 Project Structure
AI-Travel-Planner/
│ app.py                → Streamlit UI + PDF + Maps
│ agents.py             → Multi-Agent Workflow
│ rag_pipeline.py       → RAG + Embeddings + FAISS
│ processed_tourism_data.json
│ requirements.txt
└─ README.md

🧪 Testing Status
Test	Result
Itinerary generation	✔ Passed
Cost estimation	✔ Accurate
PDF Export	✔ Working
Maps Deep Link	✔ Verified
Multi-city input	✔ Supported

Screenshots available in final project report.

🚀 Future Enhancements

Live train/flight booking API

Crowd & weather prediction

Android mobile app version

Offline city maps with navigation

Voice-enabled tourist guide

👨‍🎓 Author
Adithyan A	

Guided by: Mr. Anirudha S I

License

Academic & research use only.
Not for commercial deployment.
