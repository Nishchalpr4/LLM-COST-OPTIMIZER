"""
Validator: Checks answer quality and decides if escalation is needed.

WHY THIS EXISTS:
- Validates that answers meet minimum quality thresholds
- Prevents returning poor answers to users
- Triggers escalation to larger models if quality is low
- Saves money by only escalating when necessary
"""

import random
import os
from groq import Groq


# Initialize Groq client
# API key is read from environment variable for security
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None


def generate_answer(question: str, model_name: str) -> str:
    """
    Generate an answer using the selected Groq model.
    
    WHY GROQ:
    - Fast and cheap inference
    - Good for cost optimization testing
    - Supports multiple models (mixtral, llama, etc.)
    - Easy to integrate
    
    Args:
        question: The user's question
        model_name: The selected model ("small" or "large")
        
    Returns:
        Generated answer as a string
    """
    
    # Map our model names to Groq model IDs
    # Available models at: https://console.groq.com/docs/models
    groq_models = {
        "small": "llama-3.1-8b-instant",     # Fast, cheap model
        "large": "llama-3.1-70b-versatile"   # More capable, higher cost
    }
    
    selected_groq_model = groq_models.get(model_name, "mixtral-8x7b-32768")
    
    # If no API key, fall back to placeholder
    if not groq_client:
        model_prefix = {
            "small": "[Mixtral-8x7b] ",
            "large": "[Mixtral-8x7b] "
        }
        
        if len(question.split()) < 10:
            return model_prefix.get(model_name, "") + f"Quick answer to: {question[:30]}... This is a concise response."
        else:
            return model_prefix.get(model_name, "") + f"Detailed answer to: {question[:50]}... " \
                   f"This response includes multiple perspectives and deeper analysis of the topic."
    
    # Call real Groq API
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ],
            model=selected_groq_model,
            max_tokens=500 if model_name == "small" else 1000,
            temperature=0.7,
        )
        
        answer = chat_completion.choices[0].message.content
        return answer
    
    except Exception as e:
        # Fallback if API call fails
        return f"Error calling Groq API: {str(e)}"


def calculate_quality_score(answer: str, question: str) -> float:
    """
    Validate answer quality using basic heuristics.
    
    Quality heuristics:
    1. Answer length: Should be proportional to question complexity
    2. Answer relevance: Simple keyword matching with question
    3. Answer completeness: Does it seem like a full response?
    
    WHY THIS APPROACH:
    - No ML model needed (fast, free)
    - Good enough for basic validation
    - Easy to understand and debug
    - Can be extended with better NLP later
    
    Args:
        answer: The generated answer
        question: The original question
        
    Returns:
        Quality score from 0.0 (poor) to 1.0 (excellent)
    """
    
    quality_score = 0.5  # Start with baseline
    
    # Check 1: Answer length should be reasonable
    answer_words = len(answer.split())
    question_words = len(question.split())
    
    if answer_words < 5:
        quality_score -= 0.3  # Too short
    elif answer_words < 20:
        quality_score -= 0.1  # Somewhat short
    elif answer_words > 100:
        quality_score += 0.2  # Good length
    
    # Check 2: Answer relevance (simple keyword matching)
    # Extract key terms from question (exclude common words)
    common_words = {"what", "is", "the", "a", "to", "of", "and", "or", "in", "how", "why", "when"}
    question_terms = [
        word.lower() for word in question.split()
        if len(word) > 3 and word.lower() not in common_words
    ]
    
    answer_lower = answer.lower()
    matching_terms = sum(1 for term in question_terms if term in answer_lower)
    
    if len(question_terms) > 0:
        relevance = matching_terms / len(question_terms)
        quality_score += (relevance * 0.3)  # Up to +0.3 for relevance
    
    # Check 3: Answer should have some structure
    if "." in answer and len(answer.split(".")) > 1:
        quality_score += 0.1  # Has multiple sentences
    
    if any(word in answer.lower() for word in ["first", "second", "third", "also", "additionally"]):
        quality_score += 0.1  # Has structure indicators
    
    # Add some randomness to simulate real-world variation
    # In production, this would be more deterministic
    quality_score += random.uniform(-0.05, 0.05)
    
    # Normalize to 0.0 - 1.0
    quality_score = max(0.0, min(1.0, quality_score))
    
    return quality_score


def should_escalate(quality_score: float, quality_threshold: float) -> bool:
    """
    Determine if answer should be escalated to a better model.
    
    WHY THIS LOGIC:
    - If quality is too low, we escalate to get a better answer
    - This ensures user satisfaction over cost savings
    - The threshold is based on the model's expected quality level
    
    Args:
        quality_score: Calculated quality score (0.0-1.0)
        quality_threshold: Minimum acceptable quality for current model
        
    Returns:
        True if should escalate, False otherwise
    """
    
    return quality_score < quality_threshold
