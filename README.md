AI Travel Planner (Multi-Agent RAG System)
Project Overview

This application generates a personalized travel itinerary based on:

Destination

Number of days

Budget level

Travel group (family, solo, couple, friends)

Interests

The system retrieves real tourist locations using a vector database and creates a day-wise travel plan with cost estimation, hotel suggestions, and map links.

Features

Personalized travel itinerary generation

Real attraction retrieval (using RAG)

Cost estimation (budget-based)

Ratings and duration for each attraction

Google Maps location support

PDF download of itinerary

Technologies Used

Python

Streamlit (Web UI)

LangChain (Multi-Agent workflow)

FAISS (Vector Database)

Sentence Transformer Embeddings

FPDF (PDF Generation)

Installation and Setup
Prerequisites

Python 3.10 or above

Internet connection (for model usage)

Steps to Run

Clone or download this repository

Open terminal in project folder

Create and activate virtual environment

python -m venv venv
venv\Scripts\activate   (Windows)


Install dependencies

pip install -r requirements.txt


Run the application

streamlit run app.py


Open the link displayed in terminal in a browser
(Default: http://localhost:8501
)

How To Use

Enter destination (example: Mumbai)

Select number of days for travel

Choose budget level and trip type

Enter interests (example: beaches, history, food)

Click "Generate Itinerary"

Download PDF if needed
