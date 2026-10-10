"""
Cross-Domain Retriever - FINAL FIXED VERSION

Extends ConflictAwareRetriever to retrieve examples from multiple domains
based on conflict pattern similarity.

FIX: Properly uses parent class methods instead of direct collection access
"""

from conflict_aware_retrieval import ConflictAwareRetriever
from conflict_mappings import ConflictMapper
from typing import Dict, List


class CrossDomainRetriever(ConflictAwareRetriever):
    """Retriever that can use examples from other domains"""
    
    def __init__(self):
        super().__init__()
        self.conflict_mapper = ConflictMapper()
    
    def retrieve_cross_domain(self, query_case: Dict, target_domain: str, 
                             k: int = 3, 
                             allow_domains: List[str] = None,
                             cross_domain_ratio: float = 0.33) -> List[Dict]:
        """
        Retrieve examples from multiple domains based on conflict similarity
        
        Args:
            query_case: Query with conflicts
            target_domain: Domain of the query
            k: Number of examples to retrieve
            allow_domains: Which domains to search (default: all)
            cross_domain_ratio: Ratio of cross-domain examples (default: 0.33 = 1/3)
            
        Returns:
            List of examples with potential cross-domain cases
        """
        
        if allow_domains is None:
            allow_domains = ['health', 'education', 'travel']
        
        # Get conflicts from query
        query_conflicts = query_case.get('conflicts', [])
        
        if not query_conflicts:
            # No conflicts, use standard retrieval
            return self.retrieve(query_case, target_domain, k, method='hybrid')
        
        # Calculate how many cross-domain examples to include
        num_cross_domain = max(1, int(k * cross_domain_ratio))  # At least 1
        num_same_domain = k - num_cross_domain
        
        # Get same-domain examples using parent class method
        same_domain_examples = self.retrieve(
            query_case, target_domain, num_same_domain, method='conflict'
        )
        
        # Get cross-domain candidates from other domains
        cross_domain_candidates = []
        
        for source_domain in allow_domains:
            if source_domain == target_domain:
                continue  # Skip same domain
            
            # Get candidates from this source domain
            candidates = self._get_cross_domain_candidates(
                query_case, query_conflicts, source_domain, target_domain, k * 2
            )
            
            cross_domain_candidates.extend(candidates)
        
        # Sort by cross-domain score
        cross_domain_candidates.sort(key=lambda x: x['cross_domain_score'], reverse=True)
        
        # Take top cross-domain examples
        cross_domain_examples = cross_domain_candidates[:num_cross_domain]
        
        # Combine: same-domain first, then cross-domain
        combined = same_domain_examples + cross_domain_examples
        
        return combined[:k]  # Ensure exactly k examples
    
    def _get_cross_domain_candidates(self, query_case: Dict, 
                                     query_conflicts: List[Dict],
                                     source_domain: str, 
                                     target_domain: str,
                                     max_candidates: int) -> List[Dict]:
        """
        Get candidate examples from source domain
        
        Uses parent class retrieve method with source domain
        """
        
        candidates = []
        
        # Create a temporary query case for source domain
        source_query_case = query_case.copy()
        source_query_case['domain'] = source_domain
        
        try:
            # Use parent class retrieve method for source domain
            # This properly accesses the collections
            source_results = self.retrieve(
                source_query_case, 
                source_domain, 
                k=min(max_candidates, 10),  # Get up to 10 candidates
                method='semantic'  # Use semantic for broader search
            )
            
        except Exception as e:
            print(f"  ⚠️  Error retrieving from {source_domain}: {e}")
            return []
        
        # Score each candidate based on cross-domain conflict similarity
        for result in source_results:
            case = result['case']
            
            # Calculate cross-domain score
            score = self._calculate_cross_domain_score(
                query_conflicts, 
                case.get('conflicts', []),
                source_domain, 
                target_domain, 
                result.get('similarity', 0.5)
            )
            
            if score > 0.2:  # Threshold for relevance
                # Get conflict mappings
                mappings = self._get_conflict_mappings(
                    case.get('conflicts', []),
                    source_domain,
                    target_domain
                )
                
                candidates.append({
                    'case': case,
                    'cross_domain_score': score,
                    'source_domain': source_domain,
                    'target_domain': target_domain,
                    'conflict_mappings': mappings,
                    'similarity': result.get('similarity', 0.5)
                })
        
        return candidates
    
    def _calculate_cross_domain_score(self, query_conflicts: List[Dict],
                                      case_conflicts: List[Dict],
                                      source_domain: str,
                                      target_domain: str,
                                      semantic_similarity: float) -> float:
        """
        Calculate cross-domain relevance score
        
        Combines:
        1. Conflict pattern matching (via mappings)
        2. Severity alignment
        3. Semantic similarity
        """
        
        if not query_conflicts or not case_conflicts:
            return 0.0
        
        pattern_score = 0.0
        severity_score = 0.0
        match_count = 0
        
        for query_conflict in query_conflicts:
            query_type = query_conflict.get('type', '')
            query_severity = query_conflict.get('severity', 0.5)
            
            for case_conflict in case_conflicts:
                case_type = case_conflict.get('type', '')
                case_severity = case_conflict.get('severity', 0.5)
                
                # Check if conflicts map to same pattern
                mapping_score = self.conflict_mapper.calculate_mapping_score(
                    case_type, query_type, source_domain, target_domain
                )
                
                if mapping_score > 0.0:
                    # Found a mapping!
                    pattern_score += mapping_score
                    
                    # Add severity alignment
                    severity_diff = abs(query_severity - case_severity)
                    severity_score += (1 - severity_diff)
                    
                    match_count += 1
        
        if match_count == 0:
            return 0.0
        
        # Normalize
        pattern_score /= len(query_conflicts)
        severity_score /= match_count
        
        # Combine: 50% pattern, 30% severity, 20% semantic
        final_score = (pattern_score * 0.5 + 
                      severity_score * 0.3 + 
                      semantic_similarity * 0.2)
        
        return final_score
    
    def _get_conflict_mappings(self, case_conflicts: List[Dict],
                               source_domain: str,
                               target_domain: str) -> List[Dict]:
        """Get all conflict mappings for a case"""
        
        mappings = []
        
        for conflict in case_conflicts:
            conflict_type = conflict.get('type', '')
            
            mapping = self.conflict_mapper.map_conflict(
                conflict_type, source_domain, target_domain
            )
            
            if mapping:
                mappings.append(mapping)
        
        return mappings


