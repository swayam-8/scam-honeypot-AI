import re
from typing import Dict, List

def extract_intelligence(text: str) -> Dict[str, List[str]]:
    """
    Extracts sensitive information from scammer messages.
    
    Detects:
    - UPI IDs
    - Phone Numbers
    - Phishing Links
    - Bank Account Numbers
    - Suspicious Keywords
    
    Args:
        text: The message to analyze
    
    Returns:
        Dictionary with extracted intelligence categorized by type
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
    
    # 1. UPI IDs (e.g., scammer@okhdfcbank, name@upi, etc.)
    # Patterns: username@bankname or username@upi
    upi_pattern = r"[\w\.\-_]{3,}@[\w\.]+(?:\(upi\)|\(UPI\))?"
    upi_matches = re.findall(upi_pattern, text, re.IGNORECASE)
    intel["upiIds"] = [match for match in upi_matches if "@" in match]

    # Additional UPI pattern: common UPI formats
    upi_providers = r"@(?:okhdfcbank|okaxis|okicici|okicici|upi|paytm|googlepay|phonepe|whatsapp)"
    upi_matches2 = re.findall(r"[\w\.]+"+upi_providers, text, re.IGNORECASE)
    intel["upiIds"].extend([m for m in upi_matches2 if m not in intel["upiIds"]])

    # 2. Phone Numbers 
    # Indian format: +91, 0, or direct 10-digit starting with 6-9
    phone_patterns = [
        r"\+91\s?[6-9]\d{9}",  # +91 format
        r"0\d{10}",             # 0 prefix
        r"[6-9]\d{9}",          # 10 digits starting with 6-9
        r"\(\d{3}\)\s?\d{3}\s?\d{4}",  # (XXX) XXX-XXXX format
    ]
    
    phone_numbers = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        phone_numbers.extend(matches)
    
    # Remove duplicates and clean
    intel["phoneNumbers"] = list(set([p.replace(" ", "").replace("(", "").replace(")", "") 
                                       for p in phone_numbers]))

    # 3. Phishing Links (http/https/www)
    link_patterns = [
        r"https?://[^\s\)\"\']+",
        r"www\.[^\s\)\"\']+",
    ]
    
    links = []
    for pattern in link_patterns:
        matches = re.findall(pattern, text)
        links.extend(matches)
    
    intel["phishingLinks"] = list(set(links))

    # 4. Bank Account Numbers (typically 9-18 digits)
    # More specific: often preceded by "account" or "a/c"
    account_patterns = [
        r"a/c\s*[:#]?\s*(\d{9,18})",
        r"account\s*[:#]?\s*(\d{9,18})",
        r"(?:account|a/c)\s*no\s*[:#]?\s*(\d{9,18})",
    ]
    
    bank_accounts = []
    for pattern in account_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        bank_accounts.extend(matches)
    
    # Also look for standalone 12-16 digit sequences (typical account lengths)
    if not bank_accounts:
        standalone_pattern = r"\b(\d{12,16})\b"
        matches = re.findall(standalone_pattern, text)
        bank_accounts.extend(matches)
    
    # Filter out numbers that are too short or phone number lookalikes
    intel["bankAccounts"] = [
        acc for acc in bank_accounts 
        if len(acc) >= 9 and not acc.isdigit()[:10]  # Not just 10 digits
    ]

    # 5. Suspicious Keywords (scam indicators)
    scam_keywords = [
        "urgent", "immediately", "verify", "block", "suspend", 
        "kyc", "expire", "expired", "pan", "aadhar", "aadhaar",
        "confirm", "confirm identity", "update", "validate",
        "suspicious activity", "unauthorized", "fraud",
        "link", "click here", "download", "install",
        "otp", "password", "pin", "atm", "debit card",
        "upi", "gpay", "paytm", "bank", "account",
        "limited time", "act now", "don't miss", "final notice"
    ]
    
    found_keywords = []
    for keyword in scam_keywords:
        if keyword in text.lower():
            found_keywords.append(keyword)
    
    intel["suspiciousKeywords"] = list(set(found_keywords))

    # Clean up empty lists
    return {k: list(set(filter(None, v))) for k, v in intel.items()}


def is_likely_scam(text: str, keywords_threshold: int = 2) -> bool:
    """
    Quick heuristic to assess if a message is likely a scam.
    
    Args:
        text: Message to analyze
        keywords_threshold: Minimum suspicious keywords to flag as scam
    
    Returns:
        True if likely a scam, False otherwise
    """
    intel = extract_intelligence(text)
    
    # Criteria:
    # 1. Contains suspicious keywords (2+)
    # 2. OR contains UPI/Phone/Bank/Link
    # 3. OR urgency language
    
    keyword_count = len(intel["suspiciousKeywords"])
    has_contact = (len(intel["phoneNumbers"]) > 0 or 
                   len(intel["upiIds"]) > 0 or
                   len(intel["bankAccounts"]) > 0)
    has_links = len(intel["phishingLinks"]) > 0
    
    return (keyword_count >= keywords_threshold or 
            has_contact or 
            has_links)