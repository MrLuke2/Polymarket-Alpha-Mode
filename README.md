# ⚡ POLYMARKET GOD MODE ⚡

> Elite Prediction Market Intelligence Platform

A cyberpunk-themed trading dashboard with multi-agent AI decision-making and whale copy-trading capabilities for Polymarket.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🎯 Features

### Module 1: War Room Dashboard
- **Cyberpunk Bloomberg aesthetic** - Dark mode UI with neon accents
- **Live AI monologue feed** - Watch the AI's internal reasoning in real-time
- **Sniper Scope** - Visual list of markets being monitored
- **PnL Chart** - Real-time portfolio performance vs BTC benchmark
- **System controls** - Start/stop trading, adjust risk parameters

### Module 2: Council of Agents (Swarm Intelligence)
- **The Fundamentalist** - Analyzes news, facts, and historical patterns
- **The Sentiment Analyst** - Reads social trends and market psychology
- **The Risk Manager** - Veto power for high-risk trades
- **2/3 Consensus Required** - Democratic decision-making for all trades

### Module 3: Alpha Engine (Predictive Correlation)
- **Live Binance Feed** - Monitors Binance order book imbalance (BTC/USDT) via WebSockets
- **Predictive Signals** - Detects buy/sell walls before they hit Polymarket
- **Automated Strike Trading** - High-confidence signals automatically execute on Polymarket strike price markets

### Module 4: Whale Watcher (Copy Trading)
- **Track top wallets** - Monitor the most profitable traders (Domer, Théo, etc.)
- **AI profiling** - Extracts intelligence from built-in classified whale dossiers
- **Real-time copy** - Polls Polymarket Clob API for live whale trade detection

### Module 5: Press Secretary (Viral Engine)
- **PnL Card Generator** - Automatically draws sleek, shareable images of winning trades
- **Tweet Drafter** - Generates viral tweet variations for social "flexing"
- **Human-in-the-Loop** - Review and copy drafts directly from the dashboard for safety

---

## 📁 Project Structure

```
polymarket-god-mode/
├── dashboard/
│   ├── __init__.py
│   └── app.py              # Streamlit War Room UI
├── agents/
│   ├── __init__.py
│   └── swarm.py            # Council of Agents logic
├── strategies/
│   ├── __init__.py
│   └── whale_watcher.py    # Whale copy-trading
├── core/
│   ├── __init__.py
│   ├── models.py           # Pydantic data models
│   └── state.py            # Thread-safe state manager
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration management
├── utils/                  # Utility functions
├── data/                   # Data storage
├── logs/                   # Log files
├── tests/                  # Test suite
├── main.py                 # Backend entry point
├── run.sh                  # Launch script
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip or conda

### Installation

```bash
# Clone/download the repository
cd polymarket-god-mode

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Running the Platform

**Option 1: Full System (Dashboard + Backend)**
```bash
chmod +x run.sh
./run.sh
```

**Option 2: Dashboard Only**
```bash
streamlit run dashboard/app.py
```

**Option 3: Backend Only**
```bash
python main.py
```

Access the dashboard at: **http://localhost:8501**

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for agent reasoning | Optional* |
| `ANTHROPIC_API_KEY` | Anthropic API key (alternative) | Optional* |
| `POLYMARKET_API_KEY` | Polymarket API credentials | For live trading |
| `POLYMARKET_API_SECRET` | Polymarket API secret | For live trading |
| `WALLET_PRIVATE_KEY` | Wallet for transactions | For live trading |
| `WALLET_ADDRESS` | Your wallet address | For live trading |
| `REDIS_URL` | Redis for caching | Optional |

*System uses rule-based fallback if LLM keys not provided

### Risk Parameters

Edit in `config/settings.py` or via dashboard:

