# Malware Detection Pipeline - Technical Architecture

## System Architecture

### High-Level Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                          Orchestration Layer                         │
│  • Docker Client API                                                 │
│  • Task Management & Lifecycle                                       │
│  • Error Handling & Retry Logic                                      │
│  • Result Aggregation                                                │
└─────────┬──────────────────────────────────────────────────┬────────┘
          │                                                  │
          │ Create                               Create    │
          ▼                                                  ▼
    ┌──────────────┐                                   ┌──────────────┐
    │   Scraper    │                                   │  Analyzer    │
    │  Container   │                                   │  Container   │
    ├──────────────┤                                   ├──────────────┤
    │ httpx        │◄────────Shared Volume─────────►│ google-adk   │
    │ BeautifulSoup│  malware_detection_volume  │ Risk Scoring │
    │ lxml         │                                   │ ADK Agent    │
    │ hashlib      │                                   │ Pydantic     │
    └──────────────┘                                   └──────────────┘
          │                                                  │
          │ Write (JSON)                        Read (JSON) │
          └──────────────────────────────────────────────────┘
                    shared_<task_id>.json
```

## Component Details

### 1. Orchestrator (malware_detector.py)

**Responsibilities:**
- Docker resource lifecycle management
- Task ID generation and tracking
- Container startup/monitoring
- Error handling and cleanup
- Result aggregation

**Key Classes/Functions:**
- `Docker Client`: Interface with Docker daemon
- `setup_docker_resources()`: Create network and volume
- `run_scraper_container()`: Execute scraper
- `run_analyzer_container()`: Execute analyzer
- `analyze_url()`: Main orchestration logic

**Communication Pattern:**
```python
# Task creation
task_id = generate_task_id()  # Format: task_abc123_1731604800

# Container creation with environment
container = client.containers.run(
    image_name,
    environment={"TASK_ID": task_id, "TARGET_URL": url, ...},
    volumes={volume_name: {"bind": mount_path, "mode": "rw"}},
    network=network_name,
    detach=True
)

# Wait for completion
exit_code = container.wait(timeout=30)

# Cleanup
container.stop()
container.remove()
```

### 2. Scraper (scraper.py)

**Responsibilities:**
- HTTP request execution
- HTML parsing and analysis
- Metadata extraction
- Security pattern detection
- JSON result serialization

**Key Functions:**
- `scrape_url()`: Async HTTP request with timeouts
- `extract_metadata()`: Security-relevant data extraction
- `extract_scripts()`: JavaScript analysis
- `detect_suspicious_patterns()`: Pattern matching
- `extract_links()`: External resource enumeration

**Data Flow:**
```
TARGET_URL (env)
    ↓
[httpx.AsyncClient]
    ↓
[HTML Response]
    ↓
[BeautifulSoup Parsing]
    ↓
[Multi-level Extraction]
    ├─ SSL/TLS info
    ├─ Security headers
    ├─ Scripts/iframes
    ├─ Forms/inputs
    ├─ Meta tags
    └─ Suspicious patterns
    ↓
[JSON Serialization]
    ↓
[Write to shared volume]
    ↓
scraped_<task_id>.json
```

**Extraction Layers:**
1. **HTTP Layer**: Status codes, headers, redirects
2. **DOM Layer**: Tags, attributes, structure
3. **Security Layer**: CSP, CORS, X-Frame-Options
4. **Content Layer**: Scripts, forms, external resources
5. **Metadata Layer**: Size, encoding, hashes

### 3. Analyzer (analyzer.py)

**Responsibilities:**
- Load scraper results
- Risk calculation
- Classification (benign/suspicious/malicious)
- ADK integration
- Result persistence

**Scoring Algorithm:**
```
Risk Score = weighted_sum([
    (1 - ssl_score) * 0.20,
    (1 - header_score) * 0.15,
    pattern_score * 0.25,
    resource_score * 0.20,
    metadata_score * 0.10,
    form_score * 0.10
])

Classification:
- risk_score >= 0.60 → Malicious
- 0.40 <= risk_score < 0.60 → Suspicious
- risk_score < 0.40 → Benign
```

**Component Scores:**
```python
score_ssl_security():
    - Factors: HTTPS usage
    - Range: [0, 1] (inverted: higher=safer)

score_security_headers():
    - Factors: CSP, X-Frame-Options, X-Content-Type-Options
    - Penalizes: Excessive cookies
    - Range: [0, 1] (inverted: higher=safer)

score_suspicious_patterns():
    - Factors: eval(), obfuscation, redirects, popups
    - Range: [0, 1] (higher=more suspicious)

score_external_resources():
    - Factors: External scripts, unsafe iframes, links
    - Range: [0, 1] (higher=more risky)

score_content_metadata():
    - Factors: File size, content type, meta tags
    - Range: [0, 1]

score_forms_and_inputs():
    - Factors: Form targets, methods, input count
    - Range: [0, 1] (higher=more suspicious)
