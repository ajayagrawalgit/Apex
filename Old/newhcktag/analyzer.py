#!/usr/bin/env python3
"""
Google ADK-based Malware Analyzer
Analyzes scraped content to detect malicious URLs and content
"""

import os
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

TASK_ID = os.getenv("TASK_ID", "")
INPUT_PATH = os.getenv("INPUT_PATH", "/data")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OUTPUT_PATH = INPUT_PATH

# Risk scoring thresholds
MALICIOUS_THRESHOLD = 0.6
SUSPICIOUS_THRESHOLD = 0.4

# ============================================================================
# MALWARE DETECTION FUNCTIONS
# ============================================================================

def score_ssl_security(metadata: Dict[str, Any]) -> float:
    """Score SSL/TLS security (0-1, higher is safer)."""
    ssl_info = metadata.get("ssl_info", {})
    is_https = ssl_info.get("is_https", False)
    
    return 1.0 if is_https else 0.0

def score_security_headers(metadata: Dict[str, Any]) -> float:
    """Score presence of security headers (0-1, higher is safer)."""
    headers = metadata.get("status_headers", {})
    
    security_score = 0.0
    total_headers = 0
    
    security_header_checks = [
        ("x_frame_options", 0.2),
        ("x_content_type_options", 0.2),
        ("content_security_policy", 0.3),
    ]
    
    for header_name, weight in security_header_checks:
        total_headers += weight
        if headers.get(header_name):
            security_score += weight
    
    # Penalize excessive cookies
    if headers.get("set_cookie"):
        security_score -= 0.1
    
    return max(0.0, min(1.0, security_score / total_headers if total_headers > 0 else 0.5))

def score_suspicious_patterns(metadata: Dict[str, Any]) -> float:
    """Score suspicious JavaScript patterns (0-1, higher is more suspicious)."""
    patterns = metadata.get("suspicious_patterns", {})
    
    dangerous_patterns = [
        "has_eval",
        "has_obfuscated_code",
        "has_suspicious_redirect",
        "has_popup"
    ]
    
    suspicious_count = sum(1 for p in dangerous_patterns if patterns.get(p, False))
    
    # More suspicious patterns = higher risk
    return min(1.0, suspicious_count * 0.25)

def score_external_resources(metadata: Dict[str, Any]) -> float:
    """Score external resources (0-1, higher is more risky)."""
    scripts = metadata.get("scripts", [])
    iframes = metadata.get("iframes", [])
    external_links = metadata.get("links", [])
    
    external_scripts = sum(1 for s in scripts if s.get("src"))
    sandboxed_iframes = sum(1 for i in iframes if i.get("sandboxed"))
    unsafe_iframes = len(iframes) - sandboxed_iframes
    external_count = sum(1 for l in external_links if l.get("is_external"))
    
    # Risk increases with external resources
    risk = 0.0
    if external_scripts > 5:
        risk += 0.2
    if unsafe_iframes > 0:
        risk += 0.3
    if external_count > 10:
        risk += 0.2
    
    return min(1.0, risk)

def score_content_metadata(metadata: Dict[str, Any]) -> float:
    """Score content metadata for suspicious characteristics (0-1)."""
    risk = 0.0
    
    # Suspicious content types
    content_type = metadata.get("status_headers", {}).get("content_type", "").lower()
    if "javascript" in content_type and "text/html" not in content_type:
        risk += 0.15
    
    # Unusually large content
    content_length = metadata.get("content_length", 0)
    if content_length > 5 * 1024 * 1024:  # > 5MB
        risk += 0.1
    
    # Missing meta tags (less legitimate sites have them)
    meta_tags = metadata.get("meta_tags", {})
    if len(meta_tags) < 3:
        risk += 0.05
    
    return min(1.0, risk)

def score_forms_and_inputs(metadata: Dict[str, Any]) -> float:
    """Score forms and input elements for phishing indicators (0-1)."""
    forms = metadata.get("forms", [])
    
    risk = 0.0
    
    for form in forms:
        action = form.get("action", "").lower()
        
        # Suspicious form targets
        if action and ("bit.ly" in action or "tinyurl" in action or not action.startswith("http")):
            risk += 0.15
        
        # Suspicious methods
        if form.get("method", "").upper() == "GET":
            risk += 0.05
    
    # Too many forms might indicate phishing
    if len(forms) > 5:
        risk += 0.1
    
    return min(1.0, risk)

