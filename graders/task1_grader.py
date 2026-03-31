def grade_task1(agent_action, observation):
    """Task 1: Fetch Market Data"""
    score = 0.0
    
    # Check if agent requested price
    if agent_action.type == "GET_PRICE":
        score += 0.5
    
    # Check if observation has price
    if observation.price > 0:
        score += 0.5
    
    return score
