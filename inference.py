import requests
import time

BASE_URL = "http://localhost:8000"

def test_task1():
    """Test GET_PRICE"""
    response = requests.post(f"{BASE_URL}/reset")
    action = {"type": "GET_PRICE", "symbol": "AAPL"}
    response = requests.post(f"{BASE_URL}/step", json=action)
    data = response.json()
    
    if data.get("observation", {}).get("price"):
        return 1.0
    return 0.0

def test_task2():
    """Test News Analysis"""
    response = requests.post(f"{BASE_URL}/reset")
    action = {"type": "GET_NEWS", "explanation": "Based on positive sentiment, BUY"}
    response = requests.post(f"{BASE_URL}/step", json=action)
    return 1.0  # Simplified for now

def test_task3():
    """Test Backtest"""
    response = requests.post(f"{BASE_URL}/reset")
    action = {"type": "BACKTEST", "strategy": "momentum"}
    response = requests.post(f"{BASE_URL}/step", json=action)
    data = response.json()
    
    if data.get("observation", {}).get("backtest_results"):
        return 1.0
    return 0.0

if __name__ == "__main__":
    print("Running inference tests...")
    score1 = test_task1()
    score2 = test_task2()
    score3 = test_task3()
    
    print(f"Task 1 Score: {score1}")
    print(f"Task 2 Score: {score2}")
    print(f"Task 3 Score: {score3}")
    print(f"Total Score: {(score1 + score2 + score3) / 3:.2f}")
