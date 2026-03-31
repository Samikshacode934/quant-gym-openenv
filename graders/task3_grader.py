def grade_task3(backtest_results):
    """Task 3: Backtest Strategy"""
    score = 0.0
    
    if backtest_results:
        if backtest_results.get("sharpe_ratio", 0) > 0:
            score += 0.5
        if backtest_results.get("max_drawdown", 1) < 0.5:
            score += 0.5
    
    return score
