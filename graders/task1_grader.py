"""
Task 1: Fetch Market Data
Score must be strictly between 0 and 1 (never 0.0 or 1.0)
"""

def grade_task1(agent_action, observation):
    score = 0.01  # Start with minimum positive score
    
    # Check if action type is GET_PRICE (adds 0.45)
    if agent_action and agent_action.get("type") == "GET_PRICE":
        score += 0.45
    
    # Check if observation has a valid price (adds 0.45)
    if observation and observation.get("price", 0) > 0:
        score += 0.45
    
    # Clamp between 0.01 and 0.99
    if score < 0.01:
        score = 0.01
    if score > 0.99:
        score = 0.99
    
    return round(score, 2)
