"""
Compare 4 Planning Systems:
1. Zero-shot LLM (no examples)
2. Semantic RAG (keyword retrieval)
3. Conflict-Aware RAG (your innovation)
4. Hybrid RAG (conflict + semantic)
5. Cross-Domain RAG (conflict pattern transfer)
"""

import os
from api_key_manager import APIKeyManager
from constraint_extractor import ConstraintExtractor
from conflict_detector import ConflictDetector
from conflict_aware_retrieval import ConflictAwareRetriever
from prompt_builder import PromptBuilder
from solution_generator import SolutionGenerator
from cross_domain_retriever import CrossDomainRetriever
from conflict_mappings import ConflictMapper
import json
from typing import Dict, List

class SystemComparison:
    """Run and compare all 5 systems"""
    
    def __init__(self):
        self.api_manager = APIKeyManager()
        self.client = self.api_manager.get_client()
        self.extractor = ConstraintExtractor()
        self.detector = ConflictDetector()
        self.retriever = ConflictAwareRetriever()
        self.prompt_builder = PromptBuilder()
        self.solution_generator = SolutionGenerator()
        self.cross_domain_retriever = CrossDomainRetriever()
        self.conflict_mapper = ConflictMapper()
    
    def run_all_systems(self, test_case: Dict) -> Dict[str, Dict]:
        query = test_case['query']
        domain = test_case['domain']
        
        print(f"\n{'='*80}")
        print(f"Running all systems on: {test_case['id']}")
        print(f"Query: {query[:60]}...")
        print(f"{'='*80}")
        
        results = {}
        
        print("\n[1/5] Running ZERO-SHOT system...")
        results['zero_shot'] = self._run_zero_shot(query, domain)
        
        print("[2/5] Running SEMANTIC RAG system...")
        results['semantic'] = self._run_semantic(query, domain)
        
        print("[3/5] Running CONFLICT-AWARE RAG system...")
        results['conflict_aware'] = self._run_conflict_aware(query, domain)
        
        print("[4/5] Running HYBRID RAG system...")
        results['hybrid'] = self._run_hybrid(query, domain)
        
        print("[5/5] Running CROSS-DOMAIN RAG system...")
        results['cross_domain'] = self._run_cross_domain(query, domain)
        
        print("✓ All systems complete\n")
        
        return results
    
    def _run_zero_shot(self, query: str, domain: str) -> Dict:
        """
        System 1: Zero-shot LLM (no examples)
        
        Just prompt the LLM directly without any examples
        """
        # Build minimal prompt
        prompt = f"""You are an expert {domain} planning assistant.

USER QUERY:
{query}

Generate a practical and feasible solution for this query.

Provide your response in this format:

**SOLUTION PLAN:**
[Your detailed plan]

**TRADE-OFFS:**
[Any compromises made]

**FEASIBILITY SCORE:** [X/10]
[Brief justification]
"""
        
        # Call LLM
        response = self.api_manager.call_with_retry(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are an expert {domain} planning assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        solution_text = response.choices[0].message.content
        
        return {
            'query': query,
            'domain': domain,
            'system': 'zero_shot',
            'solution': solution_text,
            'num_examples': 0,
            'method': 'zero-shot'
        }
    
    def _run_semantic(self, query: str, domain: str) -> Dict:
        """
        System 2: Semantic RAG (keyword-based retrieval)
        
        Retrieve examples based on text similarity only
        """
        # Extract constraints (needed for building case object)
        constraints = self.extractor.extract(query, domain)
        
        # Build query case
        query_case = {
            'query': query,
            'domain': domain,
            'constraints': constraints
        }
        
        # Retrieve using SEMANTIC method
        retrieved = self.retriever.retrieve(query_case, domain, k=3, method='semantic')
        
        # Build prompt manually (similar to prompt_builder but semantic)
        prompt = self._build_semantic_prompt(query, domain, constraints, retrieved)
        
        # Call LLM
        response = self.api_manager.call_with_retry(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are an expert {domain} planning assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        solution_text = response.choices[0].message.content
        
        return {
            'query': query,
            'domain': domain,
            'system': 'semantic',
            'solution': solution_text,
            'num_examples': len(retrieved),
            'retrieved_cases': [r['case'].get('id', r['case'].get('case_id')) for r in retrieved],
            'method': 'semantic'
        }
    
    def _run_conflict_aware(self, query: str, domain: str) -> Dict:
        """
        System 3: Conflict-Aware RAG (your innovation)
        
        Use the full solution_generator with conflict-aware retrieval
        """
        result = self.solution_generator.generate_solution(query, domain, k=3)
        result['system'] = 'conflict_aware'
        result['method'] = 'conflict-aware'
        return result
    
    def _run_hybrid(self, query: str, domain: str) -> Dict:
        """
        System 4: Hybrid RAG (conflict + semantic)
        
        Use hybrid retrieval method
        """
        # Extract constraints
        constraints = self.extractor.extract(query, domain)
        
        # Build query case
        query_case = {
            'query': query,
            'domain': domain,
            'constraints': constraints
        }
        
        # Detect conflicts
        conflicts = self.detector.detect_conflicts(query_case)
        query_case['conflicts'] = conflicts
        
        # Retrieve using HYBRID method
        retrieved = self.retriever.retrieve(query_case, domain, k=3, method='hybrid')
        
        # Build prompt
        prompt = self._build_hybrid_prompt(query, domain, constraints, conflicts, retrieved)
        
        # Call LLM
        response = self.api_manager.call_with_retry(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are an expert {domain} planning assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        solution_text = response.choices[0].message.content
        
        return {
            'query': query,
            'domain': domain,
            'system': 'hybrid',
            'solution': solution_text,
            'num_examples': len(retrieved),
            'retrieved_cases': [r['case'].get('id', r['case'].get('case_id')) for r in retrieved],
            'conflicts': conflicts,
            'method': 'hybrid'
        }
    
    def _run_cross_domain(self, query: str, domain: str) -> Dict:
        """System 5: Cross-Domain RAG with conflict pattern transfer"""
        
        # Extract constraints
        constraints = self.extractor.extract(query, domain)
        
        # Build query case
        query_case = {
            'query': query,
            'domain': domain,
            'constraints': constraints
        }
        
        # Detect conflicts
        conflicts = self.detector.detect_conflicts(query_case)
        query_case['conflicts'] = conflicts
        
        # Retrieve with cross-domain support
        retrieved = self.cross_domain_retriever.retrieve_cross_domain(
            query_case, 
            domain, 
            k=3,
            allow_domains=['health', 'education', 'travel'],
            cross_domain_ratio=0.33  # 1 cross-domain, 2 same-domain
        )
        
        # Build cross-domain prompt
        prompt = self._build_cross_domain_prompt(
            query, domain, constraints, conflicts, retrieved
        )
        
        # Call LLM
        response = self.api_manager.call_with_retry(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are an expert {domain} planning assistant with cross-domain learning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        solution_text = response.choices[0].message.content
        
        # Count cross-domain examples
        cross_domain_count = sum(1 for r in retrieved 
                                 if r.get('source_domain', domain) != domain)
        
        return {
            'query': query,
            'domain': domain,
            'system': 'cross_domain',
            'solution': solution_text,
            'num_examples': len(retrieved),
            'cross_domain_count': cross_domain_count,
            'retrieved_cases': [r['case'].get('id', 'unknown') for r in retrieved],
            'method': 'cross-domain'
        }
    
    def _build_semantic_prompt(self, query: str, domain: str, 
                               constraints: Dict, retrieved: List[Dict]) -> str:
        """Build prompt for semantic RAG system"""
        
        prompt = f"""You are an expert {domain} planning assistant.

QUERY:
{query}

Here are some similar cases for reference:

"""
        # Add examples
        for i, item in enumerate(retrieved, 1):
            case = item['case']
            case_query = case.get('query', 'N/A')
            solution = case.get('solution', 'N/A')
            
            if len(case_query) > 150:
                case_query = case_query[:150] + "..."
            if len(solution) > 300:
                solution = solution[:300] + "..."
            
            prompt += f"""
[EXAMPLE {i}]
Problem: {case_query}
Solution: {solution}

"""
        
        prompt += """
Based on the examples above, generate a practical solution for the query.

**SOLUTION PLAN:**
[Your detailed plan]

**TRADE-OFFS:**
[Any compromises]

**FEASIBILITY SCORE:** [X/10]
[Justification]
"""
        
        return prompt
    
    def _build_hybrid_prompt(self, query: str, domain: str, constraints: Dict,
                            conflicts: List[Dict], retrieved: List[Dict]) -> str:
        """Build prompt for hybrid system (similar to conflict-aware)"""
        
        # Use the PromptBuilder's construct method
        prompt = self.prompt_builder._construct_prompt(
            query, constraints, conflicts, retrieved, domain
        )
        
        return prompt
    
    def _build_cross_domain_prompt(self, query: str, domain: str, 
                                   constraints: Dict, conflicts: List[Dict],
                                   retrieved: List[Dict]) -> str:
        """Build prompt highlighting cross-domain transfer"""
        
        # Start with standard structure
        prompt = f"""You are an expert {domain} planning assistant with cross-domain pattern recognition.

QUERY:
{query}

CONSTRAINT ANALYSIS:
"""
        
        # Add constraints
        hard = constraints.get('hard_constraints', [])
        if hard:
            prompt += "\nHard Constraints (MUST satisfy):\n"
            for c in hard:
                prompt += f"  • {c.get('type')}: {c.get('value')}\n"
        
        soft = constraints.get('soft_constraints', [])
        if soft:
            prompt += "\nSoft Constraints (Prefer to satisfy):\n"
            for c in soft:
                prompt += f"  • {c.get('type')}: {c.get('value')} (weight: {c.get('weight', 0.5)})\n"
        
        goals = constraints.get('goals', [])
        if goals:
            prompt += "\nGoals:\n"
            for g in goals:
                prompt += f"  • {g}\n"
        
        # Add conflicts
        if conflicts:
            prompt += "\n" + "⚠️  "*20 + "\n"
            prompt += "DETECTED CONFLICTS (require trade-offs):\n"
            prompt += "⚠️  "*20 + "\n\n"
            
            for conflict in conflicts:
                prompt += f"""  ⚠️  {conflict['type'].upper().replace('_', ' ')} (severity: {conflict['severity']:.2f})
      {conflict['description']}

"""
        
        # Add examples with cross-domain annotations
        prompt += "\n" + "="*70 + "\n"
        prompt += "SIMILAR RESOLVED CASES (including cross-domain patterns):\n"
        prompt += "="*70 + "\n\n"
        
        for i, item in enumerate(retrieved, 1):
            case = item['case']
            source_domain = item.get('source_domain', domain)
            
            # Domain label
            domain_label = ""
            cross_domain_note = ""
            if source_domain != domain:
                domain_label = f" [Cross-domain: {source_domain} → {domain}]"
                cross_domain_note = " ⭐ CROSS-DOMAIN PATTERN"
            
            prompt += f"""[EXAMPLE {i}]{domain_label}{cross_domain_note}
----------------------------------------------------------------------
Problem ({source_domain}): {case.get('query', 'N/A')[:150]}...

"""
            
            # Show conflicts
            case_conflicts = case.get('conflicts', [])
            if case_conflicts:
                conflict_types = [c.get('type', '') for c in case_conflicts]
                prompt += f"Conflicts: {', '.join(conflict_types)}\n\n"
            
            # Show solution excerpt
            solution = case.get('solution', 'N/A')
            if len(solution) > 350:
                solution = solution[:350] + "..."
            prompt += f"Solution:\n{solution}\n\n"
            
            # Add cross-domain explanation
            if source_domain != domain:
                mappings = item.get('conflict_mappings', [])
                if mappings:
                    prompt += "⭐ CROSS-DOMAIN INSIGHT:\n"
                    for mapping in mappings[:2]:  # Show up to 2 mappings
                        prompt += f"  Pattern: {mapping['pattern_description']}\n"
                        prompt += f"  Strategy: {mapping['abstract_strategy']}\n"
                        if 'example_target' in mapping:
                            prompt += f"  Example: {mapping['example_target']}\n"
                    prompt += "\n"
        
        # Add task instructions
        prompt += "="*70 + "\n\n"
        prompt += """YOUR TASK:
Based on the examples above (including cross-domain patterns), generate a practical 
and feasible solution. Learn from both same-domain successes and cross-domain strategies.

KEY REQUIREMENTS:
1. ✅ MUST satisfy ALL hard constraints
2. ⚡ Address each conflict with practical strategies
3. 📋 Learn from same-domain examples
4. 🌍 Adapt strategies from cross-domain patterns where applicable
5. 💰 Stay within all resource constraints

OUTPUT FORMAT:

**SOLUTION PLAN:**
[Your detailed plan]

**CONFLICT RESOLUTION:**
[How you addressed each conflict, including strategies learned from examples]

**CROSS-DOMAIN INSIGHTS:** (if applicable)
[What strategies were adapted from other domains and how they apply]

**TRADE-OFFS MADE:**
[What was compromised and why]

**FEASIBILITY SCORE:** [X/10]
[Brief justification]

Generate your solution now:
"""
        
        return prompt


# TEST
if __name__ == "__main__":
    comparator = SystemComparison()
    
    # Test on one query
    test_case = {
        'id': 'TEST_H01',
        'domain': 'health',
        'query': '19F; Anemia (Hb: 9.2 g/dL); Budget ₹100/day; Veg; Hostel mess; No cooking',
        'expected_conflicts': ['budget_vs_protein', 'diet_vs_protein']
    }
    
    print("\n" + "="*80)
    print("TESTING SYSTEM COMPARISON")
    print("="*80)
    
    results = comparator.run_all_systems(test_case)
    
    # Print summaries
    for system_name, result in results.items():
        print(f"\n{'='*80}")
        print(f"SYSTEM: {system_name.upper()}")
        print(f"{'='*80}")
        print(f"Solution length: {len(result['solution'])} characters")
        print(f"Examples used: {result.get('num_examples', 0)}")
        if 'retrieved_cases' in result:
            print(f"Retrieved: {result['retrieved_cases']}")
        print(f"\nSolution preview:")
        print(result['solution'][:300] + "...")
    
    print("\n" + "="*80)
    print("✓ Test complete")
    print("="*80)