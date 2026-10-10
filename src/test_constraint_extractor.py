from constraint_extractor import ConstraintExtractor
import json

# Test cases from your dataset
test_cases = [
    {
        "id": "HC_001",
        "query": "22F, hair fall, vegetarian, hostel mess, ₹150/day budget, prefer quick meals",
        "domain": "health"
    },
    {
        "id": "HC_002", 
        "query": "25M, want to gain muscle, non-veg, gym available, ₹300/day budget, willing to cook",
        "domain": "health"
    },
    {
        "id": "HC_003",
        "query": "19F, anemia (iron deficiency), vegetarian, home cooking, ₹200/day, no time for elaborate meals",
        "domain": "health"
    },
    {
        "id": "HC_004",
        "query": "30M, pre-diabetic, need low carb diet, ₹250/day, prefer tasty food",
        "domain": "health"
    },
    {
        "id": "HC_005",
        "query": "21F, weight loss goal, vegan preferred, ₹100/day budget, hostel mess only",
        "domain": "health"
    },
    {
        "id": "EC_001",
        "query": "3rd semester M.Tech, completed ML basics, need 4 courses, interested in CV and NLP, want high GPA professors",
        "domain": "education"
    },
    {
        "id": "EC_002",
        "query": "Final year B.Tech, prerequisites done, need easy courses for GPA, max 15 hours/week workload",
        "domain": "education"
    },
    {
        "id": "TR_001",
        "query": "2 friends, ₹15000 total budget, 5 days, beach destination, want water sports and nightlife",
        "domain": "travel"
    },
    {
        "id": "TR_002",
        "query": "Solo trip, ₹8000 budget, 3 days, spiritual destination, prefer mountains, March travel",
        "domain": "travel"
    },
    {
        "id": "TR_003",
        "query": "Family of 4, ₹30000 budget, 7 days, kid-friendly destination, educational activities preferred",
        "domain": "travel"
    }
]

def test_extraction():
    extractor = ConstraintExtractor()
    
    results = []
    
    print("="*70)
    print("TESTING CONSTRAINT EXTRACTION")
    print("="*70)
    
    for i, case in enumerate(test_cases):
        print(f"\n[{i+1}/10] Testing {case['id']}...")
        print(f"Query: {case['query']}")
        
        constraints = extractor.extract(case['query'], case['domain'])
        
        if constraints:
            print("✓ Extraction successful")
            print(f"  Hard: {len(constraints['hard_constraints'])} constraints")
            print(f"  Soft: {len(constraints['soft_constraints'])} constraints")
            print(f"  Goals: {len(constraints['goals'])} goals")
            
            results.append({
                "case_id": case['id'],
                "status": "success",
                "constraints": constraints
            })
        else:
            print("✗ Extraction failed")
            results.append({
                "case_id": case['id'],
                "status": "failed"
            })
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"Success rate: {success_count}/10 ({success_count*10}%)")
    
    # Save results
    with open('../data/constraint_extraction_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n✓ Results saved to data/constraint_extraction_test_results.json")
    
    return results

if __name__ == "__main__":
    test_extraction()