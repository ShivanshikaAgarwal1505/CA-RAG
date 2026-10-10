from api_key_manager import APIKeyManager
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

class ConstraintExtractor:
    def __init__(self):
        self.api_manager = APIKeyManager()
        self.client = self.api_manager.get_client()
    
    def extract(self, query: str, domain: str):
        """Extract constraints from user query"""
    
        prompt = f"""You are a constraint extraction expert for {domain} domain planning.

User Query: "{query}"

Extract structured constraints following these rules:

HARD CONSTRAINTS = MUST satisfy (cannot be violated):
- Budget limits (e.g., "₹150/day budget" → hard)
- Dietary restrictions (e.g., "vegetarian", "vegan", "gluten-free" → hard)
- Facility access (e.g., "hostel mess", "no kitchen" → hard, these determine what's possible)
- Time limits (e.g., "only 2 hours available" → hard)
- Prerequisites (for education: "must have completed X" → hard)

SOFT CONSTRAINTS = PREFER but flexible (can be compromised):
- Preferences (e.g., "prefer quick meals", "like spicy food" → soft)
- Convenience (e.g., "prefer easy recipes", "less prep time" → soft)
- Taste/quality preferences (e.g., "want tasty food", "organic preferred" → soft)
- Interest areas (for education: "interested in ML" → soft)

GOALS = What user wants to achieve:
- Health outcomes (e.g., "reduce hair fall", "gain muscle")
- Academic outcomes (e.g., "high GPA", "learn CV")
- Experience outcomes (e.g., "relaxing trip", "adventure")

Return ONLY valid JSON (no markdown, no explanation):
{{
"hard_constraints": [
    {{"type": "budget|diet|facility|time|...", "value": "...", "unit": "..."}}
],
"soft_constraints": [
    {{"type": "preference|convenience|taste|...", "value": "...", "strength": 0.0-1.0}}
],
"goals": [
    {{"type": "health|academic|experience|...", "value": "...", "unit": "..."}}
]
}}

CRITICAL: 
- "hostel mess", "no kitchen", "dorm room" = HARD facility constraints
- "prefer quick", "like spicy", "want organic" = SOFT preferences
- For budget/time/numeric values, put the NUMBER in "value" field
"""
    
        response = self.api_manager.call_with_retry(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000
        )
    
        result = response.choices[0].message.content
        
        # Parse JSON
        try:
            # Remove markdown code fences if present
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            constraints = json.loads(result.strip())
            
            # POST-PROCESS: Convert numeric values to proper types
            constraints = self._normalize_constraints(constraints)
            
            return constraints
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Raw response: {result}")
            return None
    
    def _normalize_constraints(self, constraints: dict) -> dict:
        """Normalize constraint values (convert strings to numbers where appropriate)"""
        
        # Process hard constraints
        if 'hard_constraints' in constraints:
            for constraint in constraints['hard_constraints']:
                constraint['value'] = self._convert_value(
                    constraint.get('type', ''),
                    constraint.get('value', '')
                )
        
        # Process soft constraints
        if 'soft_constraints' in constraints:
            for constraint in constraints['soft_constraints']:
                # Ensure strength is a float
                if 'strength' in constraint:
                    try:
                        constraint['strength'] = float(constraint['strength'])
                    except (ValueError, TypeError):
                        constraint['strength'] = 0.5  # Default
        
        return constraints
    
    def _convert_value(self, constraint_type: str, value):
        """Convert constraint value to appropriate type"""
        
        # Types that should be numeric
        numeric_types = ['budget', 'time', 'cost', 'duration', 'age', 'weight', 'height']
        
        if constraint_type in numeric_types:
            # If already a number, return it
            if isinstance(value, (int, float)):
                return value
            
            # If string, try to extract number
            if isinstance(value, str):
                # Remove currency symbols, units, etc.
                clean_value = re.sub(r'[₹$Rs,\s]', '', value)
                
                # Extract first number found
                match = re.search(r'(\d+\.?\d*)', clean_value)
                if match:
                    num_str = match.group(1)
                    try:
                        # Return int if whole number, float otherwise
                        if '.' in num_str:
                            return float(num_str)
                        else:
                            return int(num_str)
                    except ValueError:
                        pass
        
        # Return original value if conversion not needed/failed
        return value


# TEST IT
if __name__ == "__main__":
    extractor = ConstraintExtractor()
    
    print("="*70)
    print("TESTING CONSTRAINT EXTRACTOR")
    print("="*70)
    
    # Test cases
    test_queries = [
        ("22F, hair fall, vegetarian, hostel mess, ₹150/day budget, prefer quick meals", "health"),
        ("22M; Hair fall; Budget ₹150/day; Veg; No kitchen; Bangalore", "health"),
        ("Want to gain muscle, ₹200 budget, non-veg, gym available, prefer high protein", "health"),
    ]
    
    for i, (query, domain) in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}")
        print(f"{'='*70}")
        print(f"Query: {query}")
        print(f"Domain: {domain}")
        
        constraints = extractor.extract(query, domain)
        
        if constraints:
            print("\n✓ Extracted Constraints:")
            print(json.dumps(constraints, indent=2))
            
            # Check if budget was converted to int
            hard_constraints = constraints.get('hard_constraints', [])
            for c in hard_constraints:
                if c['type'] == 'budget':
                    print(f"\n✓ Budget value type: {type(c['value'])} = {c['value']}")
                    if isinstance(c['value'], int):
                        print("  ✅ CORRECT: Budget is an integer!")
                    else:
                        print("  ⚠️  WARNING: Budget is not an integer!")
        else:
            print("\n❌ Failed to extract constraints")