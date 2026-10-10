from unified_rag import UnifiedRAG
from constraint_extractor import ConstraintExtractor
from conflict_detector import ConflictDetector

def test_full_pipeline():
    """Test complete pipeline: Query → Constraints → Conflicts → RAG"""
    
    # Initialize systems
    print("Initializing systems...")
    rag = UnifiedRAG()
    extractor = ConstraintExtractor()
    detector = ConflictDetector()
    
    # Test query
    query = "22F, hair fall, vegetarian, hostel mess, ₹150/day budget, prefer quick meals"
    
    print("\n" + "="*70)
    print("FULL PIPELINE TEST")
    print("="*70)
    print(f"\nQuery: {query}")
    
    # Step 1: Extract constraints
    print("\n[Step 1] Extracting constraints...")
    constraints = extractor.extract(query, domain="health")
    print(f"✓ Extracted {len(constraints['hard_constraints'])} hard, "
          f"{len(constraints['soft_constraints'])} soft constraints, "
          f"{len(constraints['goals'])} goals")
    
    # Step 2: Detect conflicts
    print("\n[Step 2] Detecting conflicts...")
    conflicts = detector.detect_conflicts(constraints, domain="health")
    print(f"✓ Detected {len(conflicts)} conflicts")
    
    if conflicts:
        for conflict in conflicts:
            print(f"  - {conflict['type']} (severity: {conflict['severity']:.2f})")
    
    # Step 3: RAG search based on goals
    print("\n[Step 3] Searching knowledge base...")
    for goal in constraints['goals']:
        search_query = f"{goal['value']} {constraints['hard_constraints'][1]['value']}"  # e.g., "reduce_hair_fall vegetarian"
        results = rag.search(search_query, domain="health", n_results=5)
        
        print(f"\n  Query: '{search_query}'")
        print(f"  Results: {[m['food_name'] for m in results['metadatas'][0]]}")
    
    print("\n" + "="*70)
    print("✓ FULL PIPELINE WORKING!")
    print("="*70)

if __name__ == "__main__":
    test_full_pipeline()