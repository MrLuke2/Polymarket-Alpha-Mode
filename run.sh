#!/bin/bash
# ============================================
# POLYMARKET ALPHA MODE - Launch Script
# ============================================
# Runs Dashboard and Trading Backend simultaneously
#
# Usage:
#   ./run.sh          - Start both components
#   ./run.sh dashboard - Start dashboard only
#   ./run.sh backend   - Start backend only
# ============================================

set -e

# Colors for output
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║        ⚡ POLYMARKET ALPHA MODE ⚡                           ║"
echo "║        Elite Prediction Market Intelligence                ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Create necessary directories
mkdir -p logs data

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating template...${NC}"
    cat > .env << EOF
# ============================================
# POLYMARKET ALPHA MODE - Environment Variables
# ============================================

# API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
POLYMARKET_API_KEY=your_polymarket_key_here
POLYMARKET_API_SECRET=your_polymarket_secret_here

# Wallet (for actual trading - use with caution!)
WALLET_PRIVATE_KEY=your_private_key_here
WALLET_ADDRESS=your_wallet_address_here

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379
EOF
    echo -e "${GREEN}Created .env template. Please fill in your credentials.${NC}"
fi

# Function to start dashboard
start_dashboard() {
    echo -e "${MAGENTA}[DASHBOARD]${NC} Starting War Room on http://localhost:8501"
    streamlit run dashboard/app.py --server.port 8501 --server.headless true
}

# Function to start backend
start_backend() {
    echo -e "${CYAN}[BACKEND]${NC} Starting Trading Engine..."
    python main.py
}

# Function to start both
start_all() {
    echo -e "${GREEN}Starting all components...${NC}"
    echo ""
    
    # Start backend in background
    python main.py &
    BACKEND_PID=$!
    echo -e "${CYAN}[BACKEND]${NC} Started (PID: $BACKEND_PID)"
    
    # Give backend a moment to initialize
    sleep 2
    
    # Start dashboard (foreground)
    echo -e "${MAGENTA}[DASHBOARD]${NC} Starting War Room..."
    echo -e "${GREEN}Dashboard URL: http://localhost:8501${NC}"
    echo ""
    streamlit run dashboard/app.py --server.port 8501 --server.headless true
    
    # Cleanup on exit
    trap "echo 'Shutting down...'; kill $BACKEND_PID 2>/dev/null" EXIT
}

# Parse command line args
case "${1:-all}" in
    dashboard)
        start_dashboard
        ;;
    backend)
        start_backend
        ;;
    all|*)
        start_all
        ;;
esac
