"""
Logger: Records model usage, costs, and latency to CSV.

WHY THIS EXISTS:
- Tracks which models are used for which questions
- Calculates estimated costs (for cost optimization)
- Measures latency (for performance tracking)
- Enables analysis of routing decisions
- Provides audit trail for debugging
"""

import csv
import os
import time
from datetime import datetime


def log_result(
    question: str,
    initial_model: str,
    final_model: str,
    answer: str,
    quality_score: float,
    escalated: bool,
    latency_ms: float,
    estimated_cost: float,
    output_file: str = "output/optimizer_log.csv"
) -> None:
    """
    Log the result of a question to CSV file.
    
    WHY CSV FORMAT:
    - Simple, human-readable format
    - Easy to analyze in Excel, Python, etc.
    - No database setup required
    - Can be imported into analytics tools
    - Beginner-friendly
    
    Args:
        question: The original question
        initial_model: Model selected by router
        final_model: Model actually used (may differ if escalated)
        answer: The generated answer
        quality_score: Calculated quality score
        escalated: Whether escalation occurred
        latency_ms: Total latency in milliseconds
        estimated_cost: Estimated cost in dollars
        output_file: Path to output CSV file
    """
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Prepare row data
    row = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "question_length": len(question.split()),
        "initial_model": initial_model,
        "final_model": final_model,
        "escalated": "Yes" if escalated else "No",
        "quality_score": f"{quality_score:.2f}",
        "latency_ms": f"{latency_ms:.0f}",
        "estimated_cost_usd": f"{estimated_cost:.6f}",
        "answer_preview": answer[:100] + "..." if len(answer) > 100 else answer
    }
    
    # Check if file exists (to know if we need to write headers)
    file_exists = os.path.isfile(output_file)
    
    # Write to CSV
    try:
        with open(output_file, "a", newline="", encoding="utf-8") as csvfile:
            fieldnames = row.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header only if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write the data row
            writer.writerow(row)
        
        print(f"✓ Logged to {output_file}")
    
    except IOError as e:
        print(f"✗ Error writing to {output_file}: {e}")


def calculate_cost(model_name: str, answer_length: int, model_config: dict) -> float:
    """
    Estimate the cost of generating an answer.
    
    WHY ESTIMATE:
    - Real costs depend on token count, which requires tokenization
    - For simplicity, we estimate based on answer length
    - In production, use actual token counts from the API
    
    Formula:
    - Tokens ≈ words / 1.3 (rough estimation)
    - Cost = (tokens / 1000) * cost_per_1k_tokens
    
    Args:
        model_name: Name of the model used
        answer_length: Length of generated answer in words
        model_config: Model configuration dictionary
        
    Returns:
        Estimated cost in USD
    """
    
    # Rough token estimation: ~1.3 words per token on average
    estimated_tokens = answer_length / 1.3
    
    # Get model cost
    cost_per_1k_tokens = model_config.get("cost_per_1k_tokens", 0.001)
    
    # Calculate total cost
    total_cost = (estimated_tokens / 1000) * cost_per_1k_tokens
    
    return total_cost


def estimate_latency(model_name: str, model_config: dict) -> float:
    """
    Estimate latency for the API call.
    
    WHY ESTIMATE:
    - Real latency varies based on load, network, etc.
    - For demo purposes, use average latency from config
    - Add some randomness to simulate real-world variation
    
    Args:
        model_name: Name of the model used
        model_config: Model configuration dictionary
        
    Returns:
        Estimated latency in milliseconds
    """
    
    import random
    
    base_latency = model_config.get("avg_latency_ms", 1000)
    
    # Add ±30% randomness to simulate real variation
    variation = random.uniform(0.7, 1.3)
    estimated_latency = base_latency * variation
    
    return estimated_latency


def get_summary_stats(output_file: str = "output/optimizer_log.csv") -> dict:
    """
    Calculate summary statistics from the log file.
    
    WHY THIS FUNCTION:
    - Helps understand optimizer performance
    - Shows cost savings from routing
    - Identifies patterns in escalations
    
    Args:
        output_file: Path to the CSV log file
        
    Returns:
        Dictionary with summary statistics
    """
    
    if not os.path.isfile(output_file):
        return {"status": "No log file found"}
    
    try:
        # Read CSV file
        with open(output_file, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
        
        if not rows:
            return {"status": "Log file is empty"}
        
        # Calculate statistics
        total_queries = len(rows)
        total_cost = sum(float(row["estimated_cost_usd"]) for row in rows)
        total_latency = sum(float(row["latency_ms"]) for row in rows)
        escalated_count = sum(1 for row in rows if row["escalated"] == "Yes")
        avg_quality = sum(float(row["quality_score"]) for row in rows) / total_queries
        
        # Count model usage
        model_usage = {}
        for row in rows:
            model = row["final_model"]
            model_usage[model] = model_usage.get(model, 0) + 1
        
        stats = {
            "status": "success",
            "total_queries": total_queries,
            "total_cost_usd": f"{total_cost:.6f}",
            "avg_cost_per_query_usd": f"{(total_cost / total_queries):.6f}",
            "total_latency_ms": f"{total_latency:.0f}",
            "avg_latency_ms": f"{(total_latency / total_queries):.0f}",
            "avg_quality_score": f"{avg_quality:.2f}",
            "escalation_rate": f"{(escalated_count / total_queries * 100):.1f}%",
            "escalated_count": escalated_count,
            "model_usage": model_usage
        }
        
        return stats
    
    except Exception as e:
        return {"status": f"Error reading log: {e}"}
