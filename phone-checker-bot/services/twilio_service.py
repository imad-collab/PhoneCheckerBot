def lookup_number(number: str):
    """
    Look up phone number details from Twilio.
    Returns (carrier, country).
    """
    try:
        # Ensure number is E.164 (remove spaces, add +61 if it starts with 0 and not already international)
        number = number.replace(" ", "")
        if number.startswith("0") and not number.startswith("+"):
            number = "+61" + number[1:]

        phone_number = client.lookups.v1.phone_numbers(number).fetch(type=["carrier"])
        carrier = phone_number.carrier.get("name", "Unknown") if phone_number.carrier else "Unknown"
        country = phone_number.country_code if phone_number.country_code else "Unknown"
        return carrier, country
    except Exception as e:
        print("❌ Twilio lookup error:", e)
        return "Unknown", "Unknown"
