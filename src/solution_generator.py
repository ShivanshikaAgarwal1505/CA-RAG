"""
Generate solutions using LLM with few-shot prompts
"""

import os
from api_key_manager import APIKeyManager
from prompt_builder import PromptBuilder
import json

class SolutionGenerator:
    def __init__(self):
        self.api_manager = APIKeyManager()
        self.client = self.api_manager.get_client()
        self.prompt_builder = PromptBuilder()
    
    def generate_solution(self, query: str, domain: str, k: int = 3):
        """Generate solution for query using few-shot learning"""
        
        print(f"\nBuilding prompt with {k} examples...")
        
        # Build prompt with retrieved examples
        prompt, constraints, conflicts, retrieved = self.prompt_builder.build_prompt(
            query, domain, k
        )
        
        print(f"✓ Retrieved {len(retrieved)} similar cases")
        print(f"✓ Detected {len(conflicts)} conflicts")
        
        if retrieved:
            print("\nRetrieved cases:")
            for i, r in enumerate(retrieved, 1):
                case = r['case']
                case_id = case.get('id', case.get('case_id'))
                score = r.get('score', 0)
                print(f"  {i}. {case_id} (similarity: {score:.3f})")
        
        print(f"\n🤖 Calling LLM to generate solution...")
        
        # Call LLM
        response = self.api_manager.call_with_retry(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert planning assistant who provides practical, feasible solutions that respect all constraints."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        solution = response.choices[0].message.content
        
        print(f"✓ Generated solution ({len(solution)} characters)\n")
        
        return {
            'query': query,
            'domain': domain,
            'constraints': constraints,
            'conflicts': conflicts,
            'retrieved_cases': [r['case'].get('id', r['case'].get('case_id')) for r in retrieved],
            'prompt': prompt,
            'solution': solution,
            'model': 'llama-3.3-70b-versatile',
            'k_examples': k
        }


def main():
    """Test solution generation"""
    
    generator = SolutionGenerator()
    
    # Test queries
    test_queries = [
        ("22M; Hair fall; Budget ₹150/day; Veg; No kitchen; Bangalore", "health"),
        ("22F; Anemia, fatigue; Budget ₹180/day; Veg; Hostel mess; Prefer natural foods", "health"),
    ]
    
    for i, (test_query, domain) in enumerate(test_queries, 1):
        print("\n" + "="*70)
        print(f"TEST {i}: SOLUTION GENERATION")
        print("="*70)
        print(f"\nQuery: {test_query}\n")
        
        # Generate solution
        result = generator.generate_solution(test_query, domain=domain, k=3)
        
        # Print results
        print("="*70)
        print("GENERATED SOLUTION")
        print("="*70)
        print(result['solution'])
        print("="*70)
        
        # Save result
        output_file = f'../results/solution_test_{i}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Full result saved to {output_file}\n")


if __name__ == "__main__":
    main()