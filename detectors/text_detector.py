import os
import re

try:
    import joblib
except ImportError:
    joblib = None

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "text_model.joblib")

# keyword groups: (keywords, weight per hit, up to 2 hits counted)
RULES = {
    "urgency": (
        ["urgent", "immediately", "act now", "final notice", "last warning",
         "within 24 hours", "will be suspended", "expires today", "today only"], 12),
    "payment": (
        ["gift card", "bitcoin", "crypto", "wire transfer", "western union",
         "send money", "processing fee", "pay a fee", "upi", "advance fee"], 18),
    "credentials": (
        ["otp", "one time password", "password", "cvv", "pin number",
         "account number", "verify your account", "kyc", "login details"], 18),
    "impersonation": (
        ["bank", "income tax", "customs", "courier", "police", "government",
         "paypal", "amazon", "microsoft support", "your account"], 8),
    "prize": (
        ["you have won", "lottery", "lucky draw", "free gift",
         "claim your reward", "cashback"], 12),
    "threat": (
        ["arrest", "legal action", "warrant", "deactivated", "penalty"], 12),
}

LABELS = {
    "urgency": "Pressure to act fast",
    "payment": "Asks for money or an unusual payment method",
    "credentials": "Asks for passwords, OTPs or account details",
    "impersonation": "Claims to be a trusted organisation",
    "prize": "Prize or reward bait",
    "threat": "Threatens legal or account consequences",
}

_model = None
_model_loaded = False


def _load_model():
    global _model, _model_loaded
    if not _model_loaded:
        _model_loaded = True
        if joblib and os.path.exists(MODEL_PATH):
            _model = joblib.load(MODEL_PATH)
    return _model


def _rule_score(text):
    lowered = text.lower()
    score, reasons, categories = 0, [], []
    for name, (keywords, weight) in RULES.items():
        hits = [k for k in keywords if re.search(r"\b" + re.escape(k) + r"\b", lowered)]
        if hits:
            score += weight * min(len(hits), 2)
            categories.append(name)
            reasons.append(f'{LABELS[name]} (found "{hits[0]}")')
    return min(score, 100), reasons, categories


def analyze_text(text):
    if not text or not text.strip():
        return {"score": 0, "reasons": [], "categories": [], "ml_probability": None}

    rule_score, reasons, categories = _rule_score(text)
    score = rule_score
    ml_probability = None

    model = _load_model()
    if model is not None:
        ml_probability = float(model.predict_proba([text])[0][1])
        score = round(0.5 * rule_score + 0.5 * ml_probability * 100)
        if ml_probability >= 0.5:
            reasons.append(f"Text model rates the wording as scam-like ({ml_probability:.0%})")

    return {
        "score": min(score, 100),
        "reasons": reasons,
        "categories": categories,
        "ml_probability": ml_probability,
    }
