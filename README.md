---
title: Quant-Gym
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Quant-Gym: Financial Analysis Environment for AI Agents

An OpenEnv-compliant environment that tests AI agents on financial data analysis, market sentiment, and trading strategy evaluation.



## 🎯 Overview

Quant-Gym is a benchmark environment where AI agents can practice:
- Fetching real-time market data
- Analyzing financial news sentiment
- Executing buy/sell trades
- Evaluating trading strategies with risk metrics

**This is a research benchmark for evaluating AI reasoning in financial contexts, not a trading tool.**


## 📊 Environment Tasks

| Task | Description | Difficulty |
|------|-------------|------------|
| **Task 1** | Fetch current market price for AAPL | Easy |
| **Task 2** | Analyze news headlines and recommend Buy/Sell/Hold with explanation | Medium |
| **Task 3** | Backtest a trading strategy (momentum/mean reversion) with Sharpe ratio & drawdown | Hard |


## 🏗️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/health` | GET | Health check |
| `/metadata` | GET | Environment metadata |
| `/schema` | GET | Action/observation schemas |
| `/reset` | POST | Reset environment to initial state |
| `/step` | POST | Execute an action |
| `/state` | GET | Get current environment state |
| `/tasks` | GET | List all available tasks |
| `/docs` | GET | Interactive API documentation |


## 🔧 Installation

### Prerequisites
- Python 3.10+
- Docker (for containerized deployment)

### Local Setup

```bash
# Clone the repository
git clone https://github.com/Astocoder/quant-gym-openenv.git
cd quant-gym-openenv

# Install dependencies
pip install -r requirements.txt

# Set up Hugging Face token for LLM features (create .env file)
echo 'HF_TOKEN=your_hf_token_here' > .env

# Start the server
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload



🎮 Action Schema
The agent can take the following actions:

json
{
  "type": "BUY | SELL | GET_PRICE | BACKTEST | GET_NEWS",
  "amount": 10,
  "explanation": "RSI indicates oversold condition",
  "strategy": "momentum"
}
Action Examples
Action	Description
{"type": "GET_PRICE"}	Get current stock price
{"type": "BUY", "amount": 10}	Buy 10 shares
{"type": "SELL", "amount": 5}	Sell 5 shares
{"type": "GET_NEWS", "explanation": "your analysis"}	Get news with analysis
{"type": "BACKTEST", "strategy": "momentum"}	Backtest momentum strategy


👁️ Observation Schema
The environment returns:

json
{
  "timestamp": "step_5",
  "price": 155.00,
  "balance": 8500.00,
  "holdings": 10,
  "portfolio_value": 10050.00,
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



🏃 Running the Baseline Agent
bash
# Set your Hugging Face token
export HF_TOKEN="your_hf_token_here"

# Run inference
python inference.py
Expected Output
text
[INFO] Starting Quant-Gym Inference
[START] task=quant-gym env=quant-gym model=gpt-3.5-turbo
[STEP] step=1 action=BUY 5 reward=0.15 done=false error=null
[STEP] step=2 action=GET_PRICE reward=0.05 done=false error=null
[STEP] step=3 action=SELL 5 reward=0.20 done=false error=null
...
[END] success=true steps=10 score=0.650 rewards=...


🐳 Docker Deployment
Build and run with Docker:

bash
# Build the image
docker build -t quant-gym .

# Run the container
docker run -p 7860:7860 quant-gym
Then access the API at http://localhost:7860

🌐 Hugging Face Space
Live demo: https://huggingface.co/spaces/Astocoder/quant-gym


📁 Project Structure
text
quant-gym-openenv/
├── Dockerfile              # Container configuration
├── inference.py            # Baseline agent script
├── models.py               # Pydantic schemas
├── openenv.yaml            # OpenEnv configuration
├── pyproject.toml          # Python project config
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── task1_grader.py         # Price fetch grader
├── task2_grader.py         # News analysis grader
├── task3_grader.py         # Backtest grader
├── server/
│   ├── app.py              # FastAPI server
│   ├── environment.py      # Trading logic
│   └── data/
│       ├── prices.csv      # Market data
│       └── news.json       # News headlines
└── graders/                # Backup grader folder
    ├── task1_grader.py
    ├── task2_grader.py
    └── task3_grader.py


🔐 Environment Variables
Variable	Description	Default
HF_TOKEN	Hugging Face API token	None (optional)
API_BASE_URL	LLM API endpoint	None (judge provides)
API_KEY	LLM API key	None (judge provides)
BASE_URL	Quant-Gym API URL	http://localhost:8000


📈 Evaluation Criteria
OpenEnv Compliance: Full implementation of step()/reset()/state() APIs

Task Completion: All 3 tasks return scores between 0.0-1.0

Reward Function: Partial progress signals for meaningful learning

Reproducibility: Static data ensures consistent results


💡 Unique Innovation
Unlike traditional trading environments that only measure profit, Quant-Gym rewards explanation quality:

Agents must explain their reasoning for each trade

Graders evaluate financial terminology, logical reasoning, and detail

Promotes transparent, auditable AI decision-making



⚠️ Disclaimer
This is a research benchmark environment for evaluating AI agent reasoning. It does not provide financial advice or real trading recommendations. All data is for simulation purposes only.


📄 License
MIT License - See LICENSE file for details.

Built with: Python, FastAPI, OpenEnv, Hugging Face, Docker