# TEST
if __name__ == "__main__":
    print("="*70)
    print("TESTING CROSS-DOMAIN RETRIEVER (FINAL FIX)")
    print("="*70)
    
    try:
        retriever = CrossDomainRetriever()
        
        # Test query with conflicts
        test_case = {
            'query': 'M.Tech student; Need 4 courses; High GPA target; Only 15hrs/week available',
            'domain': 'education',
            'constraints': {
                'hard_constraints': [
                    {'type': 'course_count', 'value': 4},
                    {'type': 'time', 'value': 15}
                ],
                'goals': ['high GPA']
            },
            'conflicts': [
                {'type': 'time_vs_courses', 'severity': 0.9},
                {'type': 'workload_vs_gpa', 'severity': 0.85}
            ]
        }
        
        print("\nTest Query:")
        print(f"  {test_case['query']}")
        print(f"  Domain: {test_case['domain']}")
        print(f"  Conflicts: {[c['type'] for c in test_case['conflicts']]}")
        
        # Retrieve with cross-domain support
        print("\n🔍 Retrieving with cross-domain support...")
        print("  Searching: health, education, travel domains...")
        
        results = retriever.retrieve_cross_domain(
            test_case, 'education', k=3,
            allow_domains=['health', 'education', 'travel']
        )
        
        print(f"\n✓ Retrieved {len(results)} examples:")
        
        same_domain_count = 0
        cross_domain_count = 0
        
        for i, result in enumerate(results, 1):
            case = result['case']
            source_domain = result.get('source_domain', 'education')
            
            cross_domain_label = ""
            cross_domain_emoji = ""
            
            if source_domain != 'education':
                cross_domain_label = f" [Cross-domain: {source_domain}]"
                cross_domain_emoji = " ⭐"
                cross_domain_count += 1
            else:
                same_domain_count += 1
            
            print(f"\n  {i}. {case.get('id', 'Unknown')}{cross_domain_label}{cross_domain_emoji}")
            
            # Show score if available
            if 'cross_domain_score' in result:
                print(f"     Cross-domain score: {result.get('cross_domain_score', 0.0):.3f}")
            elif 'similarity' in result:
                print(f"     Similarity: {result.get('similarity', 0.0):.3f}")
            
            # Show conflict mappings for cross-domain examples
            if 'conflict_mappings' in result and result['conflict_mappings']:
                print(f"     Conflict mappings: {len(result['conflict_mappings'])} patterns")
                for mapping in result['conflict_mappings'][:2]:
                    print(f"       • {mapping['pattern']}: {mapping['pattern_description'][:50]}...")
            
            # Show case conflicts
            case_conflicts = case.get('conflicts', [])
            if case_conflicts:
                conflict_types = [c.get('type', '') for c in case_conflicts[:3]]
                print(f"     Case conflicts: {', '.join(conflict_types)}")
        
        print(f"\n{'─'*70}")
        print(f"📊 SUMMARY:")
        print(f"{'─'*70}")
        print(f"  Same-domain examples:   {same_domain_count}")
        print(f"  Cross-domain examples:  {cross_domain_count}")
        print(f"  Total:                  {len(results)}")
        
        if cross_domain_count > 0:
            print(f"\n✅ SUCCESS! Cross-domain retrieval is working!")
            print(f"   Found examples from other domains with similar conflict patterns.")
        else:
            print(f"\n⚠️  No cross-domain examples in this batch.")
            print(f"   (This is normal - depends on conflict similarity)")
        
        print("\n" + "="*70)
        print("✓ Cross-domain retrieval test complete!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "="*70)
        print("TROUBLESHOOTING:")
        print("="*70)
        print("If you see collection errors, check that:")
        print("1. ConflictAwareRetriever is properly initialized")
        print("2. ChromaDB databases exist in ../chroma_db/")
        print("3. All required imports are available")
        print("="*70)