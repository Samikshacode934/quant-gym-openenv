cat > README.md << 'EOF'
# Quant-Gym: Financial Analysis Environment for AI Agents

An OpenEnv-compliant environment that tests AI agents on financial data analysis, market sentiment, and trading strategy evaluation.

## 🎯 Overview

Quant-Gym is a benchmark environment where AI agents can practice:
- Fetching real-time market data
- Analyzing financial news sentiment
- Evaluating trading strategies with risk metrics

This is a **research benchmark** for evaluating AI reasoning in financial contexts, not a trading tool.

## 📊 Environment Tasks

| Task | Description | Difficulty |
|------|-------------|------------|
| **Task 1** | Fetch current market price for AAPL | Easy |
| **Task 2** | Analyze news headlines and recommend Buy/Sell/Hold with explanation | Medium |
| **Task 3** | Backtest a trading strategy (momentum/mean reversion) with Sharpe ratio & drawdown | Hard |

## 🏗️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/reset` | POST | Reset environment to initial state |
| `/step` | POST | Execute an action (BUY/SELL/GET_PRICE/BACKTEST) |
| `/state` | GET | Get current environment state |
| `/tasks` | GET | List all available tasks |

## 🔧 Installation

### Prerequisites
- Python 3.10+
- Docker (for containerized deployment)

### Local Setup

```bash
# Clone the repository
git clone https://github.com/Samikshacode934/quant-gym-openenv.git
cd quant-gym-openenv

# Install dependencies
pip install -r requirements.txt

# Download market data
python download_data.py

# Start the server
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000


🎮 Action Schema
The agent can take the following actions:
{
  "type": "BUY | SELL | GET_PRICE | BACKTEST",
  "amount": 10,
  "explanation": "RSI indicates oversold condition",
  "strategy": "momentum"
}



👁️ Observation Schema
The environment returns:

{
  "timestamp": "2026-03-31 14:30:00",
  "price": 248.45,
  "balance": 8500.00,
  "holdings": 10,
  "portfolio_value": 10984.50,
  "last_news": {
    "headline": "Apple announces new AI chip",
    "sentiment": "positive"
  },
  "backtest_results": {
    "sharpe_ratio": 1.35,
    "max_drawdown": 0.12,
    "total_return": 0.18
  }
}




Architecture
quant-gym-openenv/
├── models.py              # Pydantic schemas
├── openenv.yaml           # OpenEnv configuration
├── inference.py           # Baseline agent
├── requirements.txt       # Dependencies
├── server/
│   ├── app.py            # FastAPI server
│   ├── environment.py    # Trading logic
│   ├── Dockerfile        # Container config
│   └── data/
│       ├── prices.csv    # Market data
│       └── news.json     # News headlines
└── graders/
    ├── task1_grader.py
    ├── task2_grader.py
    └── task3_grader.py