import cloudscraper
from google.adk.agents import Agent

def scrape_website(url: str, timeout: int = 10) -> dict:
    """
    Scrapes a website using cloudscraper and returns the content.
    """
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(url, timeout=timeout)
        response.raise_for_status()  # Raise an exception for bad status codes
        content = response.text
        status = "success"
        status_code = response.status_code
        # Truncate content to match the original implementation's behavior
        content = content[:5000]
        human_summary = f"Scraping of {url} completed. Status: {status} (HTTP {status_code}). Content preview length: {len(content)} characters."
        print(f"[Scraper Agent] {human_summary}")
        return {
            "status": status,
            "status_code": status_code,
            "content": content,
        }
    except Exception as e:
        error_message = f"Failed to scrape {url}. Error: {e}"
        print(f"[Scraper Agent] {error_message}")
        return {
            "status": "error",
            "error": error_message,
        }

scraper_agent = Agent(
    model="gemini-2.5-flash",
    name="scraper_agent",
    description="Sub-agent that scrapes a URL and returns its content.",
    instruction=(
        "You only perform scraping. Call scrape_website(url, timeout) and return its JSON response."
    ),
    tools=[scrape_website],
)
