from google.adk.agents import LlmAgent
from apex.tools import scrape_website

scraper_agent = LlmAgent(
    name="ScraperAgent",
    model="gemini-2.5-flash",
    instruction="""You are a Scraper Agent.
Your sole task is to scrape and return the requested website's content. Use only the user's prompt to determine the target URL.
Invoke the `scrape_website` tool to perform the scrape.
Respond only with the **full scraped content** in this format:
<complete page content here> Do **not** include any explanation, commentary, or additional text before or after the code block in your response.
""",
    description="Scrapes the website and returns the content.",
    tools=[scrape_website],
    output_key="scraped_content"
)