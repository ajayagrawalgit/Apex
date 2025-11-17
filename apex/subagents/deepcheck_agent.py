from google.adk.agents import Agent
from apex.tools.deep_analyzer import deep_safety_check

def deep_check_agent(scraped: dict, url: str, prior: dict) -> dict:
    print(f"[DeepCheck Agent] Performing deep check for URL: {url}")
    res = deep_safety_check(scraped=scraped, url=url, prior=prior)
    return res

# deepcheck_tool = FunctionTool(func=deep_safety_check)

deepcheck_agent = Agent(
    model="gemini-2.5-flash",
    name="deepcheck_agent",
    description="Sub-agent that performs an additional deep safety check when initial analysis is safe.",
    instruction=(
        "You only run the deep check. Call deep_safety_check(scraped, url, prior) and return its JSON."
    ),
    tools=[deep_check_agent],
)
