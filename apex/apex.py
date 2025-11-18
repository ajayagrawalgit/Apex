from google.adk.agents import Agent, SequentialAgent
from .tools import scrape_website, analyze_agent, deep_check_agent
from .sub_agents.deep_analysis_agent import deep_analysis_agent
from .sub_agents.scraper_agent import scraper_agent
from .sub_agents.web_check_agent import web_check_agent

root_agent = SequentialAgent(
    name="root_agent",
    description="Agent that orchestrates sub-agents to scrape, analyze, and deep-check website safety.",
    sub_agents=[scraper_agent, web_check_agent, deep_analysis_agent],
)
