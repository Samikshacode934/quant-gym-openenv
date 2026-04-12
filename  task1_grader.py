def grade_task1(action, observation):
    """
    Task 1: Fetch Market Data
    Grades: Speed, accuracy, and completeness of data retrieval
    """
    score = 0.0
    
    # Check if action was GET_PRICE (0-0.3 points)
    if action and action.get("type") == "GET_PRICE":
        score += 0.3
    
    # Check if price exists and is reasonable (0-0.4 points)
    price = observation.get("price", 0) if observation else 0
    if price > 0:
        # Price accuracy - closer to expected range is better
        if 100 < price < 200:  # Apple's typical range
            score += 0.3
        else:
            score += 0.2
        score += 0.1  # Bonus for having any price
    
    # Check if timestamp is provided (0-0.2 points)
    timestamp = observation.get("timestamp", "") if observation else ""
    if timestamp and len(timestamp) > 0:
        score += 0.15
    
    # Bonus for getting additional data (0-0.1 points)
    if observation and observation.get("volume"):
        score += 0.05
    if observation and observation.get("high") and observation.get("low"):
        score += 0.05
    
    # Ensure score is strictly between 0 and 1
    score = max(0.01, min(0.99, score))
    
    return round(score, 2)
