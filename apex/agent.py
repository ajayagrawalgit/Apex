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
        "You are Apex, a helpful AI assistant. Your goal is to evaluate the safety of a website and present your findings in a human-readable, conversational format. "
        "1) First, call `scrape_with_docker(url)` to get the website content. Store its result as `scraped_output`. "
        "2) Next, call `analyze_agent(scraped=scraped_output, url=url)` to perform an initial analysis. Store its result as `analysis_output`. "
        "3) If `analysis_output.raw_data.unsafe` is 0 (meaning safe), proceed to call `deep_check_agent(scraped=scraped_output, url=url, prior=analysis_output)` for a more thorough safety check. Store its result as `deep_check_output`. "
        "4) After all checks are complete, provide a comprehensive summary in natural language. Start with the summary from scraping: `scraped_output.human_summary`. Then add the analysis summary: `analysis_output.human_summary`. If a deep check was performed, add its summary: `deep_check_output.human_summary`. "
        "Finally, based on `analysis_output.raw_data.unsafe` and `deep_check_output.raw_data.unsafe` (if deep check was performed), state the overall safety verdict clearly and explain the reasons, insights, and any indicators found. Your response should be easy for a human to understand and act upon."
    ),
    tools=[
        scrape_with_docker,
        analyze_agent,
        deep_check_agent
    ],
    # Removed 'agents' parameter as it is not supported in this format.
)
