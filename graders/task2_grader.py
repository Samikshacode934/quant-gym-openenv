"""
Task 2: News Sentiment Analysis
Score must be strictly between 0 and 1 (never 0.0 or 1.0)
"""

def grade_task2(agent_action, observation):
    score = 0.01  # Start with minimum positive score
    
    # Check if agent provided an explanation
    if agent_action and agent_action.get("explanation"):
        explanation = agent_action.get("explanation", "")
        if len(explanation) > 10:
            score += 0.30
    
    # Check if action type is valid (BUY/SELL/HOLD/GET_NEWS)
    if agent_action:
        action_type = agent_action.get("type", "")
        if action_type in ["BUY", "SELL", "HOLD", "GET_NEWS"]:
            score += 0.30
    
    # Check if news sentiment was analyzed
    if observation and observation.get("last_news"):
        sentiment = observation.get("last_news", {}).get("sentiment", "")
        if sentiment in ["positive", "negative", "neutral"]:
            score += 0.35
    
    # Clamp between 0.01 and 0.99
    if score < 0.01:
        score = 0.01
    if score > 0.99:
        score = 0.99
    
    return round(score, 2)
