def grade_task2(agent_action, observation):
    
    score = 0.0
    
    # Check if agent gave an explanation (0.01 to 0.49 range)
    explanation = agent_action.get("explanation", "")
    if explanation and len(explanation) > 10:
        score += 0.45
    
    # Check if action type is valid (BUY/SELL/GET_NEWS)
    action_type = agent_action.get("type", "")
    if action_type in ["BUY", "SELL", "GET_NEWS", "HOLD"]:
        score += 0.45
    
    # Check if news sentiment was considered
    sentiment = observation.get("last_news", {}).get("sentiment", "")
    if sentiment in ["positive", "negative", "neutral"]:
        score += 0.05
    
    # Ensure score is never 0.0 or 1.0
    if score == 0.0:
        score = 0.01
    elif score >= 0.99:
        score = 0.98
    
    return round(score, 2)
