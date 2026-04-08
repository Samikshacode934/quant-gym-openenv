def grade_task3(agent_action, observation):
    """Grade Task 3: Backtest Strategy"""
    score = 0.0
    
    # Check if backtest results exist
    backtest_results = observation.get("backtest_results")
    if backtest_results:
        # Check for Sharpe ratio
        if backtest_results.get("sharpe_ratio", 0) > 0:
            score += 0.5
        # Check for max drawdown
        if backtest_results.get("max_drawdown", 1) < 1:
            score += 0.5
    
    return score
