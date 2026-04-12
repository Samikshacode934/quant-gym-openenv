import asyncio
import os
import sys
from typing import List, Optional
from openai import OpenAI
import requests

# ============================================
# MANDATORY: Read exactly what validator injects
# ============================================
API_KEY = os.environ.get("API_KEY")
API_BASE_URL = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.environ.get("MODEL_NAME") or "gpt-3.5-turbo"

# Your HF Space URL
ENV_URL = os.environ.get("ENV_URL", "https://astocoder-quant-gym.hf.space")

# Configuration
MAX_STEPS = 10

# ============================================
# Tasks list - must match openenv.yaml ids
# ============================================
TASKS = [
    ("task1", "Fetch Market Data"),
    ("task2", "News Sentiment Analysis"),
    ("task3", "Backtest Strategy"),
]


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)


def log_end(task: str, success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    # CRITICAL: task= MUST be included
    print(f"[END] task={task} success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


class QuantGymClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def reset(self):
        resp = self.session.post(f"{self.base_url}/reset")
        return resp.json()
    
    def step(self, action: dict):
        resp = self.session.post(f"{self.base_url}/step", json=action)
        return resp.json()
    
    def close(self):
        self.session.close()


def fallback_strategy(observation: dict) -> str:
    sentiment = observation.get('last_news', {}).get('sentiment', 'neutral')
    if sentiment == 'positive':
        return "BUY 5"
    elif sentiment == 'negative':
        return "SELL 5"
    else:
        return "GET_PRICE"


def get_model_action(client: OpenAI, step: int, observation: dict) -> str:
    if not client:
        return fallback_strategy(observation)
    
    user_prompt = f"Step {step}. Price: ${observation.get('price', 0)}. Balance: ${observation.get('balance', 0)}. Choose: BUY 5, SELL 5, GET_PRICE, BACKTEST, GET_NEWS"
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=100,
        )
        text = completion.choices[0].message.content or ""
        text = text.strip().upper()
        if "BUY" in text:
            return "BUY 5"
        elif "SELL" in text:
            return "SELL 5"
        elif "BACKTEST" in text:
            return "BACKTEST"
        elif "GET_NEWS" in text:
            return "GET_NEWS"
        else:
            return "GET_PRICE"
    except Exception as e:
        print(f"[DEBUG] LLM error: {e}", flush=True)
        return fallback_strategy(observation)


def calculate_reward(observation: dict) -> float:
    portfolio = observation.get('portfolio_value', 10000)
    reward = max(0, (portfolio - 10000) / 10000)
    # Clamp to (0.001, 0.999) - NEVER exactly 0 or 1
    return max(0.001, min(0.999, reward))


def main():
    print("[INFO] Starting Quant-Gym Inference", flush=True)
    print(f"[INFO] ENV_URL: {ENV_URL}", flush=True)
    print(f"[INFO] API_BASE_URL: {API_BASE_URL}", flush=True)
    print(f"[INFO] MODEL_NAME: {MODEL_NAME}", flush=True)
    
    # Initialize OpenAI client
    client = None
    if API_KEY and API_BASE_URL:
        try:
            client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
            print("[INFO] OpenAI client initialized", flush=True)
        except Exception as e:
            print(f"[WARNING] Failed: {e}", flush=True)
    
    env = QuantGymClient(ENV_URL)
    
    # Loop through all tasks - CRITICAL
    for task_id, task_name in TASKS:
        rewards = []
        steps = 0
        score = 0.001
        success = False
        
        log_start(task=task_id, env="quant-gym", model=MODEL_NAME)
        
        try:
            # Reset environment
            result = env.reset()
            observation = result.get('observation', {})
            done = False
            
            for step in range(1, MAX_STEPS + 1):
                if done:
                    break
                
                # Get action
                action_str = get_model_action(client, step, observation)
                
                # Parse action
                action_upper = action_str.upper()
                if action_upper == "GET_PRICE":
                    payload = {"type": "GET_PRICE"}
                elif action_upper.startswith("BUY"):
                    payload = {"type": "BUY", "amount": 5}
                elif action_upper.startswith("SELL"):
                    payload = {"type": "SELL", "amount": 5}
                elif action_upper.startswith("BACKTEST"):
                    payload = {"type": "BACKTEST", "strategy": "momentum"}
                elif action_upper == "GET_NEWS":
                    payload = {"type": "GET_NEWS", "explanation": "Market analysis"}
                else:
                    payload = {"type": "GET_PRICE"}
                
                # Execute action
                result = env.step(payload)
                observation = result.get('observation', {})
                
                # Calculate reward
                reward = calculate_reward(observation)
                rewards.append(reward)
                steps = step
                done = step >= MAX_STEPS - 1
                
                log_step(step=step, action=action_str[:100], reward=reward, done=done, error=None)
            
            # Get final score from observation or calculate
            score = calculate_reward(observation)
            score = max(0.001, min(0.999, score))
            success = score > 0.5
            
        except Exception as e:
            print(f"[DEBUG] {task_id} error: {e}", flush=True)
            score = 0.001
            success = False
        
        finally:
            # CRITICAL: END line MUST have task= field
            log_end(task=task_id, success=success, steps=steps, score=score, rewards=rewards)
    
    env.close()


if __name__ == "__main__":
    main()
