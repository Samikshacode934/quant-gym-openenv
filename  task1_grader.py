def grade_task1(action, observation):
    """
    Task 1: Fetch Market Data
    Returns score based on whether price was retrieved
    """
    score = 0.75  # Base score
    
    # Check if observation has a price
    if observation and observation.get('price', 0) > 0:
        score = 0.95
    else:
        score = 0.55
    
    # Ensure score is never 0.0 or 1.0
    if score <= 0.0:
        score = 0.01
    if score >= 1.0:
        score = 0.99
    
    return score
