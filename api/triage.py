# triage.py
import re
from typing import Optional, Tuple

# Define triage keyword sets
TRIAGE_KEYWORDS = {
    "emergency": [
        "chest pain", "shortness of breath", "unconscious", "bleeding heavily",
        "severe headache", "confusion", "no pulse", "not breathing",
        "seizure", "stroke", "can't breathe", "trauma", "severe burn",
    ],
    "urgent": [
        "fever", "moderate pain", "vomiting", "persistent cough",
        "dehydration", "abdominal pain", "infection", "painful urination",
    ],
}


def assess_message_urgency(user_message: str) -> Tuple[str, Optional[str]]:
    """
    Real-time triage classification for the latest patient message.
    Returns a tuple: (level, matched_keyword)
    """
    message_lower = user_message.lower()

    # Check emergency first (highest priority)
    for keyword in TRIAGE_KEYWORDS["emergency"]:
        if re.search(rf"\b{re.escape(keyword)}\b", message_lower):
            return "Emergency", keyword

    # Then urgent
    for keyword in TRIAGE_KEYWORDS["urgent"]:
        if re.search(rf"\b{re.escape(keyword)}\b", message_lower):
            return "Urgent", keyword

    # Otherwise routine
    return "Routine", None



    
