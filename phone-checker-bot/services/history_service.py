import json
import os
from datetime import datetime

LOOKUP_FILE = os.path.join(os.path.dirname(__file__), "lookups.json")

def save_lookup(data):
    """Save a lookup entry to lookups.json"""
    history = []
    if os.path.exists(LOOKUP_FILE):
        with open(LOOKUP_FILE, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []

    history.append(data)

    with open(LOOKUP_FILE, "w") as f:
        json.dump(history, f, indent=2)

def get_history(limit=5):
    """Get the last N lookups"""
    if not os.path.exists(LOOKUP_FILE):
        return []

    with open(LOOKUP_FILE, "r") as f:
        try:
            history = json.load(f)
        except json.JSONDecodeError:
            history = []

    return history[-limit:]
