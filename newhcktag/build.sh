#!/bin/bash
# Build and setup script for malware detection pipeline

set -e

echo "=========================================="
echo "Malware Detection Pipeline Setup"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Docker installation
echo -e "${BLUE}[1/5]${NC} Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

# Check Docker daemon
echo -e "${BLUE}[2/5]${NC} Checking Docker daemon..."
if ! docker ps &> /dev/null; then
    echo -e "${RED}Docker daemon is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker daemon running${NC}"

# Create required directories
echo -e "${BLUE}[3/5]${NC} Creating directories..."
mkdir -p data logs
chmod 777 data logs
echo -e "${GREEN}✓ Directories created${NC}"

# Build Docker images
echo -e "${BLUE}[4/5]${NC} Building Docker images..."

echo "  - Building scraper image..."
docker build -f Dockerfile.scraper -t malware-scraper:latest . --quiet
echo -e "    ${GREEN}✓ malware-scraper:latest${NC}"

echo "  - Building analyzer image..."
docker build -f Dockerfile.analyzer -t malware-analyzer:latest . --quiet
echo -e "    ${GREEN}✓ malware-analyzer:latest${NC}"

echo "  - Building orchestrator image..."
docker build -f Dockerfile.orchestrator -t malware-orchestrator:latest . --quiet
echo -e "    ${GREEN}✓ malware-orchestrator:latest${NC}"

# Setup environment
echo -e "${BLUE}[5/5]${NC} Setting up environment..."

if [ ! -f .env ]; then
    cat > .env << EOF
GOOGLE_API_KEY=your_google_api_key_here
DOCKER_HOST=unix:///var/run/docker.sock
REQUEST_TIMEOUT=30
MAX_RETRIES=3
EOF
    echo -e "${GREEN}✓ Created .env file (update GOOGLE_API_KEY)${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Display summary
echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update GOOGLE_API_KEY in .env file"
echo "2. Run: python malware_detector.py"
echo "3. Or: docker-compose up"
echo ""
echo "Verify installation:"
echo "  docker images | grep malware"
echo ""
echo "Test single URL:"
echo "  python -c \"from malware_detector import analyze_url; print(analyze_url('https://example.com'))\""
echo ""
