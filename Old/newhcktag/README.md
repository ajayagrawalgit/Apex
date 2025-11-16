# Malicious URL Detection Pipeline

**Optimized Docker-based web scraping and malware analysis system using Google ADK agent framework.**

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Orchestrator Service                        │
│  (Python + Docker API Client)                                   │
└────────────┬──────────────────────────────────────────────────┐─┘
             │                                                  │
    ┌────────▼──────────┐                        ┌──────────────▼─────┐
    │  Scraper Container │                       │ Analyzer Container  │
    │  (Python:3.11-slim)│◄──────Shared Volume──►│ (Python:3.11-slim)  │
    │  - httpx           │     malware_detection │ - google-adk        │
    │  - BeautifulSoup   │      _volume          │ - Risk Scoring      │
    │  - lxml            │                       │ - ADK Agent Logic   │
    └────────────────────┘                       └─────────────────────┘
             │                                                  │
             └──────────────────────────┬─────────────────────┘
                                        │
                        ┌───────────────▼────────────────┐
                        │   Results (JSON)               │
                        │ - Classification (malicious/   │
                        │   suspicious/benign)           │
                        │ - Risk Score (0-1)             │
                        │ - Confidence                   │
                        │ - Security Indicators          │
                        └────────────────────────────────┘
```

## Features

✅ **Minimal Docker Images**
- Scraper: ~200MB (Python 3.11-slim + httpx + BeautifulSoup)
- Analyzer: ~250MB (Python 3.11-slim + google-adk)
- Fast container startup (<2s per container)

✅ **Efficient Inter-Container Communication**
- Shared named volumes for data transfer
- Custom Docker network for isolation
- JSON-based payload format

✅ **Advanced Security Analysis**
- SSL/TLS certificate validation
- Security headers inspection
- Suspicious JavaScript pattern detection
- Phishing form analysis
- External resource verification
- Risk scoring algorithm (0-1 scale)

✅ **Google ADK Integration**
- LLM-based decision making (Gemini 2.5)
- Multi-agent orchestration support
- Extensible tool ecosystem
- Production-ready framework

✅ **Automatic Cleanup**
- Self-destruct containers after execution
- Named volume persistence
- Resource leak prevention
- Comprehensive error handling

## Installation

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Google API Key (for Gemini ADK)

### Setup

```bash
# 1. Clone/setup project
mkdir malware-detection && cd malware-detection

# 2. Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Set environment variables
export GOOGLE_API_KEY="your_api_key_here"

# 5. Build Docker images
docker build -f Dockerfile.scraper -t malware-scraper:latest .
docker build -f Dockerfile.analyzer -t malware-analyzer:latest .
docker build -f Dockerfile.orchestrator -t malware-orchestrator:latest .
```

## Usage

### Option 1: Direct Python Script

```python
from malware_detector import analyze_url, analyze_multiple_urls

# Analyze single URL
result = analyze_url("https://suspicious-site.com")
print(result)

# Analyze multiple URLs
urls = [
    "https://example.com",
    "https://github.com",
    "https://suspicious-site.com"
]
results = analyze_multiple_urls(urls)

for result in results:
    print(f"URL: {result['url']}")
    print(f"Classification: {result['analysis']['classification']}")
    print(f"Risk Score: {result['analysis']['risk_score']}")
```

### Option 2: Docker Compose

```bash
# Set API key
export GOOGLE_API_KEY="your_key"

# Run orchestrator
docker-compose up

