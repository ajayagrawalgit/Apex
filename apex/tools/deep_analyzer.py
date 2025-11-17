import re
import json
from typing import Dict, List
from urllib.parse import urlparse


def deep_safety_check(scraped: Dict, url: str, prior: Dict | None = None) -> Dict:
    """
    Sub-agent: performs a deeper safety check on content judged safe by primary analyzer.
    It looks for additional red flags such as:
      - Suspicious forms asking sensitive info
      - Obfuscated JavaScript patterns
      - Mixed content / data exfil hints
      - Domain mismatch with brand names
      - Excessive external links to shady TLDs
    Returns:
      {
        unsafe: 0|1,
        ai_opinion: str,
        reasons: [str],
        insights: [str],
      }
    """
    content = scraped.get("content", "") or ""
    lc = content.lower()
    parsed = urlparse(url or "")
    domain = parsed.netloc.lower()
    reasons: List[str] = []
    insights: List[str] = []
    # 1) Forms asking for seed/private keys
    if re.search(r"<input[^>]*(seed|mnemonic|private\s*key|recovery)[^>]*>", lc):
        reasons.append("form_sensitive_fields")
    # 2) Obfuscated JS (basic heuristic)
    if re.search(r"atob\(|eval\(|fromCharCode\(|unescape\(", lc):
        reasons.append("obfuscated_js_patterns")
    # 3) Data exfil endpoints
    if re.search(r"fetch\(https?://|xhr|navigator\.sendbeacon", lc):
        reasons.append("network_exfil_calls")
    # 4) Brand vs domain mismatch (very rough)
    known_brands = ["binance", "metamask", "trust wallet", "coinbase", "okx", "phantom"]
    mentions = [b for b in known_brands if b in lc]
    for b in mentions:
        if b.replace(" ", "") not in domain:
            reasons.append(f"brand_mismatch:{b}")
    # 5) Suspicious outbound links TLDs
    bad_tlds = (".ru", ".cn", ".tk", ".pw", ".top", ".xyz")
    ext_links = re.findall(r"https?://[^'\"\s<>]+", content)
    bad_links = [l for l in ext_links if any(l.lower().endswith(t) or f"{t}/" in l.lower() for t in bad_tlds)]
    if len(bad_links) >= 2:
        reasons.append("multiple_bad_tld_links")
    # 6) Login prompts on non-brand domain
    if ("login" in lc or "sign in" in lc) and not any(b.replace(" ", "") in domain for b in mentions):
        insights.append("Login prompts present; ensure domain is official.")
    unsafe = 1 if reasons else 0
    ai_opinion = (
        "Additional checks found red flags; consider unsafe." if unsafe else
        "No additional red flags found; appears safe, but remain cautious."
    )
    return {
        "unsafe": unsafe,
        "ai_opinion": ai_opinion,
        "reasons": reasons,
        "insights": insights,
    }
