"""
Build few-shot prompts using retrieved cases
"""

from conflict_aware_retrieval import ConflictAwareRetriever
from constraint_extractor import ConstraintExtractor
from conflict_detector import ConflictDetector

class PromptBuilder:
    def __init__(self):
        self.retriever = ConflictAwareRetriever()
        self.extractor = ConstraintExtractor()
        self.detector = ConflictDetector()
    
    def build_prompt(self, query: str, domain: str, k: int = 3):
        """Build few-shot prompt with retrieved examples"""
    
        # 1. Extract constraints
        constraints = self.extractor.extract(query, domain)
    
        # 2. BUILD COMPLETE CASE OBJECT (needed for conflict detection!)
        query_case = {
            'query': query,           # ← CRITICAL!
            'domain': domain,
            'constraints': constraints
        }
    
        # 3. Detect conflicts (pass COMPLETE case object)
        conflicts = self.detector.detect_conflicts(query_case)
    
        # 4. Add conflicts to case object
        query_case['conflicts'] = conflicts
    
        # 5. Retrieve similar cases
        retrieved = self.retriever.retrieve(query_case, domain, k, method='hybrid')
    
        # 6. Build prompt
        prompt = self._construct_prompt(query, constraints, conflicts, retrieved, domain)
    
        return prompt, constraints, conflicts, retrieved
    
    def _construct_prompt(self, query, constraints, conflicts, retrieved, domain):
        """Construct the actual prompt text"""
        
        # Domain-specific system message
        domain_expertise = {
            'health': 'nutrition and health planning',
            'education': 'academic course planning',
            'travel': 'travel itinerary planning'
        }
        
        prompt = f"""You are an expert {domain_expertise.get(domain, domain)} assistant.

QUERY:
{query}

CONSTRAINT ANALYSIS:
"""
        # Add hard constraints
        hard_constraints = constraints.get('hard_constraints', [])
        if hard_constraints:
            prompt += "\nHard Constraints (MUST satisfy):\n"
            for c in hard_constraints:
                value = c.get('value', 'N/A')
                unit = c.get('unit', '')
                if unit and unit != 'none' and unit != 'null':
                    prompt += f"  • {c['type']}: {value} {unit}\n"
                else:
                    prompt += f"  • {c['type']}: {value}\n"
        
        # Add soft constraints
        soft_constraints = constraints.get('soft_constraints', [])
        if soft_constraints:
            prompt += "\nSoft Constraints (PREFER to satisfy):\n"
            for c in soft_constraints:
                value = c.get('value', 'N/A')
                strength = c.get('strength', 0.5)
                prompt += f"  • {c['type']}: {value} (importance: {strength:.1f}/1.0)\n"
        
        # Add goals
        goals = constraints.get('goals', [])
        if goals:
            prompt += "\nGoals:\n"
            for g in goals:
                prompt += f"  • {g.get('value', 'N/A')}\n"
        
        # Add conflicts
        if conflicts:
            prompt += "\n" + "⚠️ " * 20 + "\n"
            prompt += "DETECTED CONFLICTS (require trade-offs):\n"
            prompt += "⚠️ " * 20 + "\n"
            for conf in conflicts:
                prompt += f"\n  ⚠️  {conf['type'].upper()} (severity: {conf['severity']:.2f})\n"
                prompt += f"      {conf['description']}\n"
                if 'resolution_strategy' in conf:
                    prompt += f"      Strategy hint: {conf['resolution_strategy']}\n"
        
        # Add retrieved examples
        if retrieved:
            prompt += "\n" + "="*70 + "\n"
            prompt += "SIMILAR RESOLVED CASES (learn from these):\n"
            prompt += "="*70 + "\n\n"
            
            for i, item in enumerate(retrieved, 1):
                case = item['case']
                case_id = case.get('id', case.get('case_id', 'Unknown'))
                
                prompt += f"[EXAMPLE {i}] - Case {case_id}\n"
                prompt += "-" * 70 + "\n"
                
                # Query
                case_query = case.get('query', 'N/A')
                if len(case_query) > 150:
                    case_query = case_query[:150] + "..."
                prompt += f"Problem: {case_query}\n"
                
                # Show case conflicts
                case_conflicts = case.get('conflicts', [])
                if case_conflicts:
                    prompt += "\nConflicts faced: "
                    prompt += ", ".join([c['type'] for c in case_conflicts]) + "\n"
                
                # Show solution
                solution = case.get('solution', 'No solution available')
                # Limit solution length to keep prompt manageable
                if len(solution) > 400:
                    solution = solution[:400] + "..."
                prompt += f"\nSolution:\n{solution}\n"
                
                # Resolution quality
                resolution_quality = case.get('resolution_quality', 0)
                if resolution_quality > 0:
                    prompt += f"\nResolution Quality: {resolution_quality:.1f}/1.0\n"
                
                prompt += "\n" + "="*70 + "\n\n"
        
        # Final instruction
        prompt += """
YOUR TASK:
Based on the similar resolved cases above, generate a practical and feasible solution for the query.

REQUIREMENTS:
1. ✅ MUST satisfy ALL hard constraints (non-negotiable)
2. ⚡ Address each identified conflict with practical strategies
3. 📋 Provide specific, actionable recommendations
4. 💡 Explain trade-offs when conflicts cannot be fully resolved
5. 💰 Stay within budget and other resource constraints
6. 🎯 Prioritize based on soft constraint importance scores

OUTPUT FORMAT:

**SOLUTION PLAN:**
[Your detailed day-by-day or step-by-step plan]

**CONFLICT RESOLUTION:**
For each conflict detected, explain your resolution strategy:
- [CONFLICT_NAME]: [How you resolved it]
Example:
- BUDGET_VS_PROTEIN: Prioritized affordable protein sources like dal (₹80) instead of expensive whey protein (₹300)
- DIET_VS_PROTEIN: Focused on vegetarian high-protein foods (lentils, paneer, nuts)

**SPECIFIC TRADE-OFFS:**
List concrete items you chose and rejected:
- CHOSE: [Specific item/strategy] INSTEAD OF: [Alternative you rejected]
Example:
- CHOSE: Dal-based protein (affordable) INSTEAD OF: Protein supplements (expensive)
- CHOSE: Mess optimization INSTEAD OF: Home cooking (no kitchen)

**FEASIBILITY SCORE:** [X/10]
[Brief justification]

Generate your solution now:
"""
        
        return prompt

def main():
    """Test the prompt builder"""
    builder = PromptBuilder()
    
    # Test query
    test_query = "22M; Hair fall; Budget ₹150/day; Veg; No kitchen; Bangalore"
    
    print("\n" + "="*70)
    print("TESTING PROMPT BUILDER")
    print("="*70)
    print(f"\nTest Query: {test_query}")
    print(f"Domain: health\n")
    
    # Build prompt
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
    
    # Save to file
    with open('../results/sample_prompt.txt', 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    print("\n" + "="*70)
    print("✓ Prompt saved to results/sample_prompt.txt")
    print("="*70)


if __name__ == "__main__":
    main()