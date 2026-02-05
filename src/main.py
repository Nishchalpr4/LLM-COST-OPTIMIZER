"""
LLM Cost Optimizer: Main orchestrator that coordinates all steps.

ARCHITECTURE OVERVIEW:
1. Router: Estimate difficulty & select initial model
2. Validator: Generate answer & check quality
3. Logger: Record usage and costs to CSV
4. Escalation: If quality low, retry with better model

WHY THIS DESIGN:
- Saves money by using cheaper models when possible
- Maintains quality by escalating when needed
- Simple and transparent (easy to debug)
- No complex ML or infrastructure required
"""

import time
from src.router import estimate_difficulty, select_model, get_model_config
from src.validator import generate_answer, calculate_quality_score, should_escalate
from src.logger import log_result, calculate_cost, estimate_latency, get_summary_stats


class LLMCostOptimizer:
    """
    Main class that orchestrates the entire cost optimization workflow.
    
    This class is intentionally simple to be beginner-friendly while
    still demonstrating best practices in code organization.
    """
    
    def __init__(self, max_escalations: int = 1):
        """
        Initialize the optimizer.
        
        Args:
            max_escalations: Maximum number of escalations per query
                (prevents infinite loops)
        """
        self.max_escalations = max_escalations
    
    def process_question(self, question: str, verbose: bool = True) -> dict:
        """
        Process a question through the complete optimization pipeline.
        
        STEP-BY-STEP PROCESS:
        1. Estimate difficulty using heuristics
        2. Route to appropriate model (small or large)
        3. Generate answer using selected model
        4. Validate answer quality
        5. If quality is low: escalate to better model (up to max_escalations)
        6. Log everything to CSV file
        
        Args:
            question: User's question as string
            verbose: Print debug information
            
        Returns:
            Dictionary with results (answer, quality, cost, etc.)
        """
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"Processing: {question[:60]}...")
            print(f"{'='*70}")
        
        # STEP 1: Estimate difficulty using heuristics
        # WHY: Cheaper models can handle simple questions, expensive models for complex ones
        difficulty_score = estimate_difficulty(question)
        if verbose:
            print(f"Step 1 - Difficulty Estimation: {difficulty_score:.2f}/1.0")
        
        # STEP 2: Route to appropriate model based on difficulty
        # WHY: Initial selection tries to use cheaper model when possible
        initial_model = select_model(difficulty_score)
        if verbose:
            print(f"Step 2 - Initial Routing: {initial_model}")
        
        # Get model configuration (cost, latency, quality threshold)
        model_config = get_model_config(initial_model)
        current_model = initial_model
        
        # Initialize escalation counter
        escalation_count = 0
        escalated = False
        
        # Loop for potential escalations
        while escalation_count <= self.max_escalations:
            
            # STEP 3: Generate answer using selected model
            # WHY: Create output for quality validation
            if verbose:
                print(f"Step 3 - Generating answer with {current_model}...")
            
            answer = generate_answer(question, current_model)
            
            # STEP 4: Validate answer quality using basic heuristics
            # WHY: Ensure answer meets minimum quality standards before returning
            if verbose:
                print(f"Step 4 - Validating answer quality...")
            
            quality_score = calculate_quality_score(answer, question)
            quality_threshold = model_config.get("quality_threshold", 0.7)
            
            if verbose:
                print(f"         Quality Score: {quality_score:.2f}/1.0 (threshold: {quality_threshold:.2f})")
            
            # STEP 5: Check if escalation is needed
            # WHY: If quality is below threshold, use better (more expensive) model
            if should_escalate(quality_score, quality_threshold):
                if escalation_count < self.max_escalations:
                    escalation_count += 1
                    escalated = True
                    current_model = "large"  # Escalate to large model
                    model_config = get_model_config(current_model)
                    
                    if verbose:
                        print(f"Step 5 - Escalating to {current_model} (attempt {escalation_count})...")
                    
                    continue  # Retry with better model
                else:
                    if verbose:
                        print(f"Step 5 - Escalation limit reached, using current answer")
                    break
            else:
                # Quality is acceptable
                if verbose:
                    print(f"Step 5 - Quality acceptable, no escalation needed")
                break
        
        # STEP 6: Calculate costs and latency, then log to CSV
        # WHY: Track spending and performance for analysis
        estimated_tokens = len(answer.split()) / 1.3
        estimated_cost = calculate_cost(current_model, len(answer.split()), model_config)
        estimated_latency = estimate_latency(current_model, model_config)
        
        if verbose:
            print(f"Step 6 - Logging results...")
            print(f"         Estimated Cost: ${estimated_cost:.6f}")
            print(f"         Estimated Latency: {estimated_latency:.0f}ms")
            print(f"         Model Used: {current_model}")
            if escalated:
                print(f"         Escalated from {initial_model} to {current_model}")
        
        # Log to CSV
        log_result(
            question=question,
            initial_model=initial_model,
            final_model=current_model,
            answer=answer,
            quality_score=quality_score,
            escalated=escalated,
            latency_ms=estimated_latency,
            estimated_cost=estimated_cost
        )
        
        # Return complete result
        result = {
            "question": question,
            "answer": answer,
            "difficulty": difficulty_score,
            "initial_model": initial_model,
            "final_model": current_model,
            "escalated": escalated,
            "escalations": escalation_count,
            "quality_score": quality_score,
            "estimated_cost": estimated_cost,
            "estimated_latency": estimated_latency
        }
        
        if verbose:
            print(f"{'='*70}\n")
        
        return result
    
    def get_stats(self):
        """
        Get summary statistics from the log file.
        
        WHY: Understand optimizer performance and cost savings
        """
        return get_summary_stats()
