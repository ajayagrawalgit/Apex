import cloudscraper

def apex_scraper(url: str, timeout: int = 10) -> dict:
    """
    Scrapes the HTML content of the specified URL using Cloudscraper.
    Args:
        url: Target website URL
        timeout: Timeout in seconds for the request
    Returns:
        Dictionary with status, scraped content, and HTTP status code.
    """
    scraper = cloudscraper.create_scraper()
    try:
        resp = scraper.get(url, timeout=timeout)
        resp.raise_for_status()
        return {
            "status": "success",
            "status_code": resp.status_code,
            "content": resp.text  # No slicing, returns the entire HTML
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "content": ""
        }
