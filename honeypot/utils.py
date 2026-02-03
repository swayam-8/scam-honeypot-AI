import re
from typing import Dict, List

def extract_intelligence(text: str) -> Dict[str, List[str]]:
    """
    Scans text for sensitive patterns (The Spy Logic).
    """
    intel = {
        "bankAccounts": [],
        "upiIds": [],
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": []
    }

    # 1. UPI IDs (e.g., scammer@okhdfcbank)
    upi_pattern = r"[\w\.\-_]{3,}@[a-zA-Z]{3,}"
    intel["upiIds"] = re.findall(upi_pattern, text)

    # 2. Phone Numbers (Indian format focus: +91 or starting with 6-9)
    phone_pattern = r"(?:\+91[\-\s]?)?[6-9]\d{9}"
    intel["phoneNumbers"] = re.findall(phone_pattern, text)

    # 3. Phishing Links (http/https)
    link_pattern = r"https?://[^\s]+|www\.[^\s]+"
    intel["phishingLinks"] = re.findall(link_pattern, text)

    # 4. Bank Account Numbers (Generic 9-18 digits)
    bank_pattern = r"\b\d{9,18}\b"
    # Filter out phone numbers from bank accounts just in case
    raw_nums = re.findall(bank_pattern, text)
    intel["bankAccounts"] = [n for n in raw_nums if len(n) > 6 and n not in intel["phoneNumbers"]]

    # 5. Suspicious Keywords
    keywords = ["urgent", "verify", "block", "suspend", "kyc", "expire", "pan", "aadhar"]
    found_keywords = [word for word in keywords if word in text.lower()]
    intel["suspiciousKeywords"] = found_keywords

    return intel