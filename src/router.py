"""
Router: Estimates question difficulty and routes to appropriate LLM.

WHY THIS EXISTS:
- Reduces costs by sending simple questions to cheaper small models
- Sends complex questions to powerful large models that can handle them
- Uses simple heuristics to avoid overhead of complex ML models
"""


def estimate_difficulty(question: str) -> float:
    """
    Estimate question difficulty using simple heuristics.
    
    Heuristics used:
    1. Question length: Longer = more complex
    2. Keyword indicators: "how", "why", "explain" = higher difficulty
    3. Question type: Multiple parts, technical terms = higher difficulty
    
    Args:
        question: The user's question as a string
        
    Returns:
        Difficulty score from 0.0 (trivial) to 1.0 (very complex)
    """
    
    # Initialize difficulty score
    difficulty = 0.0
    
    # Heuristic 1: Length indicator
    # Longer questions often indicate more complex topics
    question_length = len(question.split())
    if question_length < 5:
        difficulty += 0.1  # Very short, likely simple
    elif question_length < 15:
        difficulty += 0.3  # Medium, average difficulty
    elif question_length < 30:
        difficulty += 0.5  # Longer, more complex
    else:
        difficulty += 0.7  # Very long, likely complex
    
    # Heuristic 2: Keyword indicators
    # Complex questions often use words like "explain", "how", "why", "analyze"
    complex_keywords = [
        "explain", "how", "why", "analyze", "compare", "contrast",
        "evaluate", "summarize", "discuss", "implement", "design",
        "algorithm", "complex", "optimization", "technical"
    ]
    
    question_lower = question.lower()
    keyword_count = sum(1 for keyword in complex_keywords if keyword in question_lower)
    difficulty += (keyword_count * 0.1)
    
    # Heuristic 3: Special characters and punctuation
    # Questions with multiple parts (semicolons, commas) are more complex
    if "?" in question:
        if question.count("?") > 1:
            difficulty += 0.15  # Multiple questions
    
    if ";" in question or question.count(",") > 3:
        difficulty += 0.1  # Multiple parts
    
    # Normalize difficulty to 0.0 - 1.0 range
    difficulty = min(difficulty, 1.0)
    
    return difficulty


def select_model(difficulty_score: float) -> str:
    """
    Route to the appropriate model based on difficulty.
    
    WHY THIS LOGIC:
    - Small model (cheaper, faster) for difficulty < 0.5
    - Large model (expensive, more capable) for difficulty >= 0.5
    - This is a simple threshold but can be tuned based on cost/performance needs
    
    Args:
        difficulty_score: Difficulty score from 0.0 to 1.0
        
    Returns:
        Model name: "small" or "large"
    """
    
    if difficulty_score < 0.5:
        return "small"
    else:
        return "large"


def get_model_config(model_name: str) -> dict:
    """
    Get configuration parameters for the selected model.
    
    WHY THIS EXISTS:
    - Centralized config for model parameters (cost, latency, etc.)
    - Easy to update pricing or latency estimates in one place
    - Makes it easy to add new models
    
    Args:
        model_name: Name of the model ("small" or "large")
        
    Returns:
        Dictionary with model configuration (cost, latency, etc.)
    """
    
    # Model configurations (estimated values for demonstration)
    # In production, these would come from actual provider APIs
    models = {
        "small": {
            "name": "GPT-3.5-mini",
            "cost_per_1k_tokens": 0.0005,  # $0.0005 per 1k tokens
            "avg_latency_ms": 500,         # ~500ms average
            "max_tokens": 2048,
            "quality_threshold": 0.7       # Minimum quality score before escalation
        },
        "large": {
            "name": "GPT-4",
            "cost_per_1k_tokens": 0.015,   # $0.015 per 1k tokens
            "avg_latency_ms": 2000,        # ~2000ms average
            "max_tokens": 4096,
            "quality_threshold": 0.95      # Higher quality expected
        }
    }
    
    return models.get(model_name, models["small"])
