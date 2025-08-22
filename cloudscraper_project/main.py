from scraper import scrape_url

def main():
    print("Welcome to the Ultimate URL Scraper!")
    url = input("Enter the URL to scrape: ")
    content = scrape_url(url)
    print("\nScraped Content:\n")
    print(content)

if __name__ == "__main__":
    main()
