import cloudscraper
from bs4 import BeautifulSoup

def scrape_url_to_html(url):
    """
    Scrapes all the data from the given URL and outputs it as HTML with href details.

    Args:
        url (str): The URL to scrape.

    Returns:
        str: The scraped HTML content with href details.
    """
    try:
        # Strip leading and trailing spaces from the URL
        url = url.strip()
        # Create a cloudscraper instance
        scraper = cloudscraper.create_scraper()
        # Send a GET request to the URL
        response = scraper.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract all href links
        for a_tag in soup.find_all('a', href=True):
            a_tag.insert_after(soup.new_string(f" [href: {a_tag['href']}]"))
        return soup.prettify()
    except Exception as e:
        return f"An error occurred while fetching the URL: {e}"