```

## Data Flow & Communication

### Request Flow

```
1. User Input (URL)
        ↓
2. Orchestrator: analyze_url(url)
        ↓
3. Create Task ID & Docker Resources
        ↓
4. Launch Scraper Container
        │
        ├─ Mount shared volume
        ├─ Pass URL via environment
        ├─ Execute scraper.py
        ├─ Write JSON to volume
        └─ Exit & cleanup
        ↓
5. Wait for Data Transfer (2s)
        ↓
6. Launch Analyzer Container
        │
        ├─ Mount shared volume (read-only)
        ├─ Load JSON from volume
        ├─ Execute scoring algorithm
        ├─ Invoke ADK agent logic
        ├─ Write results to volume
        └─ Exit & cleanup
        ↓
7. Read Results from Volume
        ↓
8. Return to User
```

### File Format (JSON)

**Scraper Output: scraped_<task_id>.json**
```json
{
  "status": "success|error",
  "metadata": {
    "url": "https://example.com",
    "domain": "example.com",
    "timestamp": "2024-11-14T18:14:00.123Z",
    "content_hash": "sha256_hash",
    "content_length": 45230,
    "status_headers": {
      "content_type": "text/html; charset=utf-8",
      "server": "nginx",
      "x_frame_options": "SAMEORIGIN",
      "x_content_type_options": "nosniff",
      "content_security_policy": "...",
      "set_cookie": true
    },
    "ssl_info": {
      "is_https": true,
      "protocol": "https"
    },
    "scripts": [
      {"src": "https://cdn.example.com/script.js", "inline": false, "type": "text/javascript"}
    ],
    "links": [
      {"url": "https://external.com", "is_external": true, "text": "Click here"}
    ],
    "forms": [
      {"action": "https://example.com/submit", "method": "POST", "inputs": 5}
    ],
    "iframes": [
      {"src": "https://embed.example.com", "sandboxed": true}
    ],
    "meta_tags": {
      "description": "Example site",
      "viewport": "width=device-width"
    },
    "suspicious_patterns": {
      "has_eval": false,
      "has_document_write": false,
      "has_obfuscated_code": false,
      "has_suspicious_redirect": false,
      "has_form_redirect": false,
      "has_popup": false,
      "has_plugin_object": false
    }
  },
  "html_preview": "<!DOCTYPE html>...",
  "error": null
}
```

**Analyzer Output: result_<task_id>.json**
```json
{
  "task_id": "task_abc123_1731604800",
  "url": "https://example.com",
  "analysis": {
    "classification": "benign|suspicious|malicious",
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
    "recommendations": ["Site appears safe to visit"],
    "timestamp": "2024-11-14T18:14:02.456Z"
  },
  "scrape_metadata": {
    "domain": "example.com",
    "content_length": 45230,
    "timestamp": "2024-11-14T18:14:00.123Z"
  },
  "timestamp": "2024-11-14T18:14:02.456Z"
}
```

## Docker Architecture

### Network Topology

```
┌──────────────────────────────────────┐
│  Docker Bridge Network               │
│  malware_detection_net               │
│  Driver: bridge                      │
│  Subnet: 172.20.0.0/16              │
│                                      │
│  ┌─────────────────────────────────┐│
│  │ Orchestrator Container          ││
│  │ IP: 172.20.0.1 (dynamic)       ││
│  │ mounts: /var/run/docker.sock   ││
│  └─────────────────────────────────┘│
│                                      │
│  ┌─────────────────────────────────┐│
│  │ Scraper Container               ││
│  │ IP: 172.20.0.2 (dynamic)       ││
│  │ mounts: /data (shared volume)   ││
│  └─────────────────────────────────┘│
│                                      │
│  ┌─────────────────────────────────┐│
│  │ Analyzer Container              ││
│  │ IP: 172.20.0.3 (dynamic)       ││
│  │ mounts: /data (shared volume)   ││
│  └─────────────────────────────────┘│
└──────────────────────────────────────┘
```

### Shared Volume Structure

```
/var/lib/docker/volumes/malware_detection_volume/_data/
├── scraped_<task_id_1>.json
├── content_<task_id_1>.html
├── result_<task_id_1>.json
├── scraped_<task_id_2>.json
├── content_<task_id_2>.html
├── result_<task_id_2>.json
└── ...
```

### Container Lifecycle

```
1. CREATE
   - Image pull/use cached
   - Container creation
   - Resource allocation
   - Network attachment
   
2. START
   - Entrypoint execution
   - Application startup
   - Environment variable loading
   
3. RUNNING
   - Task execution
   - Logging
   - Health monitoring
   
4. STOP
   - Signal: SIGTERM (15s timeout)
   - Graceful shutdown
   - Resource cleanup
   
5. REMOVE
   - Container filesystem removal
   - Network detachment
   - Logging archive
   
