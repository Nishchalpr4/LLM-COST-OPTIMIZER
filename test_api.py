"""
Simple test script to verify Groq API and answer printing works.
"""

from src.main import LLMCostOptimizer

# Initialize optimizer
optimizer = LLMCostOptimizer(max_escalations=1)

# Test question
question = "What is Python?"

print("\n" + "="*80)
print("TESTING GROQ API CONNECTION")
print("="*80)

print(f"\nQuestion: {question}\n")

# Process
result = optimizer.process_question(question, verbose=True)

print("\n" + "="*80)
print("RESULT DETAILS")
print("="*80)
print(f"\n✓ Answer received: {len(result['answer'])} characters")
print(f"\nFull Answer:\n{result['answer']}")
print(f"\nDifficulty: {result['difficulty']:.2f}")
print(f"Model: {result['final_model']}")
print(f"Quality: {result['quality_score']:.2f}")
print(f"Cost: ${result['estimated_cost']:.6f}")
print("\n" + "="*80)
