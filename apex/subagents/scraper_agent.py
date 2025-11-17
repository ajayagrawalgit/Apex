from google.adk.agents import Agent
from apex.utils.docker_spinner import run_scraper_in_container

def scrape_with_docker(url: str, timeout: int = 10) -> dict:
    raw_result = run_scraper_in_container(url=url, timeout=timeout)
    if "content" in raw_result and isinstance(raw_result["content"], str):
        raw_result["content"] = raw_result["content"][:5000] # Truncate content here

    human_summary = f"Scraping of {url} completed. Status: {raw_result.get("status", "unknown")} (HTTP {raw_result.get("status_code", "N/A")}). Content preview length: {len(raw_result.get("content", ""))} characters."
    print(f"[Scraper Agent] {human_summary}")
    return raw_result

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
