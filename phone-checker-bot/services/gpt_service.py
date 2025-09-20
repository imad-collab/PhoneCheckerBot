import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_number(number, carrier, country, ddg_results):
    try:
        text = " ".join(ddg_results).lower()
    except Exception:
        text = ""

    # Defaults
    spam_status = "✅ Safe"
    risk_score = "Low"

    # Strong scam indicators
    scam_keywords = ["scam", "fraud", "spam", "report", "block", "scamwatch"]
    if any(word in text for word in scam_keywords):
        spam_status = "⚠️ Scam Likely"
        risk_score = "High"
    elif not carrier or carrier.lower() in ["none", "unknown"]:
        spam_status = "⚠️ Unknown"
        risk_score = "Medium"

    return {
        "number": number or "Unknown",
        "country": country or "Unknown",
        "carrier": carrier or "Unknown",
        "line_type": "Mobile" if carrier not in ["Unknown", None] else "Unknown",
        "sim_user": "Unknown",  # Placeholder
        "spam_status": spam_status,
        "risk_score": risk_score
    }
