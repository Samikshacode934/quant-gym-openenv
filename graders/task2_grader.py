def grade_task2(agent_action, observation):
    """Task 2: News Analysis with Explanation"""
    score = 0.0
    
    # Check if agent gave explanation
    if agent_action.explanation and len(agent_action.explanation) > 10:
        score += 0.5
    
    # Check if recommendation exists
    if agent_action.type in ["BUY", "SELL", "HOLD"]:
        score += 0.5
    
    return score
