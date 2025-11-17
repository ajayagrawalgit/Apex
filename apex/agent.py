from google.adk.agents.llm_agent import Agent
from google.adk.agents import Agent, Tool
from tools.scraper import apex_scraper

scrape_tool = Tool(
    name="scrape_with_cloudscraper",
    description="Scrape the HTML content of a URL using Cloudscraper, bypassing basic anti-bot screens.",
    fn=apex_scraper,
    input_schema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL of the website to scrape"},
            "timeout": {"type": "integer", "default": 10},
        },
        "required": ["url"],
    },
)


tools = [
    scrape_tool,
]


root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='You are "Apex". Your ',
    tools=tools,
)
