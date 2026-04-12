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

# System prompt for financial analysis
SYSTEM_PROMPT = textwrap.dedent(
    """
    It is a financial analyst AI agent. It's goal is to analyze market data and make trading decisions.
    
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
    
    For GET_NEWS, also provide a brief explanation of your analysis.
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
            payload = {"type": "GET_NEWS", "explanation": explanation if explanation else "Analyzing market sentiment"}
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
            payload = {"type": "BACKTEST", "strategy": strategy if strategy else "momentum"}
        else:
            payload = {"type": "GET_PRICE"}
        
        try:
            response = self.session.post(f"{self.base_url}/step", json=payload)
            return response.json()
        except Exception as e:
            print(f"[ERROR] Step failed: {e}", flush=True)
            return {"observation": {"price": 150, "balance": 10000, "holdings": 0, "portfolio_value": 10000}}
    
    def get_tasks(self):
        """Get available tasks"""
        try:
            response = self.session.get(f"{self.base_url}/tasks")
            return response.json()
        except Exception as e:
            print(f"[ERROR] Get tasks failed: {e}", flush=True)
            return {"tasks": []}
    
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
        parts = text.split()
        if len(parts) > 1:
            return f"BACKTEST {parts[1]}"
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


def get_model_action(client: OpenAI, step: int, observation: dict, history: List[str]) -> str:
    """Get action from LLM using the judge's proxy"""
    
    # If no API credentials, use fallback
    if not API_BASE_URL or not API_KEY:
        print("[DEBUG] No API credentials, using fallback strategy", flush=True)
        return fallback_strategy(observation)
    
    # Get news headline for context
    news = observation.get('last_news', {})
    headline = news.get('headline', 'No recent news')
    sentiment = news.get('sentiment', 'neutral')
    
    user_prompt = textwrap.dedent(
        f"""
        Step: {step} of {MAX_STEPS}
        
        Current Market Data:
        - Price: ${observation.get('price', 'unknown')}
        - Balance: ${observation.get('balance', 'unknown')}
        - Holdings: {observation.get('holdings', 0)} shares
        - Portfolio Value: ${observation.get('portfolio_value', 'unknown')}
        
        Latest News:
        - Headline: "{headline}"
        - Sentiment: {sentiment}
        
        Previous actions this episode:
        {chr(10).join(history[-5:]) if history else "No previous actions"}
        
        Based on this information, what is your next action?
        Respond with EXACTLY one action in format: ACTION [parameter]
        Examples: BUY 10, SELL 5, GET_PRICE, BACKTEST momentum, GET_NEWS
        """
    ).strip()
    
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        text = completion.choices[0].message.content or ""
        action = parse_action_from_response(text)
        print(f"[DEBUG] LLM suggested: {text[:100]}... -> {action}", flush=True)
        return action
    except Exception as e:
        print(f"[DEBUG] LLM error: {e}, using fallback", flush=True)
        return fallback_strategy(observation)


def calculate_reward(observation: dict, step: int) -> float:
    """Calculate reward based on portfolio performance and actions"""
    portfolio_value = observation.get('portfolio_value', 10000)
    price = observation.get('price', 150)
    
    # Profit reward (0 to 0.6)
    profit_reward = max(0, (portfolio_value - 10000) / 10000) * 0.6
    
    # News sentiment bonus (0 to 0.2)
    sentiment = observation.get('last_news', {}).get('sentiment', 'neutral')
    if sentiment == 'positive':
        sentiment_bonus = 0.2
    elif sentiment == 'negative':
        sentiment_bonus = -0.1
    else:
        sentiment_bonus = 0.05
    
    # Step completion bonus (0 to 0.2)
    step_bonus = min(0.2, step / MAX_STEPS * 0.2)
    
    reward = max(0.0, min(1.0, profit_reward + sentiment_bonus + step_bonus))
    return reward


async def main() -> None:
    print("[INFO] Starting Quant-Gym Inference", flush=True)
    print(f"[INFO] Python version: {os.sys.version}", flush=True)
    
    # CRITICAL CHECK: Both environment variables MUST be set
    if not API_BASE_URL:
        print("[WARNING] API_BASE_URL environment variable not set!", flush=True)
        print("[WARNING] Using fallback strategy without LLM.", flush=True)
    else:
        print(f"[INFO] API_BASE_URL: {API_BASE_URL}", flush=True)
    
    if not API_KEY:
        print("[WARNING] API_KEY environment variable not set!", flush=True)
        print("[WARNING] Using fallback strategy without LLM.", flush=True)
    
    # Initialize OpenAI client if credentials available
    client = None
    if API_BASE_URL and API_KEY:
        try:
            client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
            print("[INFO] OpenAI client initialized successfully", flush=True)
        except Exception as e:
            print(f"[WARNING] Failed to initialize OpenAI client: {e}", flush=True)
    
    env = QuantGymClient(BASE_URL)
    
    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    success = False
    final_score = 0.0
    
    log_start(task=TASK_NAME, env=BENCHMARK, model="gpt-3.5-turbo" if client else "fallback-rule-based")
    
    try:
        # Reset environment
        result = env.reset()
        observation = result.get('observation', {})
        print(f"[INFO] Reset complete. Initial price: ${observation.get('price', 'unknown')}", flush=True)
        
        for step in range(1, MAX_STEPS + 1):
            # Get action from LLM or fallback
            if client:
                action_str = get_model_action(client, step, observation, history)
            else:
                action_str = fallback_strategy(observation)
            
            # Execute action
            result = env.step(action_str)
            observation = result.get('observation', {})
            
            # Calculate reward
            reward = calculate_reward(observation, step)
            
            done = step >= MAX_STEPS - 1
            error = None
            
            rewards.append(reward)
            steps_taken = step
            
            log_step(step=step, action=action_str, reward=reward, done=done, error=error)
            
            # Update history
            history.append(f"Step {step}: {action_str} -> reward {reward:.2f}")
            
            if done:
                break
        
        final_score = sum(rewards) / len(rewards) if rewards else 0.0
        success = final_score >= SUCCESS_SCORE_THRESHOLD
        
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        import traceback
        traceback.print_exc()
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
