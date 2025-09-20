import json
import os

# File paths
VCF_FILE = "/Users/mohammed/phone-checker-bot/Contacts.vcf"
JSON_FILE = "/Users/mohammed/phone-checker-bot/services/safe_numbers.json"

def parse_vcf(vcf_path):
    contacts = {}
    with open(vcf_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    name = None
    number = None

    for line in lines:
        line = line.strip()
        if line.startswith("FN:"):
            name = line[3:].strip()
        elif line.startswith("TEL:") or "TEL;" in line:
            number = line.split(":")[-1].strip()
            if number and name:
                # Ensure E.164 format (+61… for AU)
                if not number.startswith("+"):
                    if number.startswith("0"):
                        number = "+61" + number[1:]
                contacts[number] = f"✅ SAFE – {name}"
                name, number = None, None
    return contacts

def main():
    if not os.path.exists(VCF_FILE):
        print(f"❌ VCF file not found: {VCF_FILE}")
        return

    new_contacts = parse_vcf(VCF_FILE)

    # Load existing JSON if it exists
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            try:
                safe_numbers = json.load(f)
            except json.JSONDecodeError:
                safe_numbers = {}
    else:
        safe_numbers = {}

    # Merge new contacts
    safe_numbers.update(new_contacts)

    # Save back
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(safe_numbers, f, indent=2, ensure_ascii=False)

    print(f"✅ Converted {len(new_contacts)} contacts and saved to {JSON_FILE}")

if __name__ == "__main__":
    main()

