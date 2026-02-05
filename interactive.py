"""
Interactive Mode: Demonstrate the LLM Cost Optimizer with user input and transparent output.

This script shows how the optimizer works step-by-step with detailed explanations
of difficulty estimation, routing decisions, and cost calculations.
"""

from src.main import LLMCostOptimizer
from src.router import estimate_difficulty, select_model, get_model_config


def show_transparent_analysis(question: str):
    """
    Show transparent step-by-step analysis of how difficulty is estimated.
    
    This helps users understand WHY a question was routed to a particular model.
    """
    print("\n" + "="*80)
    print("TRANSPARENT DIFFICULTY ANALYSIS")
    print("="*80)
    
    # Break down the difficulty estimation
    question_length = len(question.split())
    question_lower = question.lower()
    
    print(f"\nQuestion: \"{question}\"")
    print(f"Length: {question_length} words")
    
    # Analyze length
    print("\n[1] LENGTH HEURISTIC:")
    if question_length < 5:
        length_score = 0.1
        print(f"    • {question_length} words < 5 → Very short, likely simple → +0.1")
    elif question_length < 15:
        length_score = 0.3
        print(f"    • {question_length} words between 5-15 → Medium difficulty → +0.3")
    elif question_length < 30:
        length_score = 0.5
        print(f"    • {question_length} words between 15-30 → Longer, more complex → +0.5")
    else:
        length_score = 0.7
        print(f"    • {question_length} words > 30 → Very long, likely complex → +0.7")
    
    # Analyze keywords
    print("\n[2] KEYWORD HEURISTIC:")
    complex_keywords = [
        "explain", "how", "why", "analyze", "compare", "contrast",
        "evaluate", "summarize", "discuss", "implement", "design",
        "algorithm", "complex", "optimization", "technical"
    ]
    
    found_keywords = [kw for kw in complex_keywords if kw in question_lower]
    keyword_score = len(found_keywords) * 0.1
    
    if found_keywords:
        print(f"    • Found keywords: {found_keywords}")
        print(f"    • {len(found_keywords)} keyword(s) × 0.1 = +{keyword_score}")
    else:
        print(f"    • No complex keywords found → +0.0")
    
    # Analyze punctuation
    print("\n[3] PUNCTUATION HEURISTIC:")
    punct_score = 0.0
    question_count = question.count("?")
    comma_count = question.count(",")
    
    if question_count > 1:
        punct_score += 0.15
        print(f"    • Multiple questions ({question_count} ?) → +0.15")
    
    if ";" in question or comma_count > 3:
        punct_score += 0.1
        print(f"    • Multiple parts (commas: {comma_count}, semicolons: {';' in question}) → +0.1")
    
    if punct_score == 0:
        print(f"    • No special punctuation → +0.0")
    
    # Calculate final score
    difficulty = length_score + keyword_score + punct_score
    difficulty = min(difficulty, 1.0)  # Cap at 1.0
    
    print("\n" + "-"*80)
    print(f"TOTAL DIFFICULTY SCORE: {difficulty:.2f}/1.0")
    print("-"*80)
    
    # Show routing decision
    model = select_model(difficulty)
    print(f"\nROUTING DECISION:")
    if difficulty < 0.5:
        print(f"  • Difficulty {difficulty:.2f} < 0.5 (threshold)")
        print(f"  • Route to: SMALL MODEL (cheaper, faster)")
        print(f"  • Cost: $0.0005 per 1k tokens")
        print(f"  • Latency: ~500ms")
    else:
        print(f"  • Difficulty {difficulty:.2f} ≥ 0.5 (threshold)")
        print(f"  • Route to: LARGE MODEL (more capable)")
        print(f"  • Cost: $0.015 per 1k tokens (30x more expensive)")
        print(f"  • Latency: ~2000ms")
    
    print("\n" + "="*80 + "\n")
    
    return difficulty


def main():
    """Main interactive loop."""
    
    print("\n" + "="*80)
    print("LLM COST OPTIMIZER - INTERACTIVE MODE")
    print("="*80)
    print("\nThis tool shows how the optimizer routes questions intelligently.")
    print("You'll see transparent reasoning at each step:")
    print("  1. How difficulty is calculated")
    print("  2. Which model is selected")
    print("  3. Answer quality validation")
    print("  4. Cost and latency estimates")
    print("\nType 'exit' or 'quit' to stop")
    print("="*80)
    
    # Initialize optimizer
    optimizer = LLMCostOptimizer(max_escalations=1)
    query_count = 0
    
    while True:
        print("\n")
        user_input = input("Enter your question: ").strip()
        
        # Exit conditions
        if user_input.lower() in ['exit', 'quit', 'q']:
            break
        
        if not user_input:
            print("❌ Please enter a valid question")
            continue
        
        query_count += 1
        
        # Show transparent analysis
        show_transparent_analysis(user_input)
        
        # Process the question through the full optimizer
        print("="*80)
        print("PROCESSING THROUGH OPTIMIZER")
        print("="*80)
        result = optimizer.process_question(user_input, verbose=True)
        
        # Show summary of this query
        print("\n" + "="*80)
        print("QUERY SUMMARY")
        print("="*80)
        
        # Print answer prominently
        print(f"\n{'🤖 ANSWER FROM LLM:':^80}\n")
        print("-" * 80)
        print(result['answer'])
        print("-" * 80)
        
        # Print metrics
        print(f"\nDifficulty: {result['difficulty']:.2f}/1.0")
        print(f"Initial Model: {result['initial_model']}")
        print(f"Final Model: {result['final_model']}")
        print(f"Quality Score: {result['quality_score']:.2f}/1.0")
        print(f"Estimated Cost: ${result['estimated_cost']:.6f}")
        print(f"Estimated Latency: {result['estimated_latency']:.0f}ms")
        if result['escalated']:
            print(f"⚠️  Escalated from {result['initial_model']} to {result['final_model']}")
        print("="*80)
    
    # Show final statistics
    if query_count > 0:
        print("\n" + "="*80)
        print("SESSION STATISTICS")
        print("="*80)
        
        stats = optimizer.get_stats()
        
        if stats.get("status") == "success":
            print(f"\n✓ Processed {stats['total_queries']} questions")
            print(f"  • Total Estimated Cost: ${stats['total_cost_usd']}")
            print(f"  • Average Cost per Query: ${stats['avg_cost_per_query_usd']}")
            print(f"  • Total Latency: {stats['total_latency_ms']}ms")
            print(f"  • Average Latency: {stats['avg_latency_ms']}ms")
            print(f"  • Average Quality Score: {stats['avg_quality_score']}/1.0")
            print(f"  • Escalation Rate: {stats['escalation_rate']}")
            print(f"  • Model Usage: {stats['model_usage']}")
            print(f"\n✓ Full results logged to: output/optimizer_log.csv")
        else:
            print(f"  {stats.get('status', 'Unknown error')}")
        
        print("="*80 + "\n")


if __name__ == "__main__":
    main()