```python
max_single_trade = 500.0      # Max trade size in USDC
max_daily_loss = 1000.0       # Stop-loss threshold
volatility_threshold = 0.15   # 15% volatility veto trigger
council_voting_threshold = 0.67  # 2/3 majority required
whale_copy_percentage = 0.10  # Copy 10% of whale size
whale_min_trade_size = 1000.0 # Min whale trade to consider
```

---

## 🧠 Council of Agents Architecture

```
                    ┌─────────────────┐
                    │  Market Signal  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │ FUNDAMENTALIST  │ │    SENTIMENT    │ │  RISK MANAGER   │
    │                 │ │                 │ │                 │
    │ • News analysis │ │ • Social trends │ │ • Volatility    │
    │ • Historical    │ │ • Momentum      │ │ • Portfolio fit │
    │ • Base rates    │ │ • Crowd psych   │ │ • Liquidity     │
    │                 │ │                 │ │ • VETO POWER    │
    └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
             │                   │                   │
             └───────────────────┼───────────────────┘
                                 │
                        ┌────────▼────────┐
                        │  COUNCIL VOTE   │
                        │  (2/3 Required) │
                        └────────┬────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                                     │
              ▼                                     ▼
    ┌─────────────────┐                   ┌─────────────────┐
    │    APPROVED     │                   │    REJECTED     │
    │ Execute Trade   │                   │   Log & Skip    │
    └─────────────────┘                   └─────────────────┘
```

---

## 🐋 Whale Watcher Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Monitor Wallets │ ──▶ │  Detect Trade   │ ──▶ │  Size Check     │
│  (Top 5 PnL)    │     │   (>$1,000)     │     │  (Above min?)   │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │  AI Analysis    │ ◀── │ Whale Profile   │
                        │  (Should copy?) │     │ (Trust score)   │
                        └────────┬────────┘     └─────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                                     │
              ▼                                     ▼
    ┌─────────────────┐                   ┌─────────────────┐
    │    AI AGREES    │                   │  AI DISAGREES   │
    │ Copy 10% size   │                   │ Skip, log why   │
    └─────────────────┘                   └─────────────────┘
```

---

## 📊 Dashboard Preview

The War Room features:
- **Real-time portfolio chart** with BTC benchmark overlay
- **AI monologue feed** with color-coded log levels
- **Sniper Scope** showing watched markets with trigger prices
- **Council status** with agent votes and recent decisions
- **Whale leaderboard** with trust scores and PnL

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific module tests
pytest tests/test_agents.py -v
```

---

## 🔒 Security Notes

1. **Never commit `.env`** - It's in `.gitignore`
2. **Use a dedicated wallet** - Only fund with what you can lose
3. **Start in demo mode** - Test without real funds first
4. **Review whale addresses** - Verify before trusting

---

## 📝 Extending the Platform

### Adding a New Agent

```python
# In agents/swarm.py

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.CUSTOM, "My Agent")
    
    async def analyze(self, market: Market, context: Dict) -> AgentAnalysis:
        # Your analysis logic here
        return self._create_analysis(
            vote=AgentVote.YES,
            confidence=0.75,
            reasoning="My reasoning...",
            data_sources=["source1", "source2"],
            analysis_time_ms=100
        )

# Add to council
council.agents.append(MyCustomAgent())
```

### Adding a New Strategy

```python
# In strategies/my_strategy.py

class MyStrategy:
    async def generate_signals(self, markets: List[Market]) -> List[TradeSignal]:
        signals = []
        for market in markets:
            if self._meets_criteria(market):
                signals.append(TradeSignal(...))
        return signals
```

---

## 📄 License

MIT License - Use at your own risk. This is experimental software.

---

## ⚠️ Disclaimer

This software is for educational and research purposes. Trading prediction markets involves significant financial risk. Never trade with funds you cannot afford to lose. The authors are not responsible for any financial losses incurred through use of this software.

---

<div align="center">

**Built with 🔥 for the degen community**

*May your predictions be ever accurate*

</div>
