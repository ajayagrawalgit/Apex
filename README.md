# Apex: Your AI-Powered Guardian Against Malicious Websites

![Language](https://img.shields.io/badge/Python-3.11%2B-blue)
![Framework](https://img.shields.io/badge/Framework-Google_ADK-orange)
![AI Model](https://img.shields.io/badge/AI_Model-Gemini_2.5_Flash-purple)
![Deployment](https://img.shields.io/badge/Deployment-Docker-blue.svg)
![Tech](https://img.shields.io/badge/Tech-FastAPI-009688)

Meet Apex — a lightweight, AI-assisted website safety checker. Paste a URL, and Apex fetches the page, flags common phishing/scam patterns, and explains the verdict in clear, human-friendly language. It’s fast for everyday checks and deep enough for power users, with a multi‑agent pipeline coordinating scraping, analysis, and deeper safety inspection.

## 📖 Table of Contents

* [What is Apex?](#-what-is-apex)
* [Why Do We Need This?](#-why-do-we-need-this)
* [How Does Apex Work?](#-how-does-apex-work)
* [Real-World Use Cases](#-real-world-use-cases)
* [What Makes Apex Special?](#-what-makes-apex-special)
* [Who Can Use Apex?](#-who-can-use-apex)
* [Part 2: For Technical Readers - Deep Dive](#-part-2-for-technical-readers---deep-dive)
    * [Architecture Overview](#-architecture-overview)
    * [Technical Stack](#-technical-stack)
    * [Core Components](#-core-components)
    * [Root Agent Orchestration](#-root-agent-orchestration)
    * [API Architecture](#-api-architecture)
    * [Real-World Implementation Examples](#-real-world-implementation-examples)
    * [Performance, Security, & Extensibility](#-performance-security--extensibility)
    * [Limitations and Future Enhancements](#-limitations-and-future-enhancements)
    * [Conclusion](#-conclusion)
* [Getting Started](#-getting-started)
    * [For Users](#-for-users)
    * [For Developers](#-for-developers)
    * [Repository Structure](#-repository-structure)

---

## 💡 What is Apex?

Imagine you're about to click on a link someone sent you. Maybe it's in an email, a text message, or a social media post. You're not sure if it's safe. That's where Apex comes in.

Apex is like having a cybersecurity expert who instantly checks any website for you before you visit it. It's an AI-powered tool that analyzes websites and tells you whether they're safe or potentially dangerous.

## ❓ Why Do We Need This?

Every day, millions of people fall victim to online scams, phishing attacks, and malicious websites. These sites might:
* Steal your passwords and personal information
* Trick you into giving away your cryptocurrency wallet keys
* Install malware on your device
* Impersonate legitimate companies (like fake LinkedIn, PayPal, or bank websites)

Apex helps protect you from these threats by automatically detecting warning signs that humans might miss.

## ⚙️ How Does Apex Work?

Think of Apex as having three specialized assistants working together:

1.  **The Scraper 🕷️**
    This assistant visits the website and collects all the information it can find—like reading a book to understand what it's about.

2.  **The Analyzer 🔍**
    This assistant looks for obvious red flags:
    * Does the website ask for sensitive information like passwords or wallet keys?
    * Does it promise unrealistic things like "double your money" or "free cryptocurrency"?
    * Does the domain name look suspicious (like `linked1n.com` instead of `linkedin.com`)?
    * Can the website even be reached, or does it fail to load?

3.  **The Deep Checker 🧠**
    If the first check says a site might be safe, this assistant does a deeper investigation:
    * Does the website mention a well-known brand (like MetaMask or Coinbase) but use a different domain name?
    * Does it contain hidden code that might steal your data?
    * Are there suspicious links to known dangerous websites?

4.  **The AI Coordinator 🤖**
    Finally, an AI (powered by Google's Gemini) puts all this information together and explains it to you in plain English, like a security expert would.

## 🌎 Real-World Use Cases

### Use Case 1: The Suspicious Email Link
* **Scenario:** You receive an email claiming to be from your bank, asking you to "verify your account" by clicking a link.
* **How Apex Helps:**
    * You paste the URL into Apex.
    * It analyzes the website and discovers:
        * The domain doesn't match your bank's official website.
        * The page asks for sensitive information.
        * It contains phishing patterns.
* **Result:** Apex warns you: "UNSAFE—This appears to be a phishing attempt. Do not enter any personal information."

### Use Case 2: The Crypto Airdrop Scam
* **Scenario:** Someone on social media tells you about a "free cryptocurrency airdrop" and sends you a link.
* **How Apex Helps:**
    * Apex checks the website and finds:
        * Multiple mentions of "free crypto" and "airdrop" (common scam indicators).
        * The site asks you to "connect your wallet".
        * The domain cannot be resolved (doesn't exist).
* **Result:** Apex immediately flags it as malicious and explains why.

### Use Case 3: The Typosquatting Attack
* **Scenario:** You see a link to `www.linked1n.com` (note the "1" instead of "i").
* **How Apex Helps:**
    * Apex attempts to access the site.
    * The domain cannot be resolved (it's a fake domain).
    * Even if it could load, Apex would detect the brand mismatch.
* **Result:** Apex marks it as UNSAFE and explains: "Domain could not be resolved. This often indicates a non-existent or malicious domain."

## ✨ What Makes Apex Special?

1.  **Human-Readable Explanations:** Instead of technical jargon, Apex explains threats in plain language anyone can understand.
2.  **Multi-Layer Protection:** It doesn't just check one thing—it performs multiple checks to catch sophisticated attacks.
3.  **AI-Powered Intelligence:** Uses Google's advanced Gemini AI to understand context and provide nuanced analysis.
4.  **Fast and Automated:** Get results in seconds, not hours.

## 👥 Who Can Use Apex?

* **Individuals:** Check suspicious links before clicking.
* **Businesses:** Protect employees from phishing attacks.
* **Security Teams:** Quickly analyze potential threats.
* **Developers:** Integrate website safety checks into applications.

---

## 👨‍💻 Part 2: For Technical Readers - Deep Dive

### Introduction
**Apex** is a sophisticated malicious URL analyzer built on Google's Agent Development Kit (ADK), leveraging multi-agent orchestration, pattern matching, and AI-powered analysis to provide comprehensive website safety assessments.

### 🏗️ Architecture Overview

Apex follows a **multi-agent orchestration pattern** where a root agent coordinates specialized sub-agents, each responsible for a specific aspect of the analysis pipeline.

```

┌─────────────────┐
│ Root Agent │ (Gemini 2.5 Flash)
│ (Orchestrator)│
└────────┬────────┘
│
┌────┴────┬──────────────┬──────────────┐
│ │ │ │
┌───▼───┐ ┌──▼────┐ ┌────▼─────┐ ┌────▼──────┐
│Scraper│ │Analyzer│ │Deep Check│ │AI Summary│
│ Agent │ │ Agent │ │ Agent │ │ Generator│
└───────┘ └────────┘ └──────────┘ └──────────┘

````

### 🛠️ Technical Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | Google ADK | Multi-agent orchestration |
| **AI Model** | Gemini 2.5 Flash | Coordination & summarization |
| **Web Framework**| FastAPI | API serving & web interface |
| **Scraping** | Cloudscraper | Bypassing Cloudflare |
| **Language** | Python 3.11+ | Core logic |
| **Deployment** | Docker | Containerization |

### 🧩 Core Components

#### 1. Scraper Agent (`scrape_website`)
**Purpose:** Fetches website content while handling various edge cases.

**Implementation Details:**
```python
def scrape_website(url: str, timeout: int = 10) -> dict:
 scraper = cloudscraper.create_scraper()
 try:
  response = scraper.get(url, timeout=timeout)
  response.raise_for_status()
  content = response.text[:5000] # Truncate for efficiency
  return {
  "status": "success",
  "status_code": response.status_code,
  "content": content,
  }
 except requests.exceptions.ConnectionError:
  # Domain resolution failure
  return {"status": "error", "error": "Domain resolution failed."}
 except cloudscraper.exceptions.CloudflareChallengeError:
  # Cloudflare protection detected
  return {"status": "error", "error": "Cloudflare challenge."}
````

  * **Cloudflare Bypass:** Uses `cloudscraper` to handle anti-bot protection.
  * **Error Handling:** Distinguishes between DNS failures, HTTP errors, and Cloudflare challenges.
  * **Content Truncation:** Limits content to 5000 characters for performance.

#### 2\. Analyzer Agent (`analyze_agent`)

**Purpose:** Performs initial safety assessment using pattern matching and heuristics.

**Detection Mechanisms:**

```python
# Pattern-Based Detection
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

# URL Analysis
URL_RED_FLAGS = [
 r"\.(ru|cn|tk|pw|top|xyz)(/|$)", # Suspicious TLDs
 r"--", # Punycode-like patterns
]
```

**Scoring Algorithm:**

```python
score = 0
for r in reasons:
 if r.startswith("content_match"):
  score += 2 # Content matches are weighted higher
 else:
  score += 1

verdict = "benign"
if score >= 4:
 verdict = "malicious"
elif score >= 2:
 verdict = "suspicious"
```

**Output Structure:**

```python
{
 "unsafe": 0 | 1,
 "verdict": "benign" | "suspicious" | "malicious",
 "reasons": List[str],
 "insights": List[str],
 "indicators": { ... }
}
```

#### 3\. Deep Check Agent (`deep_check_agent`)

**Purpose:** Performs advanced analysis on sites that pass initial screening.

**Advanced Detection Techniques:**

  * **Form Field Analysis:**
    ```python
    if re.search(r"<input[^>]*(seed|mnemonic|private\s*key|recovery)[^>]*>", lc):
     reasons.append("form_sensitive_fields")
    ```
  * **JavaScript Obfuscation Detection:**
    ```python
    if re.search(r"atob\(|eval\(|fromCharCode\(|unescape\(", lc):
     reasons.append("obfuscated_js_patterns")
    ```
  * **Data Exfiltration Detection:**
    ```python
    if re.search(r"fetch\(https?://|xhr|navigator\.sendbeacon", lc):
     reasons.append("network_exfil_calls")
    ```
  * **Brand Mismatch Detection:**
    ```python
    known_brands = ["binance", "metamask", "trust wallet", "coinbase", "okx", "phantom"]
    mentions = [b for b in known_brands if b in content.lower()]
    for brand in mentions:
     if brand.replace(" ", "") not in domain:
      reasons.append(f"brand_mismatch:{brand}")
    ```
  * **Suspicious TLD Link Analysis:**
    ```python
    bad_tlds = (".ru", ".cn", ".tk", ".pw", ".top", ".xyz")
    ext_links = re.findall(r"https?://[^\'\"\s\<\>]+", content)
    bad_links = [l for l in ext_links if any(
     l.lower().endswith(t) or f"{t}/" in l.lower()
     for t in bad_tlds
    )]
    if len(bad_links) >= 2:
     reasons.append("multiple_bad_tld_links")
    ```

### 🤖 Root Agent Orchestration

**Agent Definition:**

```python
from google.adk.agents import SequentialAgent
from apex.sub_agents.scraper_agent import scraper_agent
from apex.sub_agents.web_check_agent import web_check_agent
from apex.sub_agents.deep_analysis_agent import deep_analysis_agent

root_agent = SequentialAgent(
    name="root_agent",
    description="Agent that orchestrates sub-agents to scrape, analyze, and deep-check website safety.",
    sub_agents=[scraper_agent, web_check_agent, deep_analysis_agent],
)
```

**Workflow:**

1.  **Scraping Phase:** Root agent calls `scrape_website(url)`.
2.  **Initial Analysis:** Calls `analyze_agent(scraped, url)`.
3.  **Conditional Deep Check:** If initial analysis is safe (`unsafe == 0`), triggers `deep_check_agent`.
4.  **Synthesis:** AI generates a human-readable summary combining all findings.

### 📡 API Architecture

**FastAPI Server:**

```python
from google.adk.cli.fast_api import get_fast_api_app

app = get_fast_api_app(
 agents_dir=AGENT_DIR,
 web=True # Enables ADK web interface
)
```

**Endpoints:**

  * `GET /`: Service information
  * `GET /health`: Health check
  * `POST /run_sse`: Execute agent (Server-Sent Events)
  * `GET /docs`: Interactive API documentation

**Deployment (Dockerfile):**

```dockerfile
FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Environment Variables:**

  * `GOOGLE_API_KEY`: Google AI API key
  * `GOOGLE_CLOUD_PROJECT`: GCP project ID (optional)
  * `GOOGLE_CLOUD_LOCATION`: GCP location (optional)

### 📊 Real-World Implementation Examples

#### Example 1: Domain Resolution Failure Detection

  * **Input:** `https://www.linked1n.com`
  * **Processing:**
    1.  Scraper attempts connection → `ConnectionError`
    2.  Analyzer detects `domain_resolution_failed`
    3.  Verdict: **UNSAFE**
  * **Output:**
    ```json
    {
     "unsafe": 1,
     "verdict": "malicious",
     "reasons": ["domain_resolution_failed", "HTTP fetch failed"],
     "insights": ["Domain could not be resolved. This often indicates a non-existent or malicious domain."]
    }
    ```

#### Example 2: Phishing Site Detection

  * **Input:** `https://verify-paypal-security.tk`
  * **Processing:**
    1.  Scraper successfully fetches content.
    2.  Analyzer detects:
          * Suspicious TLD (`.tk`)
          * Content match: "verify your account"
          * Content match: "urgent action required"
    3.  Score: 4+ → Verdict: **MALICIOUS**
  * **Output:**
    ```json
    {
     "unsafe": 1,
     "verdict": "malicious",
     "reasons": [
      "url_match:\\.(ru|cn|tk|pw|top|xyz)(/|$)",
      "content_match:verify your (wallet|account)",
      "content_match:urgent (action|required)"
     ],
     "insights": ["Contains login prompts; check for phishing cues."]
    }
    ```

#### Example 3: Crypto Scam Detection

  * **Input:** `https://free-crypto-airdrop.xyz`
  * **Processing:**
    1.  Scraper fetches content.
    2.  Analyzer detects:
          * Suspicious TLD (`.xyz`)
          * Content match: "airdrop", "free crypto", "connect wallet"
    3.  Deep check detects:
          * Form fields requesting seed phrases.
          * Brand mismatch (mentions MetaMask but domain doesn't match).
    4.  Verdict: **MALICIOUS**

### ⚡ Performance, Security, & Extensibility

  * **Performance:**
    1.  **Content Truncation:** Limits scraped content to 5000 characters.
    2.  **Conditional Deep Check:** Only performs expensive deep analysis on initially "safe" sites.
    3.  **Timeout Management:** 10-second timeout prevents hanging.
  * **Security:**
    1.  **Input Validation:** URL parsing and validation.
    2.  **Error Handling:** Comprehensive exception handling prevents information leakage.
    3.  **API Key Protection:** Uses environment variables.
  * **Extensibility:**
    1.  **Custom Patterns:** Easily add new regex to `BAD_PATTERNS`.
    2.  **New Agents:** Create new agent functions and add them to the root agent's tools.
    3.  **Integration:** Use the FastAPI as a REST API for other systems.

### ✅ Conclusion

Apex demonstrates how modern AI agent frameworks can be leveraged to build practical security tools. By combining rule-based detection, heuristics, and AI-powered analysis, it provides a comprehensive solution for website safety assessment.

**Key Takeaways:**

  * Multi-agent orchestration enables specialized, focused analysis.
  * Pattern matching + AI provides robust detection capabilities.
  * Human-readable output bridges the gap between technical analysis and user understanding.

-----

## 🚀 Getting Started

### ⚡ Quick Start

1. Set your API key in `.env`:
   
   ```env
   GOOGLE_API_KEY="your-google-api-key"
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run locally:

   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8080 --reload
   ```

4. Open the dev UI / docs:
   - http://localhost:8080/dev-ui
   - http://localhost:8080/docs

### 👤 For Users

1.  Deploy Apex using Docker or a cloud platform.
2.  Access the web interface.
3.  Enter URLs to analyze.
4.  Review safety verdicts and insights.

### 🧑‍💻 For Developers

1.  Clone the repository:
    ```bash
    git clone https://github.com/ajayagrawalgit/Apex/
    cd apex
    ```
2.  Set up environment variables (create a `.env` file):
    ```.env
    GOOGLE_API_KEY="your-google-api-key"
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run locally (with auto-reload):
    ```bash
    uvicorn server:app --reload
    ```
5.  Access at `http://localhost:8080` (API docs at `http://localhost:8080/docs`).

### _🗂️ Repository Structure

```
apex/
├── apex/
│ ├── __init__.py
│ ├── apex.py       # Root agent definition
│ └── tools.py      # Agent tools (scraper, analyzer, deep_check)
├── server.py       # FastAPI application
├── requirements.txt  # Python dependencies
├── Dockerfile      # Container configuration
└── .env            # Environment variables (not in repo)
```

-----

*Apex: Protecting the web, one URL at a time.* 🛡️

---

## 🧯 Troubleshooting

- **Cloud Run: "Docker is not installed or not in PATH"**
  - Cloud Run does not support Docker-in-Docker. Scraping runs in-process using `cloudscraper`.

- **Function-calling errors (parameter parsing)**
  - Use simple types (str/int/bool/float). Avoid Optional/Union in tool function signatures.
  - This repo provides wrappers: `analyze_scraped_text`, `deep_safety_check_text`.

- **Cloudflare challenge errors**
  - Some sites are aggressively protected. Consider increasing timeout or adding retries.
  - You may augment headers or consider proxying (respect ToS).

## 🧪 Technicalities

- **Stack**
  - Python 3.11+
  - Google ADK (multi‑agent framework)
  - Gemini 2.5 Flash/Pro
  - FastAPI + Uvicorn
  - cloudscraper, requests

- **Agents**
  - Root coordinator: orchestrates sub‑agents
  - Scraper: `scrape_website(url)`
  - Analyzer: `analyze_scraped_text(content, url="")`
  - Deep check: `deep_safety_check_text(content, url, prior_json="")`

- **Data model**
  - Analyzer/Deep outputs: `{ unsafe: 0|1, verdict, reasons[], insights[], indicators? }`
  - Scraper output: `{ status, status_code, content }` (content truncated to 5000 chars)

- **API & Deployment**
  - FastAPI app (see [API Architecture](#-api-architecture))
  - Dockerized; deployable to Cloud Run (no Docker‑in‑Docker)
  - Env: `GOOGLE_API_KEY` required

- **Constraints**
  - Cloud Run disallows running `docker` inside the container; scraper runs in‑process
  - Tool schemas simplified for automatic function calling (string params, no unions)

- **Deep dive**
  - Architecture: [Overview](#-architecture-overview)
  - Components: [Core](#-core-components), [Root Orchestration](#-root-agent-orchestration)
  - Patterns: [Bad patterns](#-core-components), [URL red flags](#-core-components)
  - Examples: [Real‑world](#-real-world-implementation-examples)