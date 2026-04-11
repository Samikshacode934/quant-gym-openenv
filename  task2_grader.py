def grade_task2(action, observation):
    """
    Task 2: News Sentiment Analysis
    Returns score based on explanation quality
    """
    score = 0.75
    
    # Check if agent provided explanation
    if action and action.get('explanation'):
        explanation = action.get('explanation', '')
        if len(explanation) > 20:
            score = 0.95
        elif len(explanation) > 10:
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
