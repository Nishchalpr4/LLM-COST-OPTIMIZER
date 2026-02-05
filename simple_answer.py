"""
Simple Answer Viewer: Just ask a question and see the answer.
No complex output, just pure answer.
"""

from src.main import LLMCostOptimizer

def main():
    optimizer = LLMCostOptimizer(max_escalations=1)
    
    print("\n" + "="*80)
    print("SIMPLE ANSWER VIEWER")
    print("="*80)
    print("Type your question and see the answer. Type 'exit' to quit.\n")
    
    while True:
        question = input("Your Question: ").strip()
        
        if question.lower() in ['exit', 'quit', 'q']:
            break
        
        if not question:
            print("❌ Please type a question\n")
            continue
        
        print("\n⏳ Getting answer...")
        result = optimizer.process_question(question, verbose=False)
        
        print("\n" + "="*80)
        print("ANSWER:")
        print("="*80)
        print(result['answer'])
        print("="*80)
        print(f"\nCost: ${result['estimated_cost']:.6f} | Quality: {result['quality_score']:.2f}/1.0 | Model: {result['final_model']}\n")

if __name__ == "__main__":
    main()
