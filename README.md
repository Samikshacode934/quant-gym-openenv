# Quant-Gym: Financial Analysis Environment for AI Agents

An OpenEnv-compliant environment that tests AI agents on:
- Real-time market data retrieval
- News sentiment analysis with explainable reasoning
- Trading strategy backtesting with risk metrics

## 🎯 Tasks
1. **Fetch Market Data** - Retrieve current price for AAPL
2. **News Analysis** - Analyze headlines and recommend Buy/Sell/Hold with rationale
3. **Backtest Strategy** - Simulate strategy and report Sharpe ratio & max drawdown

## 🛠️ Setup
```bash
pip install -r requirements.txt
uvicorn server.app:app --reload
