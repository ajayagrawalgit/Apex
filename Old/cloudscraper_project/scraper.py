import cloudscraper

def scrape_url(url):
    """
    Scrapes the content of the given URL using cloudscraper.

    Args:
        url (str): The URL to scrape.

    Returns:
        str: The content of the URL.
    """
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"
