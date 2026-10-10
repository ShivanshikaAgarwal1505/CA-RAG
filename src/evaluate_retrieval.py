"""
Evaluate retrieval quality across different methods
"""

import json
from conflict_aware_retrieval import ConflictAwareRetriever

def evaluate_precision_at_k(retriever, test_cases, k=3):
    """
    Manually evaluate if retrieved cases are relevant
    """
    
    results = {
        'conflict': [],
        'semantic': [],
        'hybrid': []
    }
    
    for test_case in test_cases:
        domain = test_case['domain']
        
        print("\n" + "="*70)
        print(f"EVALUATING: {test_case['id']}")
        print("="*70)
        print(f"Query: {test_case['query'][:100]}...")
        
        query_conflicts = test_case.get('conflicts', [])
        print(f"Conflicts: {[c['type'] for c in query_conflicts]}")
        
        # Retrieve with each method
        for method in ['conflict', 'semantic', 'hybrid']:
            retrieved = retriever.retrieve(test_case, domain, k, method)
            
            print(f"\n>>> {method.upper()} retrieved:")
            for i, r in enumerate(retrieved, 1):
                case = r['case']
                case_id = case.get('id', case.get('case_id'))
                print(f"  {i}. {case_id} (score: {r['score']:.3f})")
                print(f"     Conflicts: {[c['type'] for c in case.get('conflicts', [])]}")
            
            # Manual relevance judgment
            print(f"\nHow many of these {k} are RELEVANT to the query?")
            print("(Consider: Do they have similar problems/conflicts?)")
            
            while True:
                try:
                    relevant_count = int(input(f"Enter 0-{k}: "))
                    if 0 <= relevant_count <= k:
                        break
                    else:
                        print(f"Please enter a number between 0 and {k}")
                except ValueError:
                    print("Please enter a valid number")
            
            precision = relevant_count / k
            results[method].append(precision)
            print(f"Precision@{k}: {precision:.2f}")
        
        print("\n" + "="*70 + "\n")
    
    # Summary
    print("\n" + "="*70)
    print("EVALUATION SUMMARY")
    print("="*70)
    
    for method in ['conflict', 'semantic', 'hybrid']:
        avg_precision = sum(results[method]) / len(results[method])
        print(f"{method.upper()}: Average Precision@{k} = {avg_precision:.3f}")
    
    return results


def main():
    retriever = ConflictAwareRetriever()
    
    # Load all cases - FIX: add encoding='utf-8'
    with open('../data/processed_cases.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both formats
    cases = data if isinstance(data, list) else data.get('cases', [])
    
    # Select 5 test cases with conflicts
    test_cases = [c for c in cases 
                  if c['domain'] == 'health' and c.get('conflicts')][:5]
    
    print(f"Selected {len(test_cases)} test cases for evaluation")
    
    results = evaluate_precision_at_k(retriever, test_cases, k=3)
    
    # Save results
    with open('../data/retrieval_evaluation.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print("\n✓ Results saved to retrieval_evaluation.json")


if __name__ == "__main__":
    main() 