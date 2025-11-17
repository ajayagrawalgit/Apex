from google.adk.agents import Agent
# from google.adk.tools import FunctionTool
from apex.subagents.scraper_agent import scraper_agent, scrape_with_docker
from apex.subagents.analyzer_agent import analyzer_agent_def, analyze_agent
from apex.subagents.deepcheck_agent import deepcheck_agent, deep_check_agent

root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="Root agent that orchestrates sub-agents to scrape, analyze, and deep-check website safety.",
    instruction=(
        "You are Apex. To evaluate a website: "
        "1) First, call `scrape_with_docker(url)` to get the website content. Store this as `scraped_result`. "
        "2) Next, call `analyze_agent(scraped=scraped_result, url=url)` to analyze the scraped content. Store this as `analysis_result`. "
        "3) If and only if `analysis_result.unsafe` is 0 (meaning safe), then call `deep_check_agent(scraped=scraped_result, url=url, prior=analysis_result)` for a deeper safety check. Store this as `deep_check_result`. "
        "4) Finally, determine the overall safety: if either `analysis_result.unsafe` is 1 or if `deep_check_result.unsafe` is 1 (if deep check was performed), mark the site as unsafe (unsafe=1). Otherwise, mark it as safe (unsafe=0). "
        "Return a final JSON response with the following keys: `unsafe` (0 or 1), `verdict`, `reasons`, `insights`, `indicators`, `url`, `content_preview` from `analysis_result`, and `deep_check` (if `deep_check_result` exists)."
    ),
    tools=[
        scrape_with_docker,
        analyze_agent,
        deep_check_agent
    ],
    # Removed 'agents' parameter as it is not supported in this format.
)
