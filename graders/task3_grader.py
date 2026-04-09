"""
Task 3: Backtest Strategy
Score must be strictly between 0 and 1 (never 0.0 or 1.0)
"""

def grade_task3(agent_action, observation):
    score = 0.01  # Start with minimum positive score
    
    # Check if backtest results exist
    if observation and observation.get("backtest_results"):
        backtest_results = observation.get("backtest_results", {})
        score += 0.45
        
        # Check for Sharpe ratio
        sharpe = backtest_results.get("sharpe_ratio", 0)
        if sharpe > 0:
            score += 0.25
        
        # Check for max drawdown
        drawdown = backtest_results.get("max_drawdown", 1)
        if drawdown < 0.5:
            score += 0.25
    
    # Clamp between 0.01 and 0.99
    if score < 0.01:
        score = 0.01
    if score > 0.99:
        score = 0.99
    
    return round(score, 2)
