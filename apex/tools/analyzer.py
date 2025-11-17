import re
from typing import Dict, List

BAD_PATTERNS = [
    r"seed phrase",
    r"private key",
    r"mnemonic",
    r"airdrop",
    r"free\s+(crypto|btc|eth)",
    r"double your (money|coins)",
    r"guaranteed profit",
    r"urgent (action|required)",
    r"verify your (wallet|account)",
    r"connect (your )?wallet",
    r"claim (reward|prize)",
]

URL_RED_FLAGS = [
    r"\.(ru|cn|tk|pw|top|xyz)(/|$)",
    r"--",  # punycode-like
]


def analyze_scraped_data(scrape_result: Dict, url: str = "") -> Dict:
    """
    Analyze scraped data to assess safety.
    Returns a dict with:
      - unsafe: 0 (safe) or 1 (unsafe)
      - verdict: benign|suspicious|malicious
      - reasons: list of matched signals
      - insights: list of helpful notes
      - indicators: dict of simple features
    """
    status = scrape_result.get("status")
    content = scrape_result.get("content", "") or ""
    status_code = scrape_result.get("status_code")

    reasons: List[str] = []
    indicators = {
        "status": status,
        "status_code": status_code,
        "content_length": len(content),
        "num_digits_in_url": sum(ch.isdigit() for ch in url),
        "has_punycode": "--" in url if url else False,
    }

    # HTTP status issues
    if status != "success":
        reasons.append("HTTP fetch failed")
    if isinstance(status_code, int) and status_code >= 400:
        reasons.append(f"HTTP status {status_code}")

    # Pattern checks
    lowered = content.lower()
    for pat in BAD_PATTERNS:
        if re.search(pat, lowered):
            reasons.append(f"content_match:{pat}")

    for pat in URL_RED_FLAGS:
        if re.search(pat, url.lower() if url else ""):
            reasons.append(f"url_match:{pat}")

    # Score and verdict
    score = 0
    for r in reasons:
        if r.startswith("content_match"):
            score += 2
        else:
            score += 1

    verdict = "benign"
    if score >= 4:
        verdict = "malicious"
    elif score >= 2:
        verdict = "suspicious"

    unsafe = 1 if verdict in ("malicious", "suspicious") else 0

    insights = []
    if len(content) < 200:
        insights.append("Very short content; could be a redirect or blocker page.")
    if "wallet" in lowered:
        insights.append("Mentions wallets; verify it is an official domain.")
    if "login" in lowered:
        insights.append("Contains login prompts; check for phishing cues.")

    return {
        "unsafe": unsafe,
        "verdict": verdict,
        "reasons": reasons,
        "insights": insights,
        "indicators": indicators,
    }
