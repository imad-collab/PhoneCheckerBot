import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from .env
load_dotenv()

# Fetch Twilio credentials
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)

def lookup_number(number):
    try:
        phone_number = client.lookups.v1.phone_numbers(number).fetch(type=["carrier"])
        print("✅ Number lookup successful!")
        print("E164 Format:", phone_number.phone_number)
        print("Country:", phone_number.country_code)
        print("Carrier:", phone_number.carrier.get("name"))
        print("Type:", phone_number.carrier.get("type"))
    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    test_number = "+61428567890"  # replace with a real verified number
    print("🚀 Running Twilio test on:", test_number)   # <-- added debug
    lookup_number(test_number)
