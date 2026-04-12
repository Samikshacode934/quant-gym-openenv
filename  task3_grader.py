def grade_task3(action, observation):
    """
    Task 3: Backtest Strategy
    Grades: Strategy sophistication, risk awareness, completeness
    """
    score = 0.0
    
    # Get backtest results
    backtest_results = observation.get("backtest_results", {}) if observation else {}
    
    # 1. Check if backtest was performed (0-0.3 points)
    if backtest_results:
        score += 0.3
    
    # 2. Check Sharpe ratio (0-0.3 points)
    sharpe = backtest_results.get("sharpe_ratio", 0)
    if sharpe > 1.5:
        score += 0.3
    elif sharpe > 1.0:
        score += 0.25
    elif sharpe > 0.5:
        score += 0.15
    elif sharpe > 0:
        score += 0.05
    
    # 3. Check max drawdown (0-0.2 points)
    drawdown = backtest_results.get("max_drawdown", 1)
    if drawdown < 0.1:
        score += 0.2
    elif drawdown < 0.2:
        score += 0.15
    elif drawdown < 0.3:
        score += 0.1
    elif drawdown < 0.5:
        score += 0.05
    
    # 4. Check strategy description (0-0.2 points)
    strategy = action.get("strategy", "") if action else ""
    if strategy:
        score += 0.1
        # Sophisticated strategy names get bonus
        advanced_strategies = ['momentum', 'mean reversion', 'arbitrage', 'pair trading', 'options']
        if any(s in strategy.lower() for s in advanced_strategies):
            score += 0.1
    
    # Ensure score is strictly between 0 and 1
    score = max(0.01, min(0.99, score))
    
    return round(score, 2)
