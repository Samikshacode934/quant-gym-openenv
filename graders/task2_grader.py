def grade_task2(agent_action, observation):
    """Grade Task 2: News Sentiment Analysis"""
    score = 0.0
    
    # Check if agent gave an explanation
    if agent_action.get("explanation") and len(agent_action.get("explanation", "")) > 10:
        score += 0.5
    
    # Check if action is valid (BUY/SELL/HOLD recommendation)
    action_type = agent_action.get("type", "")
    if action_type in ["BUY", "SELL", "GET_NEWS"]:
        score += 0.5
    
    return score
