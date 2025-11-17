from google.adk.agents import Agent
from apex.utils.docker_spinner import run_scraper_in_container

def scrape_with_docker(url: str, timeout: int = 10) -> dict:
    print(f"[Scraper Agent] Scraping URL: {url}")
    result = run_scraper_in_container(url=url, timeout=timeout)
    if "content" in result and isinstance(result["content"], str):
        result["content"] = result["content"][:5000] # Truncate content here
    return result

# scraper_tool = FunctionTool(func=run_scraper_in_container)

scraper_agent = Agent(
    model="gemini-2.5-flash",
    name="scraper_agent",
    description="Sub-agent that only scrapes a URL inside an isolated Docker container.",
    instruction=(
        "You only perform scraping. Call scrape_with_docker(url, timeout) and return its JSON response."
    ),
    tools=[scrape_with_docker],
)
