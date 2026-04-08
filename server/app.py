import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import AgentAction
from server.environment import TradingEnvironment
import uvicorn

app = FastAPI(title="Quant-Gym", description="Financial Analysis Environment")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = TradingEnvironment()

@app.get("/")
def root():
    return {"message": "Quant-Gym API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset():
    obs = env.reset()
    return {"status": "reset", "observation": obs.dict()}

@app.post("/step")
def step(action: AgentAction):
    try:
        observation = env.step(action)
        return {"observation": observation.dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
def get_state():
    return env.state()

@app.get("/tasks")
def get_tasks():
    return {
        "tasks": [
            {"id": "1", "name": "Fetch Market Data", "description": "Get current price for AAPL"},
            {"id": "2", "name": "News Analysis", "description": "Analyze news and recommend action with explanation"},
            {"id": "3", "name": "Backtest Strategy", "description": "Backtest a trading strategy and return risk metrics"}
        ]
    }

def main():
    """Entry point for the application"""
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=7860,
        reload=False
    )

if __name__ == "__main__":
    main()
