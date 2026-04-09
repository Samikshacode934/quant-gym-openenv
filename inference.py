import asyncio
import os
import textwrap
from typing import List, Optional
from openai import OpenAI
import requests


API_BASE_URL = os.environ.get("API_BASE_URL")
API_KEY = os.environ.get("API_KEY")

# Quant-Gym configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
TASK_NAME = os.getenv("TASK_NAME", "quant-gym")
BENCHMARK = os.getenv("BENCHMARK", "quant-gym")
MAX_STEPS = 10
TEMPERATURE = 0.7
MAX_TOKENS = 200
SUCCESS_SCORE_THRESHOLD = 0.7

# System prompt
SYSTEM_PROMPT = textwrap.dedent(
    """
    You are a financial analyst AI agent. Analyze market data and make trading decisions.
    
    Available actions:
    - GET_PRICE: Get current stock price
    - BUY [amount]: Buy number of shares
    - SELL [amount]: Sell number of shares
    - BACKTEST [strategy]: Backtest a strategy (momentum or mean_reversion)
    - GET_NEWS: Get latest news headline
    
    Respond with EXACTLY one action in format: ACTION [parameter]
    Example: BUY 10
    Example: GET_PRICE
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
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def reset(self):
        try:
            response = self.session.post(f"{self.base_url}/reset")
            return response.json()
        except Exception as e:
            print(f"[ERROR] Reset failed: {e}", flush=True)
            return {"observation": {"price": 150, "balance": 10000, "holdings": 0, "portfolio_value": 10000}}
    
    def step(self, action: str):
        action_upper = action.upper()
        
        if action_upper == "GET_PRICE":
            payload = {"type": "GET_PRICE"}
        elif action_upper.startswith("BUY"):
            amount = 5
            if " " in action_upper:
                try:
                    amount = int(action_upper.split()[1])
                except:
                    pass
            payload = {"type": "BUY", "amount": amount}
        elif action_upper.startswith("SELL"):
            amount = 5
            if " " in action_upper:
                try:
                    amount = int(action_upper.split()[1])
                except:
                    pass
            payload = {"type": "SELL", "amount": amount}
        elif action_upper.startswith("BACKTEST"):
            payload = {"type": "BACKTEST", "strategy": "momentum"}
        elif action_upper == "GET_NEWS":
            payload = {"type": "GET_NEWS", "explanation": "Analyzing market sentiment"}
        else:
            payload = {"type": "GET_PRICE"}
        
        try:
            response = self.session.post(f"{self.base_url}/step", json=payload)
            return response.json()
        except Exception as e:
            print(f"[ERROR] Step failed: {e}", flush=True)
            return {"observation": {"price": 150, "balance": 10000, "holdings": 0, "portfolio_value": 10000}}
    
    def close(self):
        self.session.close()


def get_model_action(client: OpenAI, step: int, observation: dict, history: List[str]) -> str:
    """Get action from LLM using the judge's proxy"""
    
    user_prompt = textwrap.dedent(
        f"""
        Step: {step}
        Current price: ${observation.get('price', 'unknown')}
        Balance: ${observation.get('balance', 'unknown')}
        Holdings: {observation.get('holdings', 0)} shares
        Portfolio value: ${observation.get('portfolio_value', 'unknown')}
        Latest news: {observation.get('last_news', {}).get('headline', 'No news')}
        
        What is your next action? (BUY X, SELL X, GET_PRICE, BACKTEST, or GET_NEWS)
        """
    ).strip()
    
    try:
        # CRITICAL: This MUST go through their proxy using BOTH env vars
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Their proxy expects this
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        text = completion.choices[0].message.content or ""
        return parse_action_from_response(text)
    except Exception as e:
        print(f"[DEBUG] LLM error: {e}, using fallback", flush=True)
        return fallback_strategy(observation)


def parse_action_from_response(text: str) -> str:
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
        return "BACKTEST"
    elif text.startswith("GET_NEWS"):
        return "GET_NEWS"
    else:
        return "GET_PRICE"


def fallback_strategy(observation: dict) -> str:
    sentiment = observation.get('last_news', {}).get('sentiment', 'neutral')
    if sentiment == 'positive':
        return "BUY 5"
    elif sentiment == 'negative':
        return "SELL 5"
    else:
        return "GET_PRICE"


async def main() -> None:
    print("[INFO] Starting Quant-Gym Inference", flush=True)
    
    # CRITICAL CHECK: Both environment variables MUST be set
    if not API_BASE_URL:
        print("[ERROR] API_BASE_URL environment variable not set!", flush=True)
        print("[ERROR] This must be provided by the hackathon judge.", flush=True)
        return
    
    if not API_KEY:
        print("[ERROR] API_KEY environment variable not set!", flush=True)
        print("[ERROR] This must be provided by the hackathon judge.", flush=True)
        return
    
    print(f"[INFO] Using API_BASE_URL: {API_BASE_URL}", flush=True)
    
    # Initialize OpenAI client with judge's proxy - MUST use BOTH
    client = OpenAI(
        base_url=API_BASE_URL,  # Their proxy URL
        api_key=API_KEY,        # Their API key
    )
    
    env = QuantGymClient(BASE_URL)
    
    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    success = False
    final_score = 0.0
    
    log_start(task=TASK_NAME, env=BENCHMARK, model="gpt-3.5-turbo")
    
    try:
        result = env.reset()
        observation = result.get('observation', {})
        
        for step in range(1, MAX_STEPS + 1):
            action_str = get_model_action(client, step, observation, history)
            
            result = env.step(action_str)
            observation = result.get('observation', {})
            
            portfolio_value = observation.get('portfolio_value', 10000)
            profit_reward = max(0, (portfolio_value - 10000) / 10000)
            reward = min(1.0, max(0.0, profit_reward))
            
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
        except:
            pass
        log_end(success=success, steps=steps_taken, score=final_score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())
