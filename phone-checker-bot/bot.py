# --- Force IPv4 for httpx globally ---
import httpx

# Monkey-patch httpx to always use IPv4
orig_init = httpx.AsyncClient.__init__

def ipv4_init(self, *args, **kwargs):
    kwargs["transport"] = httpx.AsyncHTTPTransport(local_address="0.0.0.0")
    return orig_init(self, *args, **kwargs)

httpx.AsyncClient.__init__ = ipv4_init


# --- Normal imports ---
import os
import json
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Our services
from services.twilio_service import lookup_number
from services.ddg_service import scam_search
from services.gpt_service import analyze_number
from services.history_service import save_lookup, get_history


# Load .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# Load safe numbers JSON
SAFE_FILE = "services/safe_numbers.json"
if os.path.exists(SAFE_FILE):
    with open(SAFE_FILE, "r") as f:
        SAFE_NUMBERS = json.load(f)
else:
    SAFE_NUMBERS = {}


# /start command
async def start(update, context):
    await update.message.reply_text(
        "👋 Hello! Send me a phone number in E.164 format (e.g. +61412345678). "
        "I’ll check if it’s spam or safe."
    )


# /history command
async def history(update, context):
    history_data = get_history()
    if not history_data:
        await update.message.reply_text("📂 No history yet.")
        return

    reply_lines = ["📂 Last 5 Lookups:\n"]
    for h in history_data[-5:]:
        reply_lines.append(
            f"📞 {h['number']}\n"
            f"🌍 {h['country']}\n"
            f"📡 {h['carrier']}\n"
            f"🚦 Status: {h['spam_status']}\n"
            f"⚖️ Risk Score: {h['risk_score']}\n"
        )

    await update.message.reply_text("\n".join(reply_lines))


# Handle phone number lookup
async def check_number(update, context):
    number = update.message.text.strip()

    await update.message.reply_text(f"🔍 Checking number: {number} ...")

    # Step 0: Check safelist
    if number in SAFE_NUMBERS:
        safe_info = SAFE_NUMBERS[number]
        result = {
            "number": number,
            "country": "AU",
            "carrier": "Safe",
            "spam_status": "✅ Safe",
            "risk_score": "Low"
        }
        save_lookup(result)
        await update.message.reply_text(
            f"✅ SAFE NUMBER\n"
            f"📞 Number: {number}\n"
            f"ℹ️ Info: {safe_info}"
        )
        return

    # Step 1: Twilio lookup
    result = lookup_number(number)
    if isinstance(result, tuple) and len(result) == 2:
        carrier, country = result
    else:
        carrier, country = "Unknown", "Unknown"

    # Step 2: DuckDuckGo scam search (ensure list)
    ddg_results = scam_search(number)
    if not isinstance(ddg_results, list):
        ddg_results = [str(ddg_results)]

    # Step 3: AI analysis
    decision = analyze_number(number, carrier, country, ddg_results)

    # Save history
    save_lookup(decision)

    # Step 4: Pretty reply
    pretty_output = (
        f"📞 Number: {decision['number']}\n"
        f"🌍 Country: {decision['country']}\n"
        f"📡 Carrier: {decision['carrier']}\n"
        f"🚦 Status: {decision['spam_status']}\n"
        f"⚖️ Risk Score: {decision['risk_score']}"
    )
    await update.message.reply_text(pretty_output)


def main():
    # Init bot
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_number))

    print("🚀 Bot is running... Press CTRL+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
