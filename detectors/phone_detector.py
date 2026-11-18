import re

PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{7,}\d")


def analyze_phones(text):
    numbers = []
    for match in PHONE_RE.findall(text or ""):
        digits = re.sub(r"\D", "", match)
        if 8 <= len(digits) <= 15:
            numbers.append(digits)

    score, reasons = 0, []
    for digits in numbers:
        if len(digits) >= 8 and len(set(digits)) <= 2:
            score += 20
            reasons.append("Phone number has repeated digits and may be fake")
        if digits.startswith(("1900", "911900")):
            score += 25
            reasons.append("Premium-rate style number that can charge high fees")

    return {"score": min(score, 100), "reasons": list(dict.fromkeys(reasons)), "numbers": numbers}
