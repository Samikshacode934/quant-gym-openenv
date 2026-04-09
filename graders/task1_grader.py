def grade_task1(agent_action, observation):
    
    score = 0.0
    
    # Check if action was GET_PRICE (0.01 to 0.49 range)
    if agent_action.get("type") == "GET_PRICE":
        score += 0.45  # Not 0.5 to avoid exactly 0.5
    
    # Check if observation has a valid price (0.01 to 0.49 range)
    price = observation.get("price", 0)
    if price > 0:
        score += 0.45  # Not 0.5 to avoid exactly 0.5
    
    # Ensured score is never 0.0 or 1.0
    if score == 0.0:
        score = 0.01  # Minimum positive score
    elif score >= 0.99:
        score = 0.98  # Maximum score below 1.0
    
    return round(score, 2)