Total Lifecycle: ~3-5 seconds per container
```

## Performance Optimizations

### 1. Image Size Optimization

**Scraper Image (~200MB)**
```dockerfile
FROM python:3.11-slim      # 131 MB base
+ httpx (1 MB)
+ beautifulsoup4 (0.5 MB)
+ lxml (5 MB)
= ~137 MB total
```

**Analyzer Image (~250MB)**
```dockerfile
FROM python:3.11-slim      # 131 MB base
+ google-adk (1 MB)
+ google-genai (2 MB)
+ pydantic (1 MB)
= ~135 MB total
```

### 2. Request Optimization

```python
# Connection pooling
async with httpx.AsyncClient(timeout=20) as client:
    # Reuses connections
    response = await client.get(url)

# Memory-efficient parsing
soup = BeautifulSoup(html, 'lxml')  # C-based parser
for element in soup.find_all(..., limit=10):  # Limit results
    # Process incrementally
```

### 3. Resource Limits

```python
MAX_CONTENT_SIZE = 10 * 1024 * 1024  # 10 MB limit
REQUEST_TIMEOUT = 20                  # Seconds
MAX_RETRIES = 3
```

## Error Handling & Resilience

### Error Categories

```
┌─ Network Errors
│  ├─ Timeout
│  ├─ Connection refused
│  ├─ DNS resolution failure
│  └─ SSL/TLS certificate error
│
├─ HTTP Errors
│  ├─ 4xx (client errors)
│  ├─ 5xx (server errors)
│  └─ Redirects (>10 hops)
│
├─ Container Errors
│  ├─ Image not found
│  ├─ Insufficient resources
│  ├─ Container crash
│  └─ Timeout
│
└─ Data Errors
   ├─ Invalid JSON
   ├─ File not found
   ├─ Permission denied
   └─ Corrupted data
```

### Recovery Mechanisms

```python
# Retry logic
for attempt in range(MAX_RETRIES):
    try:
        result = scrape_url(url)
        break
    except RequestError:
        if attempt < MAX_RETRIES - 1:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        else:
            raise

# Graceful degradation
if not analysis_result:
    result["analysis"] = {
        "classification": "unknown",
        "error": "Analysis failed",
        "recommendations": ["Manual review required"]
    }

# Resource cleanup
finally:
    container.stop(timeout=5)
    container.remove()
```

## Security Architecture

### Container Security

```
1. Non-root Users
   - Scraper: UID 1000 (scraper user)
   - Analyzer: UID 1001 (analyzer user)
   - Read-only filesystem where possible

2. Network Isolation
   - Custom bridge network
   - No external port exposure
   - Internal communication only

3. Resource Limits
   - Memory: 256 MB soft, 512 MB hard
   - CPU: 0.5 cores
   - Timeout: 30 seconds max

4. Data Protection
   - Encrypted volumes (optional)
   - Temporary data cleanup
   - No credential logging
```

### Risk Scoring Security

```
1. Multi-factor Analysis
   - SSL/TLS verification (0.20 weight)
   - HTTP security headers (0.15 weight)
   - JavaScript analysis (0.25 weight)
   - Resource enumeration (0.20 weight)
   - Content analysis (0.10 weight)
   - Form analysis (0.10 weight)

2. False Positive Mitigation
   - Confidence scores
   - Recommendation context
   - Manual review suggestions

3. Threat Intelligence Integration
   - Checksum hashing (SHA256)
   - Domain reputation lookup (future)
   - Known malware signatures (future)
```

## Scalability Considerations

### Vertical Scaling

```
Current Config:
- Single orchestrator process
- Sequential URL analysis
- ~3-5 sec per URL

Bottleneck: CPU for parallel container management
```

### Horizontal Scaling

```
1. Task Queue (Redis/RabbitMQ)
   - Multiple orchestrator instances
   - Load balancing
   - Fault tolerance

2. Distributed Analysis
   - Multiple Docker hosts
   - Kubernetes cluster
   - Cloud container services

3. Result Caching
   - Cache analysis results
   - Reduce duplicate processing
   - Quick lookups
```

### Throughput Estimates

```
Sequential:  1-2 URLs/sec
Parallel(4): 4-8 URLs/sec
Distributed: 20-50 URLs/sec (depending on infrastructure)
```

## Monitoring & Observability

### Metrics to Track

```
1. Performance Metrics
   - Scraper duration (p50, p95, p99)
   - Analyzer duration
   - Total pipeline duration
   - Success rate

2. Resource Metrics
   - Container memory usage
   - Container CPU usage
   - Volume usage
   - Network I/O

3. Quality Metrics
   - Risk score distribution
   - Classification accuracy
   - False positive rate
   - Confidence scores
```

### Logging Strategy

```
Levels:
- INFO: Task start/completion, key events
- WARNING: Retries, timeouts, resource constraints
- ERROR: Failures, exceptions, cleanup issues
- DEBUG: Detailed execution, intermediate states

Log Rotation:
- Daily rotation
- 30-day retention
- Compression after 7 days
- Archive to S3/GCS
```

---

**Version**: 1.0.0
**Last Updated**: November 2024
**Document Type**: Technical Specification
