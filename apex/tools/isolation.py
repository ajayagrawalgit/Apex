import sys
import json
from scraper import apex_scraper


def main():
    # Usage: python isolation.py <url> [timeout]
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "error": "missing url arg"}))
        return 0
    url = sys.argv[1]
    try:
        timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    except Exception:
        timeout = 10

    result = apex_scraper(url=url, timeout=timeout)
    # Always print a single JSON line to stdout
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
