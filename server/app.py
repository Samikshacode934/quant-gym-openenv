from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

prices = [150.00, 152.50, 151.75, 153.25, 155.00]
cash = 10000.00
shares = 0
step_num = 0

class Action(BaseModel):
    action: str
    amount: Optional[int] = 0

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/")
def root():
    return {"message": "Trading API Running"}

@app.post("/reset")
def reset():
    global cash, shares, step_num
    cash = 10000.00
    shares = 0
    step_num = 0
    return {"cash": cash, "shares": shares, "price": prices[0]}

@app.post("/step")
def step(action: Action):
    global cash, shares, step_num
    step_num = min(step_num + 1, len(prices) - 1)
    price = prices[step_num]
    
    if action.action == "BUY" and action.amount:
        cost = price * action.amount
        if cost <= cash:
            cash -= cost
            shares += action.amount
    elif action.action == "SELL" and action.amount:
        if action.amount <= shares:
            cash += price * action.amount
            shares -= action.amount
    
    return {
        "price": price,
        "cash": cash,
        "shares": shares,
        "portfolio_value": cash + (shares * price)
    }

@app.get("/tasks")
def tasks():
    return {
        "tasks": [
            {"id": 1, "name": "Get Price"},
            {"id": 2, "name": "Buy Stock"},
            {"id": 3, "name": "Sell Stock"}
        ]
    }