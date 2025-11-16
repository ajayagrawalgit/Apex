from scraper import scrape_url
from docker_runner import run_scraper_in_docker

def main():
    print("Welcome to the Ultimate URL Scraper!")
    url = input("Enter the URL to scrape: ")
    # content = scrape_url(url)
    content = run_scraper_in_docker(url)
    print("\nScraped Content:\n")
    print(content)

if __name__ == "__main__":
    main()
