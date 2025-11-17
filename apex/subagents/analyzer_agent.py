from google.adk.agents import Agent
from apex.tools.analyzer import analyze_scraped_data

def analyze_agent(scraped: dict, url: str) -> dict:
    print(f"[Analyzer Agent] Analyzing URL: {url}")
    raw_scraped_data = scraped.get("raw_data", {})
    analysis_result = analyze_scraped_data(scrape_result=raw_scraped_data, url=url)
    unsafe_flag = analysis_result.get("unsafe", 1)
    content_preview = raw_scraped_data.get("content", "")[:1000] # Use raw_scraped_data here

    verdict_text = "safe" if unsafe_flag == 0 else "unsafe"
    human_summary = f"Analysis for {url} completed. Verdict: {verdict_text.upper()}. Reasons: {', '.join(analysis_result.get("reasons", []))}. Insights: {', '.join(analysis_result.get("insights", []))}. Content preview: {content_preview}"
    print(f"[Analyzer Agent] {human_summary}")
    return {"raw_data": analysis_result, "human_summary": human_summary}

analyzer_agent_def = Agent(
    model="gemini-2.5-flash",
    name="analyzer_agent",
    description="Sub-agent that analyzes scraped data for safety and insights.",
    instruction=(
        "You only analyze. Call analyze_site_safety(scraped, url) and return the JSON with unsafe flag, verdict, reasons, insights, indicators. Also, add your complete opinion on the website safety in the 'opinion' key."
    ),
    tools=[analyze_agent],
)
