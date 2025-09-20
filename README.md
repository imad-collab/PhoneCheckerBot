📞 PhoneCheckerBot
A Telegram bot that checks phone numbers for validity, carrier info, and scam risk using Twilio Lookup, DuckDuckGo live search, and AI-powered analysis.

🚀 Features
✅ Validate numbers in E.164 format
🌍 Detect country, carrier, and line type (Mobile, Landline, VoIP)
🔎 Search web (DuckDuckGo) for scam/spam reports
🤖 AI-powered decision engine with risk scoring
🗂️ Import personal contacts (VCF → JSON safelist)
💾 Store lookup history for quick reference
🔐 Safe number whitelist (customer support, personal contacts)

📦 Tech Stack
Python 3.11+
python-telegram-bot
Twilio Lookup API
httpx
 + BeautifulSoup4
OpenAI
 (LLM-based analysis)

⚙️ Installation
Clone this repo:
git clone https://github.com/YOUR_USERNAME/PhoneCheckerBot.git
cd PhoneCheckerBot


Create virtual environment:
python3 -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows


Install dependencies:
pip install -r requirements.txt

🔑 Setup
Copy .env.example → .env and add your keys:

TELEGRAM_BOT_TOKEN=your_telegram_token
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_auth_token
OPENAI_API_KEY=your_openai_api_key


Add your safelist numbers in services/safe_numbers.json:
{
  "+611300555123": "✅ SAFE – DHL Customer Service",
  "+611800123456": "✅ SAFE – NAB Bank Helpline",
  "+61426648942": "✅ SAFE – Your Personal Number"
}


(Optional) Convert your contacts VCF file:
python services/convert_vcf.py

▶️ Run the Bot
python bot.py

💬 Usage
In Telegram:
Send any phone number (must be E.164 format like +61426648942).

Bot replies with structured JSON output:

{
  "number": "+61426964413",
  "country_code": "+61",
  "region": "Australia",
  "carrier": "Optus",
  "line_type": "Mobile",
  "sim_user": "Unknown",
  "spam_status": "✅ Safe",
  "risk_score": "Low"
}

🗂️ Project Structure
phone-checker-bot/
├── bot.py                   # Main Telegram bot
├── services/
│   ├── twilio_service.py    # Twilio lookup
│   ├── ddg_service.py       # DuckDuckGo scraper
│   ├── gpt_service.py       # OpenAI risk analysis
│   ├── history_service.py   # Save & retrieve lookups
│   ├── convert_vcf.py       # Convert VCF contacts → JSON
│   ├── safe_numbers.json    # Whitelisted safe numbers
│   └── lookups.json         # History of lookups
├── requirements.txt
└── README.md

📌 Deployment
Local Run: Python environment (as above)
Docker: Build container and run
Cloud: Deploy on Oracle Cloud / AWS EC2 / Heroku / Railway

✨ Future Improvements
Web dashboard for number lookups
SMS/WhatsApp integration
Automatic scam database sync (e.g., Scamwatch API)
Improved carrier + SIM user detection

