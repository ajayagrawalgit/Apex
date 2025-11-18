import re
from typing import Dict, List, Any, Optional
import cloudscraper
from urllib.parse import urlparse
import json
import requests
import os

# From agents/apex/tools/analyzer.py
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


def analyze_scraped_data(scrape_result: Dict[str, Any], url: str = "") -> Dict[str, Any]:
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
    if scrape_result.get("error") == "Domain resolution failed.":
        reasons.append("domain_resolution_failed")

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

# Wrapper for easier automatic function calling from LLM (string content input)
def analyze_scraped_text(content: str, url: str = "") -> Dict[str, Any]:
    scrape_result: Dict[str, Any] = {
        "status": "success",
        "status_code": 200,
        "content": content or "",
    }
    return analyze_scraped_data(scrape_result=scrape_result, url=url)

# From agents/apex/tools/deep_analyzer.py
def deep_safety_check(
    scraped: Dict[str, Any],
    url: str,
    prior: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
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
    ext_links = re.findall(r"https?://[^\'\"\s\<\>]+", content)
    bad_links = [l for l in ext_links if any([l.lower().endswith(t) or f"{t}/" in l.lower() for t in bad_tlds])]
    if len(bad_links) >= 2:
        reasons.append("multiple_bad_tld_links")
    # 6) Login prompts on non-brand domain
    if ("login" in lc or "sign in" in lc) and not any(b.replace(" ", "") in domain for b in mentions):
        insights.append("Login prompts present; ensure domain is official.")
    unsafe = 1 if reasons else 0
    ai_opinion = (
        "Additional checks found red flags; consider unsafe." if unsafe else
        "No additional red flags found; appears safe"
    )
    return {
        "unsafe": unsafe,
        "ai_opinion": ai_opinion,
        "reasons": reasons,
        "insights": insights,
    }

# Wrapper for easier automatic function calling from LLM (string content input)
def deep_safety_check_text(content: str, url: str, prior_json: str = "") -> Dict[str, Any]:
    try:
        prior: Optional[Dict[str, Any]] = json.loads(prior_json) if prior_json else None
    except Exception:
        prior = None
    scraped = {
        "status": "success",
        "status_code": 200,
        "content": content or "",
    }
    return deep_safety_check(scraped=scraped, url=url, prior=prior)

# From agents/apex/subagents/scraper_agent.py
def scrape_website(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Scrapes a website using cloudscraper and returns the content.
    """
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        content = (response.text or "")[:5000]
        status = "success"
        status_code = response.status_code
        human_summary = (
            f"Scraping of {url} completed. Status: {status} (HTTP {status_code}). Content preview length: {len(content)} characters."
        )
        print(f"[Scraper Agent] {human_summary}")
        return {
            "status": status,
            "status_code": status_code,
            "content": content,
        }
    except cloudscraper.exceptions.CloudflareChallengeError as e:
        error_message = f"Failed to scrape {url} due to Cloudflare challenge. Error: {e}"
        print(f"[Scraper Agent] {error_message}")
        return {
            "status": "error",
            "error": error_message,
        }
    except requests.exceptions.ConnectionError as e:
        error_message = f"Failed to scrape {url} due to domain resolution failure. Error: {e}"
        print(f"[Scraper Agent] {error_message}")
        return {
            "status": "error",
            "error": error_message,
        }
    except Exception as e:
        error_message = f"Failed to scrape {url}. Error: {e}"
        print(f"[Scraper Agent] {error_message}")
        return {
            "status": "error",
            "error": error_message,
        }

# From agents/apex/subagents/analyzer_agent.py
def analyze_agent(scraped: Dict[str, Any], url: str) -> Dict[str, Any]:
    print(f"[Analyzer Agent] Analyzing URL: {url}")
    analysis_result = analyze_scraped_data(scrape_result=scraped, url=url)
    unsafe_flag = analysis_result.get("unsafe", 1)
    content_preview = scraped.get("content", "")[:1000]

    verdict_text = "safe" if unsafe_flag == 0 else "unsafe"
    human_summary = f"Analysis for {url} completed. Verdict: {verdict_text.upper()}. Reasons: {', '.join(analysis_result.get('reasons', []))}. Insights: {', '.join(analysis_result.get('insights', []))}. Content preview: {content_preview}"
    if "domain_resolution_failed" in analysis_result.get("reasons", []):
        human_summary = f"Analysis for {url} completed. Verdict: UNSAFE. Reason: Domain could not be resolved. This often indicates a non-existent or malicious domain. Insights: {', '.join(analysis_result.get('insights', []))}."
    print(f"[Analyzer Agent] {human_summary}")
    return analysis_result

# From agents/apex/subagents/deepcheck_agent.py
def deep_check_agent(scraped: Dict[str, Any], url: str, prior: Dict[str, Any]) -> Dict[str, Any]:
    print(f"[DeepCheck Agent] Performing deep check for URL: {url}")
    deep_check_result = deep_safety_check(scraped=scraped, url=url, prior=prior)

    unsafe_flag = deep_check_result.get("unsafe", 1)
    verdict_text = "safe" if unsafe_flag == 0 else "unsafe"
    human_summary = f"Deep check for {url} completed. Verdict: {verdict_text.upper()}. Reasons: {', '.join(deep_check_result.get('reasons', []))}. Insights: {', '.join(deep_check_result.get('insights', []))} ."
    if "domain_resolution_failed" in deep_check_result.get("reasons", []):
        human_summary = f"Deep check for {url} completed. Verdict: UNSAFE. Reason: Domain could not be resolved. This often indicates a non-existent or malicious domain. Insights: {', '.join(deep_check_result.get('insights', []))}."
    print(f"[DeepCheck Agent] {human_summary}")
    return deep_check_result
