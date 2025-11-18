from google.adk.agents import Agent
# from google.adk.tools import FunctionTool
from .subagents.scraper_agent import scraper_agent, scrape_website
from .subagents.analyzer_agent import analyzer_agent_def, analyze_agent
from .subagents.deepcheck_agent import deepcheck_agent, deep_check_agent

root_agent = Agent(
    model="gemini-2.5-pro",
    name="root_agent",
    description="Root agent that orchestrates sub-agents to scrape, analyze, and deep-check website safety.",
    instruction=(
        "You are Apex, a helpful AI assistant. Your goal is to evaluate the safety of a website and present your findings in a human-readable, conversational format. "
        "1) First, call `scrape_website(url)` to get the website content. Store this as `scraped_result`. "
        "2) Next, call `analyze_agent(scraped=scraped_result, url=url)` to perform an initial analysis. Store this as `analysis_result`. "
        "3) If `analysis_result.unsafe` is 0 (meaning safe), proceed to call `deep_check_agent(scraped=scraped_result, url=url, prior=analysis_result)` for a more thorough safety check. Store this as `deep_check_result`. "
        "4) After all checks are complete, summarize the findings. Start by stating the URL analyzed. Then, based on `analysis_result.unsafe` and `deep_check_result.unsafe` (if deep check was performed), clearly state the overall safety verdict (safe/unsafe) and explain the reasons, insights, and any indicators found from both analysis results. Your response should be easy for a human to understand and act upon."
    ),
    tools=[
        scrape_website,
        analyze_agent,
        deep_check_agent
    ],
    # Removed 'agents' parameter as it is not supported in this format.
)
