"""
Test prompt generation
"""

from prompt_builder import PromptBuilder

def main():
    builder = PromptBuilder()
    
    # Test query
    test_query = "22M; Hair fall; Budget ₹150/day; Veg; No kitchen; Bangalore"
    
    print("\n" + "="*70)
    print("TESTING PROMPT BUILDER")
    print("="*70)
    print(f"\nTest Query: {test_query}")
    print(f"Domain: health\n")
    
    # Build prompt - NOW captures all 4 return values
    prompt, constraints, conflicts, retrieved = builder.build_prompt(
        test_query, 
        domain='health', 
        k=3
    )
    
    # Print summary
    print("="*70)
    print("EXTRACTED INFORMATION")
    print("="*70)
    print(f"\nHard Constraints: {len(constraints.get('hard_constraints', []))}")
    print(f"Soft Constraints: {len(constraints.get('soft_constraints', []))}")
    print(f"Goals: {len(constraints.get('goals', []))}")
    print(f"Conflicts Detected: {len(conflicts)}")
    print(f"Examples Retrieved: {len(retrieved)}")
    
    if conflicts:
        print("\nConflicts:")
        for c in conflicts:
            print(f"  • {c['type']} (severity: {c['severity']:.2f})")
    else:
        print("\nConflicts: None detected")
    
    if retrieved:
        print("\nRetrieved Cases:")
        for i, r in enumerate(retrieved, 1):
            case = r['case']
            case_id = case.get('id', case.get('case_id'))
            score = r.get('score', 0)
            print(f"  {i}. {case_id} (similarity: {score:.3f})")
    
    # Print full prompt
    print("\n" + "="*70)
    print("FULL PROMPT (sent to LLM)")
    print("="*70)
    print(prompt)
    
    # Save to file - FIX: now writes just the string
    with open('../results/sample_prompt.txt', 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    print("\n" + "="*70)
    print("✓ Prompt saved to results/sample_prompt.txt")
    print("="*70)
    
    # Show prompt length
    print(f"\nPrompt Statistics:")
    print(f"  Total length: {len(prompt)} characters")
    print(f"  Total length: ~{len(prompt.split())} words")
    print(f"  Estimated tokens: ~{len(prompt) // 4}")


if __name__ == "__main__":
    main()