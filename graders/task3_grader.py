def grade_task3(agent_action, observation):
    
    score = 0.0
    
    # Check if backtest results exist (0.01 to 0.49 range)
    backtest_results = observation.get("backtest_results")
    if backtest_results:
        score += 0.45
    
    # Check for Sharpe ratio (0.01 to 0.49 range)
    sharpe = backtest_results.get("sharpe_ratio", 0) if backtest_results else 0
    if sharpe > 0:
        score += 0.45
    
    # Small bonus for reasonable drawdown
    drawdown = backtest_results.get("max_drawdown", 1) if backtest_results else 1
    if drawdown < 0.5:
        score += 0.05
    
    # Ensure score is never 0.0 or 1.0
    if score == 0.0:
        score = 0.01
    elif score >= 0.99:
        score = 0.98
    
    return round(score, 2)
