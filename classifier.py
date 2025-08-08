
import re
from typing import Literal

OWNER_HINTS = [
    r'@owner\.', r'\bowner\b', r'\bowner portal\b', r'\bstatement\b', r'\bpayout\b',
    r'\bmaintenance invoice\b', r'\blease\b'
]

def classify_sender(email_address: str, subject: str, body_text: str) -> Literal["owner", "guest", "unknown"]:
    text = f"{email_address} {subject} {body_text}".lower()
    if re.search(r'@professionalholidayhomes\.com\.au', text):
        return "owner"  # internal/owner comms route to humans
    for hint in OWNER_HINTS:
        if re.search(hint, text):
            return "owner"
    if re.search(r'\bbooking\b|\bcheck[- ]?in\b|\bcode\b|\bkeys?\b|\bwi[- ]?fi\b', text):
        return "guest"
    return "unknown"
