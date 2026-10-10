"""
Conflict-Aware Case Retrieval for Few-Shot Learning
Retrieves cases based on similar constraint conflicts, not just semantic similarity

Author: Research Project - Adaptive Few-Shot Learning
Date: 2025
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter
import numpy as np


class ConflictAwareRetriever:
    def __init__(self, processed_cases_path='../data/processed_cases.json'):
        """Initialize retriever with preprocessed cases"""
        self.cases = self._load_cases(processed_cases_path)
        print(f"✓ Loaded {len(self.cases)} preprocessed cases")
        
        # Statistics
        domains = [c['domain'] for c in self.cases]
        domain_counts = Counter(domains)
        for domain, count in domain_counts.items():
            print(f"  - {domain}: {count} cases")
        
    def _load_cases(self, path: str) -> List[Dict]:
        """Load processed cases from JSON"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both formats: list or dict with 'cases' key
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'cases' in data:
            return data['cases']
        else:
            raise ValueError("Unexpected JSON format. Expected list or dict with 'cases' key")
    
    def retrieve(self, query_case: Dict, domain: str, k: int = 3, 
                 method: str = 'conflict') -> List[Dict]:
        """
        Retrieve top-k similar cases
        
        Args:
            query_case: Case with extracted constraints and conflicts
            domain: 'health', 'education', or 'travel'
            k: Number of cases to retrieve
            method: 'conflict', 'semantic', or 'hybrid'
        
        Returns:
            List of k most similar cases with similarity scores
        """
        # Filter by domain (exclude the query case itself)
        query_id = query_case.get('id', query_case.get('case_id'))
        domain_cases = [c for c in self.cases 
                       if c['domain'] == domain 
                       and c.get('id', c.get('case_id')) != query_id]
        
        if not domain_cases:
            print(f"Warning: No cases found for domain '{domain}'")
            return []
        
        if method == 'conflict':
            return self._retrieve_by_conflict(query_case, domain_cases, k)
        elif method == 'semantic':
            return self._retrieve_by_semantic(query_case, domain_cases, k)
        elif method == 'hybrid':
            return self._retrieve_hybrid(query_case, domain_cases, k)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'conflict', 'semantic', or 'hybrid'")
    
    def _retrieve_by_conflict(self, query: Dict, candidates: List[Dict], 
                             k: int) -> List[Dict]:
        """Retrieve based on conflict pattern similarity"""
        scored_cases = []
        
        for case in candidates:
            score = self._calculate_conflict_similarity(
                query.get('conflicts', []), 
                case.get('conflicts', [])
            )
            scored_cases.append({
                'case': case,
                'score': score,
                'method': 'conflict'
            })
        
        # Sort by score (descending)
        scored_cases.sort(key=lambda x: x['score'], reverse=True)
        
        # Deduplicate and return top-k
        return self._deduplicate(scored_cases, k)
    
    def _retrieve_by_semantic(self, query: Dict, candidates: List[Dict], 
                             k: int) -> List[Dict]:
        """Retrieve based on text similarity (baseline)"""
        query_text = query.get('query', '').lower()
        query_words = set(query_text.split())
        
        scored_cases = []
        for case in candidates:
            case_text = case.get('query', '').lower()
            case_words = set(case_text.split())
            
            # Jaccard similarity of words
            intersection = query_words & case_words
            union = query_words | case_words
            
            score = len(intersection) / len(union) if union else 0.0
            
            scored_cases.append({
                'case': case,
                'score': score,
                'method': 'semantic'
            })
        
        scored_cases.sort(key=lambda x: x['score'], reverse=True)
        
        # Deduplicate and return top-k
        return self._deduplicate(scored_cases, k)
    
    def _retrieve_hybrid(self, query: Dict, candidates: List[Dict], 
                        k: int) -> List[Dict]:
        """Combine conflict and semantic similarity"""
        scored_cases = []
        
        # Pre-compute query text features
        query_text = query.get('query', '').lower()
        query_words = set(query_text.split())
        
        for case in candidates:
            # Conflict similarity
            conflict_score = self._calculate_conflict_similarity(
                query.get('conflicts', []),
                case.get('conflicts', [])
            )
            
            # Semantic similarity
            case_text = case.get('query', '').lower()
            case_words = set(case_text.split())
            intersection = query_words & case_words
            union = query_words | case_words
            semantic_score = len(intersection) / len(union) if union else 0.0
            
            # Weighted combination (60% conflict, 40% semantic)
            final_score = conflict_score * 0.6 + semantic_score * 0.4
            
            scored_cases.append({
                'case': case,
                'score': final_score,
                'conflict_score': conflict_score,
                'semantic_score': semantic_score,
                'method': 'hybrid'
            })
        
        scored_cases.sort(key=lambda x: x['score'], reverse=True)
        
        # Deduplicate and return top-k
        return self._deduplicate(scored_cases, k)
    
    def _deduplicate(self, scored_cases: List[Dict], k: int) -> List[Dict]:
        """Remove duplicate cases and return top-k unique cases"""
        seen_ids = set()
        unique_cases = []
        
        for item in scored_cases:
            case_id = item['case'].get('id', item['case'].get('case_id', 'unknown'))
            
            if case_id not in seen_ids:
                seen_ids.add(case_id)
                unique_cases.append(item)
            
            if len(unique_cases) >= k:
                break
        
        return unique_cases
    
    def _calculate_conflict_similarity(self, query_conflicts: List[Dict], 
                                      case_conflicts: List[Dict]) -> float:
        """
        Calculate similarity between two conflict sets
        
        Similarity based on:
        1. Conflict type overlap (Jaccard similarity) - 70% weight
        2. Severity alignment (if same conflict types exist) - 30% weight
        
        Args:
            query_conflicts: List of conflict dicts from query
            case_conflicts: List of conflict dicts from candidate case
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Handle empty conflicts
        if not query_conflicts and not case_conflicts:
            return 0.0  # No conflicts in either - not similar
        
        if not query_conflicts or not case_conflicts:
            return 0.0  # One has conflicts, other doesn't - not similar
        
        # Extract conflict types
        query_types = set(c['type'] for c in query_conflicts)
        case_types = set(c['type'] for c in case_conflicts)
        
        # Jaccard similarity of conflict types
        intersection = query_types & case_types
        union = query_types | case_types
        
        if not union:
            return 0.0
        
        jaccard = len(intersection) / len(union)
        
        # Bonus: Severity alignment for matching conflict types
        severity_bonus = 0.0
        if intersection:
            # Build severity maps
            query_severity_map = {c['type']: c['severity'] 
                                 for c in query_conflicts}
            case_severity_map = {c['type']: c['severity'] 
                                for c in case_conflicts}
            
            # Compare severities for matching conflicts
            severity_diffs = []
            for conflict_type in intersection:
                diff = abs(query_severity_map[conflict_type] - 
                          case_severity_map[conflict_type])
                severity_diffs.append(diff)
            
            # Average severity alignment (0 = perfect match, 1 = max diff)
            avg_diff = np.mean(severity_diffs)
            severity_bonus = (1 - avg_diff) * 0.3  # 30% weight
        
        # Final score: 70% type overlap + 30% severity alignment
        return jaccard * 0.7 + severity_bonus
    
    def print_retrieval_results(self, results: List[Dict], 
                               query_case: Dict = None):
        """Pretty print retrieval results"""
        print("\n" + "="*80)
        print("RETRIEVAL RESULTS")
        print("="*80)
        
        if query_case:
            query_text = query_case.get('query', 'N/A')
            print(f"\nQuery: {query_text[:80]}...")
            print(f"Domain: {query_case.get('domain', 'N/A')}")
            
            query_conflicts = query_case.get('conflicts', [])
            if query_conflicts:
                print(f"\nQuery Conflicts ({len(query_conflicts)}):")
                for conf in query_conflicts:
                    print(f"  • {conf['type']} (severity: {conf['severity']:.2f})")
            else:
                print("\nQuery Conflicts: None")
        
        print(f"\n{'Rank':<6} {'Score':<8} {'Case ID':<12} {'Conflicts':<40}")
        print("-"*80)
        
        if not results:
            print("No results found")
        else:
            for i, result in enumerate(results, 1):
                case = result['case']
                score = result['score']
                case_id = case.get('id', case.get('case_id', 'Unknown'))
                
                conflicts = case.get('conflicts', [])
                if conflicts:
                    conflict_str = ", ".join([c['type'] for c in conflicts[:2]])
                    if len(conflicts) > 2:
                        conflict_str += f" +{len(conflicts)-2} more"
                else:
                    conflict_str = "(no conflicts)"
                
                print(f"{i:<6} {score:<8.3f} {case_id:<12} {conflict_str:<40}")
        
        print("="*80 + "\n")
    
    def get_statistics(self):
        """Get statistics about the case collection"""
        total_cases = len(self.cases)
        cases_with_conflicts = sum(1 for c in self.cases if c.get('conflicts'))
        
        conflict_types = []
        for case in self.cases:
            for conflict in case.get('conflicts', []):
                conflict_types.append(conflict['type'])
        
        conflict_counts = Counter(conflict_types)
        
        print("\n" + "="*80)
        print("CASE COLLECTION STATISTICS")
        print("="*80)
        print(f"\nTotal cases: {total_cases}")
        print(f"Cases with conflicts: {cases_with_conflicts} ({cases_with_conflicts/total_cases*100:.1f}%)")
        print(f"Cases without conflicts: {total_cases - cases_with_conflicts}")
        
        print(f"\nConflict types distribution:")
        for conflict_type, count in conflict_counts.most_common():
            print(f"  • {conflict_type}: {count} occurrences")
        
        print("="*80 + "\n")
 
def main():
    """Test the retrieval system"""
    
    print("\n" + "="*80)
    print("CONFLICT-AWARE RETRIEVAL SYSTEM - TEST")
    print("="*80 + "\n")
    
    # Initialize retriever
    retriever = ConflictAwareRetriever()
    
    # Show statistics
    retriever.get_statistics()
    
    # Load a test case (use one from processed_cases.json)
    with open('../data/processed_cases.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both formats
    cases = data if isinstance(data, list) else data.get('cases', [])
    
    # Find a case with conflicts to use as test query
    test_case = None
    for case in cases:
        if case['domain'] == 'health' and case.get('conflicts'):
            test_case = case
            break
    
    if not test_case:
        print("❌ No health cases with conflicts found!")
        return
    
    print("\n" + "="*80)
    print("TESTING CONFLICT-AWARE RETRIEVAL")
    print("="*80)
    
    # Test 1: Conflict-based retrieval
    print("\n" + "🔍 Method 1: CONFLICT-AWARE RETRIEVAL")
    print("-"*80)
    conflict_results = retriever.retrieve(
        test_case, 
        domain='health', 
        k=5, 
        method='conflict'
    )
    retriever.print_retrieval_results(conflict_results, test_case)
    
    # Test 2: Semantic baseline
    print("\n" + "🔍 Method 2: SEMANTIC BASELINE")
    print("-"*80)
    semantic_results = retriever.retrieve(
        test_case,
        domain='health',
        k=5,
        method='semantic'
    )
    retriever.print_retrieval_results(semantic_results, test_case)
    
    # Test 3: Hybrid
    print("\n" + "🔍 Method 3: HYBRID (60% conflict + 40% semantic)")
    print("-"*80)
    hybrid_results = retriever.retrieve(
        test_case,
        domain='health',
        k=5,
        method='hybrid'
    )
    retriever.print_retrieval_results(hybrid_results, test_case)
    
    # Compare which cases were retrieved by each method
    print("\n" + "="*80)
    print("COMPARISON: Which cases were retrieved by each method?")
    print("="*80)
    
    conflict_ids = set(r['case'].get('id', r['case'].get('case_id', '')) 
                      for r in conflict_results)
    semantic_ids = set(r['case'].get('id', r['case'].get('case_id', '')) 
                      for r in semantic_results)
    hybrid_ids = set(r['case'].get('id', r['case'].get('case_id', '')) 
                    for r in hybrid_results)
    
    print(f"\nConflict-aware retrieved: {conflict_ids}")
    print(f"Semantic-baseline retrieved: {semantic_ids}")
    print(f"Hybrid retrieved: {hybrid_ids}")
    
    overlap_cs = conflict_ids & semantic_ids
    overlap_ch = conflict_ids & hybrid_ids
    unique_conflict = conflict_ids - semantic_ids
    unique_semantic = semantic_ids - conflict_ids
    
    print(f"\n📊 Overlap Analysis:")
    print(f"  • Conflict ∩ Semantic: {overlap_cs}")
    print(f"  • Conflict ∩ Hybrid: {overlap_ch}")
    print(f"  • Unique to Conflict: {unique_conflict}")
    print(f"  • Unique to Semantic: {unique_semantic}")
    
    # Analysis
    print("\n" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)
    
    if unique_conflict:
        print(f"\n✅ Conflict-aware found {len(unique_conflict)} cases that semantic missed!")
        print("   → These likely have similar conflict patterns but different wording")
    
    if unique_semantic:
        print(f"\n⚠️  Semantic found {len(unique_semantic)} cases that conflict-aware missed!")
        print("   → These may have similar wording but different conflict structures")
    
    if len(conflict_ids) == len(semantic_ids) == len(hybrid_ids):
        print("\n⚡ All methods retrieved the same cases")
        print("   → This query might have very clear conflict patterns")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()