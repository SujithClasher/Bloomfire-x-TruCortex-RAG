"""
guard_llm.py — Regex-based PII guard.
Detects and masks PII in user inputs and LLM outputs.
No external LLM dependencies.
"""

import re

# ---------------------------------------------------------------------------
# Compiled patterns
# ---------------------------------------------------------------------------

# Indian PAN: 5 uppercase letters, 4 digits, 1 uppercase letter  (e.g. ABCDE1234F)
PAN_PATTERN = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')

# Indian Aadhaar: 12 consecutive digits, optionally space-separated in groups of 4
AADHAAR_PATTERN = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')

# Indian mobile: optional +91 prefix, then 10-digit number starting 6-9
PHONE_PATTERN = re.compile(r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b')

# Standard e-mail address
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scan_input(text: str) -> dict:
    """
    Scan *text* for PII and decide whether to block or mask.

    Returns a dict::

        {
            "blocked": bool,
            "reason":  str,          # human-readable explanation (empty string if not blocked)
            "masked_text": str,      # text safe to store / pass forward
        }
    """
    # --- Hard-block: PAN card number ---
    pan_matches = PAN_PATTERN.findall(text)
    if pan_matches:
        return {
            "blocked": True,
            "reason": (
                f"🚫 PII Detected: Query contains a PAN card number "
                f"({', '.join(pan_matches)}). Remove the PAN and try again."
            ),
            "masked_text": "",
        }

    # --- Hard-block: Aadhaar number (12-digit) ---
    # Aadhaar check: collapse spaces, ensure exactly 12 digits
    aadhaar_matches = AADHAAR_PATTERN.findall(text)
    for match in aadhaar_matches:
        digits = match.replace(" ", "")
        if len(digits) == 12:
            return {
                "blocked": True,
                "reason": (
                    "🚫 PII Detected: Query contains an Aadhaar number. "
                    "Remove the Aadhaar number and try again."
                ),
                "masked_text": "",
            }

    # --- Soft-mask: phone numbers and e-mail addresses (allow query through) ---
    masked = _mask_phones_and_emails(text)

    return {
        "blocked": False,
        "reason": "",
        "masked_text": masked,
    }


def mask_output(text: str) -> str:
    """
    Mask phone numbers and e-mail addresses in LLM-generated output
    before returning to the client.
    """
    return _mask_phones_and_emails(text)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _mask_phones_and_emails(text: str) -> str:
    """Replace phone numbers and e-mail addresses with redaction tokens."""
    # Mask phone numbers
    text = PHONE_PATTERN.sub("[PHONE_MASKED]", text)
    # Mask e-mail addresses
    text = EMAIL_PATTERN.sub("[EMAIL_MASKED]", text)
    return text
