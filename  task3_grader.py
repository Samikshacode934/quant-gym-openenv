def grade_task3(action, observation):
    """
    Task 3: Backtest Strategy
    Returns score based on backtest results
    """
    score = 0.75
    
    # Check if backtest results exist
    if observation and observation.get('backtest_results'):
        results = observation.get('backtest_results', {})
        if results.get('sharpe_ratio', 0) > 1.0:
            score = 0.95
        elif results.get('sharpe_ratio', 0) > 0.5:
            score = 0.85
        else:
            score = 0.65
    else:
        score = 0.55
    
    if score <= 0.0:
        score = 0.01
    if score >= 1.0:
        score = 0.99
    
    return score
