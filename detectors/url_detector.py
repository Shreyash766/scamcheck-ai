import re
from urllib.parse import urlparse

URL_RE = re.compile(r"(?:https?://|www\.)[^\s<>\"']+", re.IGNORECASE)
IP_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
SUSPICIOUS_TLDS = {"xyz", "top", "tk", "ml", "ga", "cf", "gq", "zip", "mov",
                   "click", "link", "loan", "work", "country"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly",
              "rb.gy", "ow.ly"}
BAIT_WORDS = ["login", "verify", "secure", "account", "update", "confirm",
              "signin", "wallet", "refund", "support"]


def extract_urls(text):
    return URL_RE.findall(text or "")


def _score_url(url):
    full = url if url.lower().startswith("http") else "http://" + url
    parsed = urlparse(full)
    host = (parsed.hostname or "").lower()
    score, reasons = 0, []

    if parsed.scheme == "http":
        score += 10
        reasons.append("Link is not encrypted (http instead of https)")
    if IP_RE.match(host):
        score += 30
        reasons.append("Link uses a raw IP address instead of a domain name")
    if host in SHORTENERS:
        score += 20
        reasons.append("Link shortener hides the real destination")
    tld = host.rsplit(".", 1)[-1] if "." in host else ""
    if tld in SUSPICIOUS_TLDS:
        score += 20
        reasons.append(f"Domain ends in .{tld}, which is often used for scams")
    if "xn--" in host:
        score += 20
        reasons.append("Link uses look-alike characters to imitate a real site")
    if host.count(".") >= 4:
        score += 10
        reasons.append("Many subdomains, a common way to imitate a brand")
    if "@" in url:
        score += 25
        reasons.append("Link contains '@', which can hide the real website")
    if len(url) > 75:
        score += 8
        reasons.append("Unusually long web address")
    if host.count("-") >= 3:
        score += 10
        reasons.append("Domain has many hyphens")
    bait = [w for w in BAIT_WORDS if w in host or w in parsed.path.lower()]
    if bait:
        score += 15
        reasons.append(f'Uses words like "{bait[0]}" to look official')

    return min(score, 100), reasons


def analyze_urls(text):
    urls = extract_urls(text)
    if not urls:
        return {"score": 0, "reasons": [], "urls": []}

    best, reasons = 0, []
    for url in urls:
        score, url_reasons = _score_url(url)
        best = max(best, score)
        reasons.extend(url_reasons)
    return {"score": best, "reasons": list(dict.fromkeys(reasons)), "urls": urls}
