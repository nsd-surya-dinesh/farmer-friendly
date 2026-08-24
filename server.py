"""
server.py — Farmer Friendly backend
AgriN & Regenerative Agricultural Intelligence track.

Two AI-powered flows:
  1. Crop disease diagnosis from an uploaded photo (Gemini Vision)
  2. Regenerative crop recommendations based on state, soil type, and
     season (Gemini text, grounded in a representative regional
     soil/climate context table)

Both flows are stored and aggregated into a state cooperation dashboard,
so different states can see shared agricultural patterns — the
"digital public good" / cross-state collaboration piece of the brief.
"""

import os
import io
import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
DB_FILE = "farmer_friendly.db"

app = Flask(__name__)
CORS(app)

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-3.6-flash")
else:
    model = None

# Representative soil/climate context per state. In production this would
# be sourced from real satellite data (e.g. Google Earth Engine), soil
# health card data, and IMD weather forecasts. Documented honestly in
# README as a next step — this table is a realistic stand-in so the AI
# reasoning is regionally grounded even without live data feeds.
STATE_CONTEXT = {
    "Andhra Pradesh": "coastal & inland mix, red/black soils, tropical climate, monsoon-dependent",
    "Uttar Pradesh": "alluvial soils, subtropical climate, high groundwater dependence",
    "Maharashtra": "black cotton soil in interior, semi-arid to tropical, drought-prone in parts",
    "Bihar": "alluvial floodplain soils, subtropical climate, flood-prone in monsoon",
    "Tamil Nadu": "red & laterite soils, tropical climate, dependent on both monsoons",
    "Rajasthan": "arid sandy soils, hot desert climate, severe water scarcity",
    "West Bengal": "alluvial delta soils, humid subtropical, high flood/cyclone exposure",
    "Karnataka": "red & black soils, semi-arid interior with coastal wet zone",
    "Punjab": "alluvial soils, subtropical, intensive irrigation-dependent agriculture",
    "Gujarat": "black & sandy coastal soils, semi-arid to arid, salinity concerns in coastal belts",
}

SEASONS = ["Kharif (Monsoon)", "Rabi (Winter)", "Zaid (Summer)"]


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnoses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT,
            diagnosis_summary TEXT,
            confidence TEXT,
            full_response TEXT,
            submitted_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT,
            soil_type TEXT,
            season TEXT,
            recommended_crops TEXT,
            full_response TEXT,
            submitted_at TEXT
        )
    """)
    conn.commit()
    conn.close()


# ===================== Crop disease diagnosis =====================

@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    state = request.form.get("state", "Unknown")
    image_file = request.files["image"]

    try:
        image = Image.open(io.BytesIO(image_file.read()))
    except Exception as e:
        return jsonify({"error": f"Could not read image: {e}"}), 400

    if model is None:
        return jsonify({"error": "Server is missing a Gemini API key. Set GOOGLE_API_KEY in .env."}), 500

    context = STATE_CONTEXT.get(state, "general Indian farming context, no specific regional data available")

    prompt = f"""You are an agricultural extension expert. A farmer in {state}, India
({context}) has uploaded a photo of their crop.

Respond ONLY with a valid JSON object, no other text, in this exact format:
{{
  "diagnosis": "<short name of the disease/pest/deficiency, or 'Healthy' if no issue visible>",
  "confidence": "<Low, Medium, or High>",
  "explanation": "<plain-language explanation under 40 words>",
  "regenerative_actions": "<2-3 practical, low-cost, preferably regenerative/organic next steps under 60 words>"
}}"""

    try:
        response = model.generate_content([prompt, image])
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        result = json.loads(text.strip())
    except Exception as e:
        return jsonify({"error": f"Gemini request failed: {e}"}), 500

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO diagnoses (state, diagnosis_summary, confidence, full_response, submitted_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        state, result.get("diagnosis", "Unknown"), result.get("confidence", "Medium"),
        json.dumps(result), datetime.now().isoformat(),
    ))
    conn.commit()
    conn.close()

    return jsonify(result)


# ===================== Regenerative crop recommendation =====================

@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.get_json(force=True)
    state = data.get("state", "Unknown")
    soil_type = data.get("soil_type", "Unspecified")
    season = data.get("season", "Unspecified")

    if model is None:
        return jsonify({"error": "Server is missing a Gemini API key. Set GOOGLE_API_KEY in .env."}), 500

    context = STATE_CONTEXT.get(state, "general Indian farming context, no specific regional data available")

    prompt = f"""You are an agricultural extension expert advising a farmer in {state}, India
({context}). The farmer describes their soil as: {soil_type}. It is currently
the {season} season.

Respond ONLY with a valid JSON object, no other text, in this exact format:
{{
  "recommended_crops": "<2-3 specific crop names well-suited to this soil/season/region>",
  "regenerative_practices": "<2-3 regenerative/sustainable practices suited to this context, under 60 words>",
  "climate_note": "<one sentence on the main climate risk to plan around this season, under 25 words>"
}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        result = json.loads(text.strip())
    except Exception as e:
        return jsonify({"error": f"Gemini request failed: {e}"}), 500

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recommendations (state, soil_type, season, recommended_crops, full_response, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        state, soil_type, season, result.get("recommended_crops", ""),
        json.dumps(result), datetime.now().isoformat(),
    ))
    conn.commit()
    conn.close()

    return jsonify(result)


# ===================== State cooperation dashboard =====================

@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM diagnoses ORDER BY submitted_at DESC")
    diagnoses = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM recommendations ORDER BY submitted_at DESC")
    recommendations = [dict(row) for row in cursor.fetchall()]

    conn.close()

    diagnoses_by_state = {}
    for d in diagnoses:
        diagnoses_by_state.setdefault(d["state"], []).append(d)

    recs_by_state = {}
    for r in recommendations:
        recs_by_state.setdefault(r["state"], []).append(r)

    issue_counts = {}
    for d in diagnoses:
        issue_counts[d["diagnosis_summary"]] = issue_counts.get(d["diagnosis_summary"], 0) + 1

    return jsonify({
        "total_diagnoses": len(diagnoses),
        "total_recommendations": len(recommendations),
        "states_participating": len(set(list(diagnoses_by_state.keys()) + list(recs_by_state.keys()))),
        "diagnoses_by_state": {k: len(v) for k, v in diagnoses_by_state.items()},
        "recommendations_by_state": {k: len(v) for k, v in recs_by_state.items()},
        "common_issues": sorted(issue_counts.items(), key=lambda x: -x[1])[:10],
        "recent_diagnoses": diagnoses[:10],
        "recent_recommendations": recommendations[:10],
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "gemini_configured": model is not None})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
