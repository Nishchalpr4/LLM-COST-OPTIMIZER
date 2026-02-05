"""
Example: Demonstrate the LLM Cost Optimizer with sample questions.

This script shows how to use the optimizer with different types of questions
and displays the routing and cost optimization decisions.
"""

from src.main import LLMCostOptimizer


def main():
    """Run example questions through the optimizer."""
    
    print("\n" + "="*70)
    print("LLM COST OPTIMIZER - EXAMPLE RUN")
    print("="*70)
    print("\nThis demo shows how the optimizer:")
    print("  1. Routes simple questions to cheaper models")
    print("  2. Routes complex questions to powerful models")
    print("  3. Escalates if answer quality is too low")
    print("  4. Logs all decisions to CSV for analysis")
    print()
    
    # Initialize optimizer
    optimizer = LLMCostOptimizer(max_escalations=1)
    
    # Sample questions covering different difficulty levels
    sample_questions = [
        # Simple questions (should use small model)
        "What is Python?",
        "How do I print hello world?",
        
        # Medium questions (might use small or large)
        "Explain how machine learning works",
        "What are the differences between arrays and linked lists in computer science?",
        
        # Complex questions (should use large model)
        "Design an algorithm to find the optimal route through a graph while minimizing latency and maximizing throughput under varying network conditions, considering both geographical proximity and current network load factors.",
        "Analyze the trade-offs between consistency, availability, and partition tolerance in distributed systems, provide concrete examples, and explain how different architectures make different choices.",
    ]
    
    results = []
    
    # Process each question
    for question in sample_questions:
        result = optimizer.process_question(question, verbose=True)
        results.append(result)
    
    # Display summary statistics
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    
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
    else:
        print(f"  {stats.get('status', 'Unknown error')}")
    
    print(f"\n✓ Results logged to: output/optimizer_log.csv")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
