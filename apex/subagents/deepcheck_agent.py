from google.adk.agents import Agent
from apex.tools.deep_analyzer import deep_safety_check

def deep_check_agent(scraped: dict, url: str, prior: dict) -> dict:
    print(f"[DeepCheck Agent] Performing deep check for URL: {url}")
    raw_scraped_data = scraped.get("raw_data", {})
    raw_prior_data = prior.get("raw_data", {})
    deep_check_result = deep_safety_check(scraped=raw_scraped_data, url=url, prior=raw_prior_data)

    unsafe_flag = deep_check_result.get("unsafe", 1)
    verdict_text = "safe" if unsafe_flag == 0 else "unsafe"
    human_summary = f"Deep check for {url} completed. Verdict: {verdict_text.upper()}. Reasons: {', '.join(deep_check_result.get("reasons", []))}. Insights: {', '.join(deep_check_result.get("insights", []))}."
    print(f"[DeepCheck Agent] {human_summary}")
    return {"raw_data": deep_check_result, "human_summary": human_summary}

# deepcheck_tool = FunctionTool(func=deep_safety_check)

deepcheck_agent = Agent(
    model="gemini-2.5-flash",
    name="deepcheck_agent",
    description="Sub-agent that performs an additional deep safety check when initial analysis is safe.",
    instruction=(
        "You only run the deep check. Call deep_safety_check(scraped, url, prior) and return its JSON. Also, add your complete opinion on the website safety in the 'opinion' key. Everything should be human readable and concise. Format it well."
    ),
    tools=[deep_check_agent],
)
