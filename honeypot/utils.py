import re
from typing import Dict, List

def extract_intelligence(text: str) -> Dict[str, List[str]]:
    """
    Extract sensitive information from messages.
    
    Detects:
    - UPI IDs
    - Phone Numbers
    - Phishing Links
    - Bank Account Numbers
    - Suspicious Keywords
    """
    intel = {
        "bankAccounts": [],
        "upiIds": [],
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": []
    }
    
    if not text or not isinstance(text, str):
        return intel
    
    # 1. UPI IDs
    upi_pattern = r"[\w\.\-]+@[\w]+"
    upi_matches = re.findall(upi_pattern, text, re.IGNORECASE)
    intel["upiIds"] = [m for m in upi_matches if "@" in m and len(m) > 3][:10]
    
    # 2. Phone Numbers (Indian format)
    phone_patterns = [
        r"\+91\s?[6-9]\d{9}",
        r"[6-9]\d{9}",
        r"\b9\d{9}\b",
    ]
    
    phone_numbers = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        phone_numbers.extend(matches)
    
    intel["phoneNumbers"] = list(set(phone_numbers))[:10]
    
    # 3. Phishing Links
    link_pattern = r"https?://[^\s\)\"\']+|www\.[^\s\)\"\']+\.\w+"
    links = re.findall(link_pattern, text)
    intel["phishingLinks"] = list(set(links))[:10]
    
    # 4. Bank Account Numbers (9-18 digits)
    account_pattern = r"\b\d{9,18}\b"
    accounts = re.findall(account_pattern, text)
    intel["bankAccounts"] = [a for a in accounts if len(a) >= 9][:10]
    
    # 5. Suspicious Keywords
    scam_keywords = [
        "urgent", "verify", "confirm", "click", "update", "kyc",
        "upi", "bank", "account", "otp", "password", "pan",
        "expired", "suspend", "fraud", "download", "link"
    ]
    
    found_keywords = []
    text_lower = text.lower()
    for keyword in scam_keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    intel["suspiciousKeywords"] = list(set(found_keywords))
    
    return intel

def is_likely_scam(text: str) -> bool:
    """Quick heuristic to assess if message is likely a scam."""
    intel = extract_intelligence(text)
    
    keyword_count = len(intel["suspiciousKeywords"])
    has_contact = (len(intel["phoneNumbers"]) > 0 or 
                   len(intel["upiIds"]) > 0)
    has_links = len(intel["phishingLinks"]) > 0
    
    return keyword_count >= 2 or has_contact or has_links
