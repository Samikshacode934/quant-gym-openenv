def grade_task2(action, observation):
    """
    Task 2: News Sentiment Analysis with Explanation
    Grades: Quality of reasoning, financial knowledge, clarity
    This is your unique innovation!
    """
    score = 0.0
    
    # Get the agent's explanation
    explanation = action.get('explanation', '') if action else ''
    
    # 1. Check explanation length and detail (0-0.3 points)
    if len(explanation) > 100:
        score += 0.3
    elif len(explanation) > 50:
        score += 0.2
    elif len(explanation) > 20:
        score += 0.1
    else:
        score += 0.02
    
    # 2. Check for financial terminology (0-0.3 points)
    financial_terms = [
        'pe', 'p/e', 'valuation', 'earnings',
        'moving average', 'trend', 'momentum', 'rsi',
        'support', 'resistance', 'breakout',
        'risk', 'volatility', 'drawdown', 'sharpe',
        'sentiment', 'market cap', 'liquidity'
    ]
    terms_found = sum(1 for term in financial_terms if term in explanation.lower())
    score += min(0.3, terms_found * 0.05)
    
    # 3. Check for logical reasoning (0-0.2 points)
    reasoning_words = ['because', 'therefore', 'since', 'due to', 'based on', 'as a result']
    if any(word in explanation.lower() for word in reasoning_words):
        score += 0.2
    
    # 4. Check for specific data references (0-0.1 points)
    import re
    if re.search(r'\d+', explanation):  # Contains numbers
        score += 0.05
    if '%' in explanation:
        score += 0.05
    
    # 5. Check if recommendation is clear (0-0.1 points)
    recommendations = ['buy', 'sell', 'hold', 'accumulate', 'reduce']
    if any(word in explanation.lower() for word in recommendations):
        score += 0.1
    
    # Ensure score is strictly between 0 and 1
    score = max(0.01, min(0.99, score))
    
    return round(score, 2)
