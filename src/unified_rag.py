from rag_setup import NutritionRAG, EducationRAG, TravelRAG
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # Research/
DATA_DIR = BASE_DIR / "data"

class UnifiedRAG:
    """Unified interface for all domains"""
    
    def __init__(self):
        print("Initializing Unified RAG System...")
        
        self.nutrition_rag = NutritionRAG(DATA_DIR / "nutrition_db.csv")
        self.education_rag = EducationRAG(DATA_DIR / "courses_db.csv")
        self.travel_rag = TravelRAG(DATA_DIR / "travel_db.csv")
        
        print("✓ All RAG systems ready!")
    
    def search(self, query: str, domain: str, n_results: int = 5, constraints: dict = None):
        """
        Search across domains with constraint filtering
        
        Args:
            query: Search query
            domain: 'health', 'education', or 'travel'
            n_results: Number of results to return
            constraints: Optional constraint dict for filtering
        """
        if domain == 'health':
            results = self.nutrition_rag.search(query, n_results * 2)  # Get extra for filtering
            
            # Filter by dietary constraints if provided
            if constraints:
                results = self._filter_by_diet(results, constraints)
            
            # Remove duplicates
            results = self._remove_duplicates(results, n_results)
            
            return results
            
        elif domain == 'education':
            return self.education_rag.search(query, n_results)
        elif domain == 'travel':
            return self.travel_rag.search(query, n_results)
        else:
            raise ValueError(f"Unknown domain: {domain}")
    
    def _filter_by_diet(self, results, constraints):
        """Filter nutrition results by dietary restrictions"""
        # Find diet constraint
        diet_type = None
        for c in constraints.get('hard_constraints', []):
            if c['type'] == 'diet':
                diet_type = c['value'].lower()
                break
        
        if not diet_type:
            return results  # No filtering needed
        
        # Filter results
        filtered_docs = []
        filtered_metas = []
        
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            food_name = meta['food_name'].lower()
            category = meta['category'].lower()
            
            # Vegetarian filter
            if diet_type == 'vegetarian':
                if category not in ['animal products', 'seafood', 'meat', 'poultry']:
                    if 'beef' not in food_name and 'chicken' not in food_name and 'fish' not in food_name:
                        filtered_docs.append(doc)
                        filtered_metas.append(meta)
            
            # Vegan filter
            elif diet_type == 'vegan':
                if category not in ['animal products', 'seafood', 'meat', 'poultry', 'dairy']:
                    if not any(word in food_name for word in ['milk', 'cheese', 'egg', 'butter', 'yogurt', 'paneer']):
                        filtered_docs.append(doc)
                        filtered_metas.append(meta)
            
            # Non-veg (no filter)
            else:
                filtered_docs.append(doc)
                filtered_metas.append(meta)
        
        return {
            'documents': [filtered_docs],
            'metadatas': [filtered_metas]
        }
    
    def _remove_duplicates(self, results, n_results):
        """Remove duplicate foods from results"""
        seen_foods = set()
        unique_docs = []
        unique_metas = []
        
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            food_name = meta['food_name']
            
            if food_name not in seen_foods:
                seen_foods.add(food_name)
                unique_docs.append(doc)
                unique_metas.append(meta)
                
                if len(unique_docs) >= n_results:
                    break
        
        return {
            'documents': [unique_docs],
            'metadatas': [unique_metas]
        }
    
    def search_all_domains(self, query: str, n_results: int = 3, constraints: dict = None):
        """Search across all domains"""
        results = {}
        results['health'] = self.search(query, domain='health', n_results=n_results, constraints=constraints)
        results['education'] = self.education_rag.search(query, n_results)
        results['travel'] = self.travel_rag.search(query, n_results)
        return results


# Test unified system with constraints
if __name__ == "__main__":
    from constraint_extractor import ConstraintExtractor
    
    unified = UnifiedRAG()
    extractor = ConstraintExtractor()
    
    # Test with constraint filtering
    query = "22F, hair fall, vegetarian, hostel mess, ₹150/day budget, prefer quick meals"
    
    print("\n" + "="*60)
    print("Query:", query)
    print("="*60)
    
    # Extract constraints
    constraints = extractor.extract(query, domain="health")
    
    # Search with filtering
    results = unified.search(
        "reduce hair fall vegetarian", 
        domain="health", 
        n_results=5,
        constraints=constraints
    )
    
    print("\nFiltered Results (vegetarian only, no duplicates):")
    for i, meta in enumerate(results['metadatas'][0]):
        print(f"{i+1}. {meta['food_name']} ({meta['category']}) - "
              f"Biotin: {meta['biotin']}mcg, Protein: {meta['protein']}g")