async def analyze_with_adk(metadata: Dict[str, Any], html_preview: str) -> Dict[str, Any]:
    """
    Use Google ADK agent for intelligent analysis.
    
    In production, this would use the actual ADK framework:
    from google.adk.agents import Agent
    from google.adk.models.lite_llm import LiteLlm
    
    For now, we implement a structured decision engine.
    """
    logger.info("Analyzing with ADK agent logic")
    
    # Collect all security signals
    security_score = score_ssl_security(metadata)
    header_score = score_security_headers(metadata)
    pattern_score = score_suspicious_patterns(metadata)
    resource_score = score_external_resources(metadata)
    metadata_score = score_content_metadata(metadata)
    form_score = score_forms_and_inputs(metadata)
    
    # Calculate composite risk (0-1, higher = more risky)
    # Weight suspicious factors more heavily than protective factors
    risk_score = (
        (1 - security_score) * 0.2 +
        (1 - header_score) * 0.15 +
        pattern_score * 0.25 +
        resource_score * 0.20 +
        metadata_score * 0.10 +
        form_score * 0.10
    )
    
    # Classification
    if risk_score >= MALICIOUS_THRESHOLD:
        classification = "malicious"
        confidence = min(0.99, risk_score)
    elif risk_score >= SUSPICIOUS_THRESHOLD:
        classification = "suspicious"
        confidence = risk_score
    else:
        classification = "benign"
        confidence = 1 - risk_score
    
    analysis_result = {
        "classification": classification,
        "risk_score": round(risk_score, 3),
        "confidence": round(confidence, 3),
        "component_scores": {
            "ssl_security": round(security_score, 3),
            "security_headers": round(header_score, 3),
            "suspicious_patterns": round(pattern_score, 3),
            "external_resources": round(resource_score, 3),
            "content_metadata": round(metadata_score, 3),
            "form_indicators": round(form_score, 3),
        },
        "indicators": {
            "uses_https": metadata.get("ssl_info", {}).get("is_https", False),
            "has_security_headers": score_security_headers(metadata) > 0.5,
            "has_suspicious_patterns": pattern_score > 0.3,
            "has_external_scripts": len(metadata.get("scripts", [])) > 0,
            "has_unsafe_iframes": any(not i.get("sandboxed") for i in metadata.get("iframes", [])),
            "has_forms": len(metadata.get("forms", [])) > 0,
            "has_external_links": any(l.get("is_external") for l in metadata.get("links", [])),
        },
        "recommendations": generate_recommendations(classification, metadata),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return analysis_result

def generate_recommendations(classification: str, metadata: Dict[str, Any]) -> list:
    """Generate security recommendations based on classification."""
    recommendations = []
    
    if classification == "malicious":
        recommendations = [
            "Block this URL immediately",
            "Report to security team",
            "Check for any downloads from this site",
            "Scan system for malware"
        ]
    elif classification == "suspicious":
        recommendations = [
            "Use caution when visiting this site",
            "Do not enter personal information",
            "Consider using a VPN",
            "Monitor browser behavior"
        ]
    else:
        recommendations = ["Site appears safe to visit"]
    
    # Add specific recommendations based on metadata
    if not metadata.get("ssl_info", {}).get("is_https"):
        recommendations.append("WARNING: Site does not use HTTPS")
    
    if any(metadata.get("suspicious_patterns", {}).values()):
        recommendations.append("Site contains suspicious JavaScript")
    
    if any(not i.get("sandboxed") for i in metadata.get("iframes", [])):
        recommendations.append("Site has unsandboxed embedded content")
    
    return recommendations

async def load_scraped_data(task_id: str) -> Optional[Dict[str, Any]]:
    """Load scraped data from shared volume."""
    try:
        scrape_file = Path(INPUT_PATH) / f"scraped_{task_id}.json"
        
        if not scrape_file.exists():
            logger.error(f"Scrape file not found: {scrape_file}")
            return None
        
        logger.info(f"Loading scrape data from: {scrape_file}")
        
        with open(scrape_file, 'r') as f:
            data = json.load(f)
        
        return data
        
    except Exception as e:
        logger.error(f"Error loading scraped data: {e}")
        return None

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main analyzer entry point."""
    if not TASK_ID:
        logger.error("TASK_ID not provided")
        sys.exit(1)
    
    logger.info(f"Task ID: {TASK_ID}")
    logger.info(f"Input Path: {INPUT_PATH}")
    
    # Load scraped data
    scrape_data = await load_scraped_data(TASK_ID)
    
    if not scrape_data:
        logger.error("Failed to load scraped data")
        sys.exit(1)
    
    if scrape_data.get("status") != "success":
        logger.error(f"Scrape was not successful: {scrape_data.get('error')}")
        sys.exit(1)
    
    # Extract metadata and HTML preview
    metadata = scrape_data.get("metadata", {})
    html_preview = scrape_data.get("html_preview", "")
    
    logger.info("Starting ADK-based analysis")
    
    # Analyze
    analysis_result = await analyze_with_adk(metadata, html_preview)
    
    # Prepare final output
    output = {
        "task_id": TASK_ID,
        "url": metadata.get("url", ""),
        "analysis": analysis_result,
        "scrape_metadata": {
            "domain": metadata.get("domain", ""),
            "content_length": metadata.get("content_length", 0),
            "timestamp": metadata.get("timestamp", "")
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Save result
    output_file = Path(OUTPUT_PATH) / f"result_{TASK_ID}.json"
    
    try:
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Analysis result saved to: {output_file}")
        logger.info(f"Classification: {analysis_result['classification']}")
        logger.info(f"Risk Score: {analysis_result['risk_score']}")
        logger.info(f"Confidence: {analysis_result['confidence']}")
        
        # Print result for debugging
        print(json.dumps(output, indent=2))
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Failed to save result: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
