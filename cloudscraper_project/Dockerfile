
            FROM python:3.9-slim
            WORKDIR /app
            COPY . /app
            RUN pip install cloudscraper
            CMD ["python", "-u", "-c", "from scraper import scrape_url; import sys; print(scrape_url(sys.stdin.read().strip()))"]
            