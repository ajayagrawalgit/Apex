from google.adk.agents import Agent
from apex.tools.analyzer import analyze_scraped_data

def analyze_agent(scraped: dict, url: str) -> dict:
    print(f"[Analyzer Agent] Analyzing URL: {url}")
    result = analyze_scraped_data(scrape_result=scraped, url=url)
    unsafe_flag = result.get("unsafe", 1)
    content = scraped.get("content", "")
    # Limit content echo to avoid huge payloads
    content_preview = content[:1000]
    return {
        "unsafe": int(unsafe_flag),
        "verdict": result.get("verdict", "unknown"),
        "reasons": result.get("reasons", []),
        "insights": result.get("insights", []),
        "indicators": result.get("indicators", {}),
        "url": url,
        "content_preview": content_preview,
    }

analyzer_agent_def = Agent(
    model="gemini-2.5-flash",
    name="analyzer_agent",
    description="Sub-agent that analyzes scraped data for safety and insights.",
    instruction=(
        "You only analyze. Call analyze_site_safety(scraped, url) and return the JSON with unsafe flag, verdict, reasons, insights, indicators."
    ),
    tools=[analyze_agent],
)
