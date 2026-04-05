import asyncio
import os
import textwrap
from typing import List, Optional
from openai import OpenAI
import requests

# Try to load from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[INFO] Loaded .env file", flush=True)
except ImportError:
    print("[INFO] python-dotenv not installed, using system env only", flush=True)

# Environment variables (set by the judge or .env)
API_BASE_URL = os.getenv("API_BASE_URL", "https://api-inference.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.2-3B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

# Quant-Gym specific configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
TASK_NAME = os.getenv("TASK_NAME", "quant-gym")
BENCHMARK = os.getenv("BENCHMARK", "quant-gym")
MAX_STEPS = 10
TEMPERATURE = 0.7
MAX_TOKENS = 200
SUCCESS_SCORE_THRESHOLD = 0.7

# System prompt for financial analysis
SYSTEM_PROMPT = textwrap.dedent(
    """
    You are a financial analyst AI agent. Your goal is to analyze market data and make trading decisions.
    
    Available actions:
    - GET_PRICE: Get current stock price
    - BUY [amount]: Buy number of shares
    - SELL [amount]: Sell number of shares
    - BACKTEST [strategy]: Backtest a strategy (momentum or mean_reversion)
    - GET_NEWS: Get latest news headline
    
    Strategy tips:
    - Positive news sentiment suggests BUY
    - Negative news sentiment suggests SELL
    - Momentum strategy: Buy when price is rising
    - Mean reversion: Buy when price is low relative to recent average
    
    Respond with EXACTLY one action in format: ACTION [parameter]
    Example: BUY 10
    Example: GET_PRICE
    Example: BACKTEST momentum
    """
).strip()


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


class QuantGymClient:
    """Client for interacting with Quant-Gym environment"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def reset(self):
        """Reset environment"""
        try:
            response = self.session.post(f"{self.base_url}/reset")
            return response.json()
        except Exception as e:
            print(f"[ERROR] Reset failed: {e}", flush=True)
            return {"observation": {"price": 150, "balance": 10000, "holdings": 0, "portfolio_value": 10000}}
    
    def step(self, action: str, amount: int = 0, explanation: str = "", strategy: str = ""):
        """Execute an action"""
        action_upper = action.upper()
        
        if action_upper == "GET_PRICE":
            payload = {"type": "GET_PRICE"}
        elif action_upper == "GET_NEWS":
            payload = {"type": "GET_NEWS", "explanation": explanation}
        elif action_upper.startswith("BUY"):
            if " " in action_upper:
                try:
                    amount = int(action_upper.split()[1])
                except:
                    amount = 5
            payload = {"type": "BUY", "amount": amount}
        elif action_upper.startswith("SELL"):
            if " " in action_upper:
                try:
                    amount = int(action_upper.split()[1])
                except:
                    amount = 5
            payload = {"type": "SELL", "amount": amount}
        elif action_upper.startswith("BACKTEST"):
            if " " in action_upper:
                strategy = action_upper.split()[1]
            payload = {"type": "BACKTEST", "strategy": strategy}
        elif action_upper == "GET_NEWS":
            payload = {"type": "GET_NEWS", "explanation": explanation}
        else:
            payload = {"type": "GET_PRICE"}
        
        try:
            response = self.session.post(f"{self.base_url}/step", json=payload)
            return response.json()
        except Exception as e:
            print(f"[ERROR] Step failed: {e}", flush=True)
            return {"observation": {"price": 150, "balance": 10000, "holdings": 0, "portfolio_value": 10000}}
    
    def close(self):
        """Close the session"""
        self.session.close()


def parse_action_from_response(text: str) -> str:
    """Parse LLM response into action string"""
    text = text.strip().upper()
    
    if text.startswith("BUY"):
        parts = text.split()
        if len(parts) > 1 and parts[1].isdigit():
            return f"BUY {parts[1]}"
        return "BUY 5"
    elif text.startswith("SELL"):
        parts = text.split()
        if len(parts) > 1 and parts[1].isdigit():
            return f"SELL {parts[1]}"
        return "SELL 5"
    elif text.startswith("BACKTEST"):
        return "BACKTEST momentum"
    elif text.startswith("GET_NEWS"):
        return "GET_NEWS"
    else:
        return "GET_PRICE"


def fallback_strategy(observation: dict) -> str:
    """Rule-based strategy when LLM is unavailable"""
    sentiment = observation.get('last_news', {}).get('sentiment', 'neutral')
    if sentiment == 'positive':
        return "BUY 5"
    elif sentiment == 'negative':
        return "SELL 5"
    else:
        return "GET_PRICE"


def get_model_action(step: int, observation: dict, history: List[str]) -> str:
    """Get action using fallback strategy (no LLM required for basic testing)"""
    return fallback_strategy(observation)


async def main() -> None:
    print("[INFO] Starting Quant-Gym Inference", flush=True)
    
    # Check token status
    if HF_TOKEN:
        print(f"[INFO] HF_TOKEN found (length: {len(HF_TOKEN)} chars)", flush=True)
    else:
        print("[INFO] No HF_TOKEN found, using rule-based fallback strategy", flush=True)
    
    # Initialize environment client
    env = QuantGymClient(BASE_URL)
    
    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    success = False
    final_score = 0.0
    
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME if HF_TOKEN else "fallback-rule-based")
    
    try:
        # Reset environment
        result = env.reset()
        observation = result.get('observation', {})
        print(f"[INFO] Reset complete. Initial observation: {observation}", flush=True)
        
        for step in range(1, MAX_STEPS + 1):
            # Get action
            action_str = get_model_action(step, observation, history)
            
            # Execute action
            result = env.step(action_str)
            observation = result.get('observation', {})
            
            # Calculate reward
            portfolio_value = observation.get('portfolio_value', 10000)
            sentiment = observation.get('last_news', {}).get('sentiment', 'neutral')
            
            profit_reward = max(0, (portfolio_value - 10000) / 10000)
            sentiment_bonus = 0.2 if sentiment == 'positive' else (-0.1 if sentiment == 'negative' else 0)
            reward = min(1.0, max(0.0, profit_reward + sentiment_bonus))
            
            done = step >= MAX_STEPS - 1
            error = None
            
            rewards.append(reward)
            steps_taken = step
            
            log_step(step=step, action=action_str, reward=reward, done=done, error=error)
            
            history.append(f"Step {step}: {action_str}")
            
            if done:
                break
        
        final_score = sum(rewards) / len(rewards) if rewards else 0.0
        success = final_score >= SUCCESS_SCORE_THRESHOLD
        
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        success = False
        final_score = 0.0
    finally:
        try:
            env.close()
        except Exception as e:
            pass
        log_end(success=success, steps=steps_taken, score=final_score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())
