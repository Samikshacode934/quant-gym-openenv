import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from pathlib import Path
import json
import numpy as np
from typing import Optional, Dict, Any, List
from models import MarketObservation, AgentAction

class TradingEnvironment:
    def __init__(self):
        # Initialize with simple data if CSV doesn't exist
        self.prices = [150, 152, 151, 153, 155, 154, 156, 158, 157, 159]
        self.news = [
            {"headline": "Apple announces new AI chip", "sentiment": "positive"},
            {"headline": "Supply chain delays expected", "sentiment": "negative"},
            {"headline": "Analysts raise price target", "sentiment": "positive"},
            {"headline": "Market shows strong growth", "sentiment": "positive"},
        ]
        self.reset()
    
    def reset(self):
        self.idx = 0
        self.cash = 10000.0
        self.shares = 0
        self.total_steps = len(self.prices)
        self.tasks_completed = []
        return self._get_observation()
    
    def step(self, action: AgentAction):
        # Move time forward
        self.idx = min(self.idx + 1, self.total_steps - 1)
        price = self.prices[self.idx]
        
        if action.type == "BUY" and action.amount:
            cost = price * action.amount
            if cost <= self.cash:
                self.cash -= cost
                self.shares += action.amount
        elif action.type == "SELL" and action.amount:
            if action.amount <= self.shares:
                self.cash += price * action.amount
                self.shares -= action.amount
        elif action.type == "BACKTEST":
            return self._get_observation_with_backtest(action.strategy)
        
        return self._get_observation()
    
    def _get_observation(self):
        price = self.prices[self.idx]
        news_idx = self.idx % len(self.news)
        
        return MarketObservation(
            timestamp=f"step_{self.idx}",
            price=float(price),
            balance=round(self.cash, 2),
            holdings=self.shares,
            portfolio_value=round(self.cash + self.shares * price, 2),
            last_news=self.news[news_idx]
        )
    
    def _get_observation_with_backtest(self, strategy):
        obs = self._get_observation()
        if strategy and "momentum" in strategy.lower():
            obs.backtest_results = {"sharpe_ratio": 1.35, "max_drawdown": 0.12, "total_return": 0.18}
        else:
            obs.backtest_results = {"sharpe_ratio": 0.85, "max_drawdown": 0.18, "total_return": 0.09}
        return obs
    
    def state(self):
        return {
            "current_step": self.idx,
            "total_steps": self.total_steps,
            "observation": self._get_observation().dict(),
            "tasks_completed": self.tasks_completed
        }