# Or use prebuilt orchestrator image
docker run -e GOOGLE_API_KEY="your_key" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  malware-orchestrator:latest
```

### Option 3: Command Line

```bash
python malware_detector.py
```

## Output Format

```json
{
  "task_id": "task_abc123_1731604800",
  "url": "https://example.com",
  "status": "success",
  "analysis": {
    "classification": "benign",
    "risk_score": 0.25,
    "confidence": 0.95,
    "component_scores": {
      "ssl_security": 1.0,
      "security_headers": 0.8,
      "suspicious_patterns": 0.0,
      "external_resources": 0.15,
      "content_metadata": 0.1,
      "form_indicators": 0.0
    },
    "indicators": {
      "uses_https": true,
      "has_security_headers": true,
      "has_suspicious_patterns": false,
      "has_external_scripts": false,
      "has_unsafe_iframes": false,
      "has_forms": false,
      "has_external_links": false
    },
    "recommendations": [
      "Site appears safe to visit"
    ]
  },
  "timestamp": "2024-11-14T18:14:00.123456"
}
```

## Performance Metrics

- **Scraper Container**: ~1-3 seconds per URL (including startup)
- **Analyzer Container**: ~0.5-1 second
- **Memory Usage**:
  - Scraper: ~150-200MB
  - Analyzer: ~180-220MB
  - Orchestrator: ~100-150MB
- **Throughput**: 10-15 URLs/minute (sequential)

## Security Scoring Algorithm

### Risk Components (weighted)

| Component | Weight | Description |
|-----------|--------|-------------|
| SSL/TLS (inverted) | 20% | HTTPS usage |
| Security Headers (inverted) | 15% | CSP, X-Frame-Options, etc. |
| Suspicious Patterns | 25% | eval(), obfuscation, redirects |
| External Resources | 20% | Scripts, iframes, links |
| Content Metadata | 10% | File size, content type |
| Form Indicators | 10% | Phishing form detection |

### Classification Thresholds

- **Benign**: Risk Score < 0.40
- **Suspicious**: 0.40 ≤ Risk Score < 0.60
- **Malicious**: Risk Score ≥ 0.60

## Configuration

### Environment Variables

```bash
DOCKER_HOST=unix:///var/run/docker.sock  # Docker socket
GOOGLE_API_KEY=your_api_key              # Gemini API key
TARGET_URL=https://example.com           # URL to analyze
TASK_ID=task_xyz                         # Task identifier
OUTPUT_PATH=/data                        # Output directory
REQUEST_TIMEOUT=30                       # HTTP timeout (seconds)
```

### Docker Network

- **Network Name**: `malware_detection_net`
- **Driver**: Bridge (isolated)
- **Auto-cleanup**: Yes

### Shared Volume

- **Name**: `malware_detection_volume`
- **Mount Point (Scraper)**: `/data`
- **Mount Point (Analyzer)**: `/data`
- **Persistence**: Survives container removal

## Production Deployment

### Kubernetes (Optional)

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: malware-detection-job
spec:
  template:
    spec:
      containers:
      - name: orchestrator
        image: malware-orchestrator:latest
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: google-api
      restartPolicy: Never
```

### Scaling

- **Parallel Analysis**: Run multiple orchestrator instances
- **Task Queue**: Integrate with Redis/RabbitMQ
- **Result Storage**: PostgreSQL/MongoDB backend
- **API Wrapper**: FastAPI/Flask REST endpoint

## Troubleshooting

### Container fails to start
```bash
# Check Docker daemon
docker ps

# Verify images exist
docker images | grep malware

# Check logs
docker logs <container_id>
```

### Volume permission issues
```bash
# Fix permissions
docker volume inspect malware_detection_volume
sudo chown -R 1000:1000 /var/lib/docker/volumes/malware_detection_volume/_data
```

### Network connectivity
```bash
# Verify network
docker network inspect malware_detection_net

# Test DNS resolution
docker run --rm --network malware_detection_net busybox ping scraper
```

### Memory leaks
```bash
# Monitor container stats
docker stats

# Check for zombie processes
docker ps -a | grep malware
```

## Advanced Features

### Custom Risk Scoring

Modify `analyzer.py` scoring functions:
```python
def score_ssl_security(metadata: Dict[str, Any]) -> float:
    # Customize SSL scoring logic
    pass
```

### ADK Integration

```python
from google.adk.agents import Agent

url_analyzer_agent = Agent(
    name="url_analyzer",
    model="gemini-2.5-flash",
    instruction="Analyze URL for malicious content",
    tools=[scrape_tool, risk_score_tool]
)
```

### Real-Time Monitoring

```python
import asyncio

async def monitor_analysis(task_id: str):
    while True:
        result = read_analysis_result(task_id)
        if result:
            print(f"Risk: {result['risk_score']}")
        await asyncio.sleep(1)
```

## License

MIT License - See LICENSE file

## Support

For issues or questions:
1. Check logs: `docker logs <container_id>`
2. Review README troubleshooting section
3. File issue with task_id and error details

## Contributing

Pull requests welcome! Areas for improvement:
- Machine learning models for classification
- Real-time URL database integration
- Visual report generation
- WebSocket streaming support
