from .text_detector import analyze_text
from .url_detector import analyze_urls
from .phone_detector import analyze_phones

NEXT_STEPS = {
    "HIGH": ("Do not click any links, reply, or send money. Block the sender and report "
             "it. If you already shared details, contact your bank or the provider right "
             "away using the number on their official website."),
    "MEDIUM": ("Be cautious. Verify the sender through the official website or app, not "
               "the contact details in this message."),
    "LOW": ("No strong scam signals were found, but never share OTPs or passwords, and "
            "check unexpected requests through official channels."),
}


def _level(score):
    if score >= 70:
        return "HIGH", "Likely scam"
    if score >= 40:
        return "MEDIUM", "Suspicious"
    return "LOW", "Low risk"


def analyze(text="", image_text=""):
    combined = "\n".join(part for part in [text, image_text] if part)

    text_result = analyze_text(combined)
    url_result = analyze_urls(combined)
    phone_result = analyze_phones(combined)

    signals = {
        "text": text_result["score"],
        "links": url_result["score"],
        "phone": phone_result["score"],
    }

    # Strongest signal sets the base score. Each extra independent signal adds a bonus,
    # because a message that is urgent AND has a suspicious link is more dangerous.
    base = max(signals.values())
    active = sum(1 for value in signals.values() if value >= 20)
    score = min(100, base + 10 * max(active - 1, 0))

    level, label = _level(score)
    reasons = text_result["reasons"] + url_result["reasons"] + phone_result["reasons"]
    if not reasons:
        reasons = ["No common scam signals were found"]

    return {
        "score": score,
        "level": level,
        "label": label,
        "reasons": reasons,
        "next_step": NEXT_STEPS[level],
        "signals": signals,
        "urls": url_result["urls"],
        "extracted_text": image_text,
    }
