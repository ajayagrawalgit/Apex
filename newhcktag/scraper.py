#!/usr/bin/env python3
"""
Optimized Web Scraper for Malware Detection Pipeline
Runs in minimal Docker container, scrapes URL and saves data
"""

import os
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

TARGET_URL = os.getenv("TARGET_URL", "")
TASK_ID = os.getenv("TASK_ID", "")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "/data")
REQUEST_TIMEOUT = 20
MAX_CONTENT_SIZE = 10 * 1024 * 1024  # 10 MB limit

# ============================================================================
# SCRAPER FUNCTIONS
# ============================================================================

def calculate_hash(data: str) -> str:
    """Calculate SHA256 hash of content."""
    return hashlib.sha256(data.encode()).hexdigest()

def extract_metadata(url: str, html: str, headers: dict) -> Dict[str, Any]:
    """Extract security-relevant metadata from response."""
    soup = BeautifulSoup(html, 'lxml')
    
    metadata = {
        "url": url,
        "domain": url.split('/')[2] if '://' in url else url,
        "timestamp": datetime.utcnow().isoformat(),
        "content_hash": calculate_hash(html),
        "content_length": len(html),
        "status_headers": {
            "content_type": headers.get('content-type', ''),
            "server": headers.get('server', ''),
            "x_frame_options": headers.get('x-frame-options', ''),
            "x_content_type_options": headers.get('x-content-type-options', ''),
            "content_security_policy": headers.get('content-security-policy', ''),
            "set_cookie": bool(headers.get('set-cookie')),
        },
        "ssl_info": extract_ssl_info(url),
        "scripts": extract_scripts(soup),
        "links": extract_links(soup, url),
        "forms": extract_forms(soup),
        "iframes": extract_iframes(soup),
        "meta_tags": extract_meta_tags(soup),
        "suspicious_patterns": detect_suspicious_patterns(html)
    }
    
    return metadata

def extract_ssl_info(url: str) -> Dict[str, Any]:
    """Extract SSL/TLS information."""
    return {
        "is_https": url.startswith('https://'),
        "protocol": "https" if url.startswith('https://') else "http"
    }

def extract_scripts(soup: BeautifulSoup) -> list:
    """Extract script tags and sources."""
    scripts = []
    for script in soup.find_all('script', limit=10):
        scripts.append({
            "src": script.get('src', ''),
            "inline": bool(script.string),
            "type": script.get('type', 'text/javascript'),
            "async": script.get('async', False),
            "defer": script.get('defer', False)
        })
    return scripts

def extract_links(soup: BeautifulSoup, base_url: str) -> list:
    """Extract external links."""
    links = []
    base_domain = base_url.split('/')[2]
    
    for link in soup.find_all('a', limit=20):
        href = link.get('href', '')
        if href and href.startswith('http'):
            domain = href.split('/')[2]
            links.append({
                "url": href,
                "is_external": domain != base_domain,
                "text": link.get_text()[:50]  # First 50 chars
            })
    return links

def extract_forms(soup: BeautifulSoup) -> list:
    """Extract form data."""
    forms = []
    for form in soup.find_all('form', limit=10):
        forms.append({
            "action": form.get('action', ''),
            "method": form.get('method', 'GET'),
            "inputs": len(form.find_all('input'))
        })
    return forms

def extract_iframes(soup: BeautifulSoup) -> list:
    """Extract iframe sources."""
    iframes = []
    for iframe in soup.find_all('iframe', limit=10):
        iframes.append({
            "src": iframe.get('src', ''),
            "sandboxed": bool(iframe.get('sandbox'))
        })
    return iframes

def extract_meta_tags(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract meta tags."""
    meta = {}
    for tag in soup.find_all('meta'):
        if tag.get('name'):
            meta[tag.get('name')] = tag.get('content', '')
        elif tag.get('property'):
            meta[tag.get('property')] = tag.get('content', '')
    return meta

def detect_suspicious_patterns(html: str) -> Dict[str, bool]:
    """Detect suspicious patterns in HTML."""
    html_lower = html.lower()
    
    return {
        "has_eval": "eval(" in html_lower,
        "has_document_write": "document.write" in html_lower,
        "has_obfuscated_code": "String.fromCharCode" in html_lower,
        "has_suspicious_redirect": "window.location" in html_lower or "location.href" in html_lower,
        "has_form_redirect": any(x in html_lower for x in ["<form", "submit"]),
        "has_popup": "window.open" in html_lower or "alert(" in html_lower,
        "has_plugin_object": "<embed" in html_lower or "<object" in html_lower,
    }

async def scrape_url(url: str) -> Optional[Dict[str, Any]]:
    """Scrape URL and extract relevant data."""
    try:
        logger.info(f"Starting scrape for: {url}")
        
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            response = await client.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            response.raise_for_status()
            
            html = response.text
            
            # Check content size
            if len(html) > MAX_CONTENT_SIZE:
                logger.warning(f"Content exceeds size limit: {len(html)} bytes")
                html = html[:MAX_CONTENT_SIZE]
            
            logger.info(f"Successfully scraped {url}")
            logger.info(f"Response status: {response.status_code}, Size: {len(html)} bytes")
            
            metadata = extract_metadata(url, html, dict(response.headers))
            
            return {
                "status": "success",
                "metadata": metadata,
                "html_preview": html[:1000],  # First 1000 chars for analysis
                "full_html": html  # Full content for detailed analysis
            }
            
    except httpx.TimeoutException:
        logger.error(f"Timeout while scraping: {url}")
        return {"status": "error", "error": "timeout"}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code} for {url}")
        return {"status": "error", "error": f"http_error_{e.response.status_code}"}
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        return {"status": "error", "error": "request_error"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"status": "error", "error": str(e)}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main scraper entry point."""
    if not TARGET_URL:
        logger.error("TARGET_URL not provided")
        sys.exit(1)
    
    if not TASK_ID:
        logger.error("TASK_ID not provided")
        sys.exit(1)
    
    # Create output directory if needed
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    
    logger.info(f"Task ID: {TASK_ID}")
    logger.info(f"Target URL: {TARGET_URL}")
    logger.info(f"Output Path: {OUTPUT_PATH}")
    
    # Scrape the URL
    result = await scrape_url(TARGET_URL)
    
    if result is None:
        logger.error("Scraping failed")
        sys.exit(1)
    
    # Save result to shared volume
    output_file = os.path.join(OUTPUT_PATH, f"scraped_{TASK_ID}.json")
    
    try:
        with open(output_file, 'w') as f:
            # Don't include full HTML in JSON for space efficiency
            safe_result = result.copy()
            safe_result.pop('full_html', None)
            json.dump(safe_result, f, indent=2)
        
        logger.info(f"Scrape result saved to: {output_file}")
        
        # Also save raw HTML separately if successful
        if result["status"] == "success":
            html_file = os.path.join(OUTPUT_PATH, f"content_{TASK_ID}.html")
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(result["full_html"])
            logger.info(f"HTML content saved to: {html_file}")
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Failed to save result: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
