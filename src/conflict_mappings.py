"""
Cross-Domain Conflict Mappings - COMPLETE WITH ALL CONFLICTS

Maps conflicts across domains based on universal patterns.
Based on expanded conflict_detector.py with:
- Health: 8 conflicts
- Education: 14 conflicts  
- Travel: 10 conflicts

Universal Patterns:
1. Resource vs Quality: Limited resource conflicts with quality goal
2. Constraint vs Goal: Hard constraint limits goal achievement
3. Facility vs Requirement: Lack of facility limits capability
4. Timeline vs Scope: Time constraint limits scope of work
5. Preference vs Reality: Ideal preference conflicts with practical reality
6. Medical/Special vs Standard: Special conditions require modifications
"""

from typing import Dict, List, Optional


class ConflictMapper:
    """Maps conflicts across domains based on universal patterns"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict:
        """Define universal conflict patterns and domain mappings"""
        
        return {
            # PATTERN 1: Resource vs Quality
            'resource_vs_quality': {
                'description': 'Limited resource (budget/time) conflicts with quality/quantity goal',
                'abstract_strategy': 'Optimize for efficiency: prioritize high-value options within resource constraint',
                'domains': {
                    'health': [
                        'budget_vs_protein',           # Budget limits protein sources
                        'budget_vs_supplements',       # Budget limits supplement options
                        'time_vs_meal_prep'           # Time limits meal preparation
                    ],
                    'education': [
                        'time_vs_courses',            # Time limits course selection
                        'workload_vs_gpa',            # Heavy workload limits GPA
                        'part_time_work_vs_study',    # Work hours limit study time
                        'course_count_vs_workload',   # Course count exceeds capacity
                        'theory_heavy_vs_time',       # Theory courses need more time
                        'exam_schedule_vs_workload'   # Overlapping exams create pressure
                    ],
                    'travel': [
                        'budget_vs_luxury',           # Budget limits luxury options
                        'budget_vs_activities',       # Budget limits activities
                        'group_size_vs_budget',       # Group size increases costs
                        'flight_budget_vs_destination', # Flight costs too high
                        'short_duration_vs_distance'  # Short time for long travel
                    ]
                },
                'resolution_template': 'Focus on {efficient_option} ({low_cost}) instead of {premium_option} ({high_cost}). Prioritize highest value-to-cost ratio.',
                'transfer_confidence': 0.88,
                'examples': {
                    'health': 'Use dal (₹20/kg) instead of protein powder (₹300/month)',
                    'education': 'Take 3 focused courses instead of 5 spread thin',
                    'travel': 'Choose local beaches (₹2000) instead of Maldives (₹80000)'
                }
            },
            
            # PATTERN 2: Constraint vs Goal (Strict Limitation)
            'constraint_vs_goal': {
                'description': 'Hard constraint severely limits ability to achieve goal',
                'abstract_strategy': 'Find alternative paths: identify creative workarounds within constraints',
                'domains': {
                    'health': [
                        'diet_vs_protein',            # Veg diet limits protein
                        'vegan_vs_protein',           # Vegan severely limits protein
                        'medical_condition_vs_diet',  # Medical needs require diet changes
                        'no_kitchen_vs_nutrition'     # No cooking limits nutrition
                    ],
                    'education': [
                        'prerequisites_vs_interests', # Lack of prereqs blocks courses
                        'prerequisites_vs_timeline',  # Missing prereqs delay graduation
                        'math_anxiety_vs_requirements', # Math fear blocks requirements
                        'language_barrier_vs_theory', # Language limits theory courses
                        'prerequisites_vs_interests'  # Prereqs limit choices
                    ],
                    'travel': [
                        'accessibility_vs_remote',    # Accessibility needs vs remote places
                        'family_vs_adventure',        # Kids limit adventure options
                        'weather_vs_timeline'         # Fixed dates conflict with weather
                    ]
                },
                'resolution_template': 'Given constraint {constraint}, achieve {goal} through {alternative_approach}. Accept partial achievement.',
                'transfer_confidence': 0.82,
                'examples': {
                    'health': 'Use plant protein (tofu, lentils) instead of meat',
                    'education': 'Self-study prerequisites concurrently with courses',
                    'travel': 'Choose accessible adventure (zip-lining) over trekking'
                }
            },
            
            # PATTERN 3: Facility vs Requirement
            'facility_vs_requirement': {
                'description': 'Lack of necessary facility/infrastructure limits capability',
                'abstract_strategy': 'Adapt to available facilities: leverage what exists, minimize dependency',
                'domains': {
                    'health': [
                        'no_kitchen_vs_nutrition'     # No cooking facility
                    ],
                    'education': [
                        'language_barrier_vs_theory'  # Language skills lacking
                    ],
                    'travel': [
                        'accessibility_vs_remote',    # Accessibility infrastructure missing
                        'solo_vs_safety'             # Safety infrastructure concerns
                    ]
                },
                'resolution_template': 'Work within {available_facility} by {adaptation_strategy}. Focus on facility-independent approaches.',
                'transfer_confidence': 0.75,
                'examples': {
                    'health': 'Use mess/canteen food, ready-to-eat options',
                    'education': 'Use translated materials, visual learning',
                    'travel': 'Choose guided tours with safety measures'
                }
            },
            
            # PATTERN 4: Timeline vs Scope (Unrealistic Expectations)
            'timeline_vs_scope': {
                'description': 'Fixed timeline conflicts with scope of desired outcome',
                'abstract_strategy': 'Scope reduction: prioritize essential elements, defer non-critical items',
                'domains': {
                    'health': [
                        'extreme_goal_vs_timeline'    # Gain 12kg in 3 months
                    ],
                    'education': [
                        'course_count_vs_workload',   # Too many courses for time
                        'theory_heavy_vs_time',       # Theory needs more time
                        'exam_schedule_vs_workload',  # Exam overlap creates crunch
                        'research_vs_coursework',     # Research time vs courses
                        'multiple_projects_vs_capacity' # Too many projects
                    ],
                    'travel': [
                        'short_duration_vs_distance', # Short trip, far destination
                        'weather_vs_timeline'         # Fixed dates, wrong season
                    ]
                },
                'resolution_template': 'Given timeline {timeframe}, reduce scope to {priority_items}. Focus on high-impact activities first.',
                'transfer_confidence': 0.79,
                'examples': {
                    'health': 'Target 6kg gain (realistic) instead of 12kg',
                    'education': 'Focus on 3 core courses, audit 4th',
                    'travel': 'Visit 2 cities deeply instead of 5 superficially'
                }
            },
            
            # PATTERN 5: Preference vs Reality (Idealism vs Pragmatism)
            'preference_vs_reality': {
                'description': 'Ideal preferences conflict with practical constraints',
                'abstract_strategy': 'Realistic adjustment: find acceptable compromise between ideal and practical',
                'domains': {
                    'health': [
                        'medical_condition_vs_diet'   # Medical needs override preferences
                    ],
                    'education': [
                        'gpa_vs_difficulty',          # Want high GPA + hard courses
                        'specialization_vs_breadth',  # Want depth + breadth
                        'multiple_projects_vs_capacity', # Want all projects
                        'research_vs_coursework'      # Want research + full courses
                    ],
                    'travel': [
                        'luxury_vs_adventure',        # Want luxury + adventure
                        'family_vs_adventure'         # Want family + extreme adventure
                    ]
                },
                'resolution_template': 'Balance {ideal_preference} with {practical_constraint} by {compromise_approach}.',
                'transfer_confidence': 0.71,
                'examples': {
                    'health': 'PCOS diet with occasional treats (80/20 rule)',
                    'education': 'Mix easy courses (GPA) with 1-2 challenging',
                    'travel': 'Comfortable resort + day adventure trips'
                }
            },
            
            # PATTERN 6: Special Condition vs Standard Approach
            'special_vs_standard': {
                'description': 'Special medical/psychological/social condition requires non-standard approach',
                'abstract_strategy': 'Accommodate special needs: modify standard approaches, seek expert guidance',
                'domains': {
                    'health': [
                        'medical_condition_vs_diet',  # Diabetes, PCOS, etc.
                        'vegan_vs_protein',           # Strict dietary philosophy
                        'extreme_goal_vs_timeline'    # Extreme body transformation
                    ],
                    'education': [
                        'math_anxiety_vs_requirements', # Psychological barrier
                        'language_barrier_vs_theory',   # Language challenge
                        'research_vs_coursework'        # Research student needs
                    ],
                    'travel': [
                        'solo_vs_safety',             # Solo female traveler
                        'family_vs_adventure',        # Young children
                        'accessibility_vs_remote'     # Disability considerations
                    ]
                },
                'resolution_template': 'Accommodate {special_condition} by {specialized_approach}. May require expert support.',
                'transfer_confidence': 0.68,
                'examples': {
                    'health': 'PCOS diet: Low GI, high fiber, specific supplements',
                    'education': 'Math anxiety: Start easy, build confidence gradually',
                    'travel': 'Solo female: Join group tours, women-only hostels'
                }
            }
        }
    
    def map_conflict(self, source_conflict: str, source_domain: str, 
                    target_domain: str) -> Optional[Dict]:
        """
        Map a conflict from source domain to target domain
        
        Args:
            source_conflict: Conflict type in source domain
            source_domain: Source domain ('health', 'education', 'travel')
            target_domain: Target domain ('health', 'education', 'travel')
            
        Returns:
            Mapping dict with target conflicts and strategies, or None
        """
        
        if source_domain == target_domain:
            return None  # No cross-domain mapping needed
        
        # Find which pattern this conflict belongs to
        for pattern_name, pattern in self.patterns.items():
            if source_conflict in pattern['domains'].get(source_domain, []):
                # Found the pattern!
                target_conflicts = pattern['domains'].get(target_domain, [])
                
                if not target_conflicts:
                    continue  # Pattern doesn't exist in target domain
                
                return {
                    'source_conflict': source_conflict,
                    'source_domain': source_domain,
                    'target_domain': target_domain,
                    'target_conflicts': target_conflicts,
                    'pattern': pattern_name,
                    'pattern_description': pattern['description'],
                    'abstract_strategy': pattern['abstract_strategy'],
                    'resolution_template': pattern['resolution_template'],
                    'transfer_confidence': pattern['transfer_confidence'],
                    'example_source': pattern['examples'].get(source_domain, ''),
                    'example_target': pattern['examples'].get(target_domain, ''),
                    'adaptation_note': self._generate_adaptation_note(
                        source_conflict, target_conflicts, pattern_name, pattern
                    )
                }
        
        return None  # No mapping found
    
    def _generate_adaptation_note(self, source_conflict: str, 
                                  target_conflicts: List[str], 
                                  pattern: str,
                                  pattern_data: Dict) -> str:
        """Generate human-readable adaptation note"""
        
        source_example = pattern_data['examples'].get('health', '')
        target_example = pattern_data['examples'].get('education', '')
        
        base_notes = {
            'resource_vs_quality': f"Apply efficiency principle from {source_conflict}: prioritize high-value options within limited resources.",
            'constraint_vs_goal': f"Like {source_conflict}, find creative alternatives that work within strict constraints.",
            'facility_vs_requirement': f"Similar to {source_conflict}, adapt requirements to available facilities.",
            'timeline_vs_scope': f"Use scope reduction strategy from {source_conflict}: prioritize essential items.",
            'preference_vs_reality': f"Apply compromise approach from {source_conflict}: balance ideal with practical.",
            'special_vs_standard': f"Like {source_conflict}, accommodate special needs with modified approach."
        }
        
        return base_notes.get(pattern, f"Apply principles from {source_conflict}")
    
    def get_all_mappings(self, source_domain: str, target_domain: str) -> List[Dict]:
        """Get all possible mappings from source domain to target domain"""
        
        mappings = []
        
        for pattern_name, pattern in self.patterns.items():
            source_conflicts = pattern['domains'].get(source_domain, [])
            target_conflicts = pattern['domains'].get(target_domain, [])
            
            if source_conflicts and target_conflicts:
                for source_conflict in source_conflicts:
                    mapping = self.map_conflict(source_conflict, source_domain, target_domain)
                    if mapping:
                        mappings.append(mapping)
        
        return mappings
    
    def calculate_mapping_score(self, source_conflict_type: str, 
                                target_conflict_type: str,
                                source_domain: str, 
                                target_domain: str) -> float:
        """
        Calculate how well source conflict maps to target conflict
        
        Returns:
            Score from 0.0 (no mapping) to 1.0 (perfect mapping)
        """
        
        mapping = self.map_conflict(source_conflict_type, source_domain, target_domain)
        
        if not mapping:
            return 0.0
        
        if target_conflict_type in mapping['target_conflicts']:
            # Direct mapping exists
            return mapping['transfer_confidence']
        
        return 0.0
    
    def explain_mapping(self, source_conflict: str, source_domain: str,
                       target_domain: str, detailed: bool = True) -> str:
        """Generate human-readable explanation of conflict mapping"""
        
        mapping = self.map_conflict(source_conflict, source_domain, target_domain)
        
        if not mapping:
            return f"No cross-domain mapping found for {source_conflict}"
        
        explanation = f"""
CROSS-DOMAIN MAPPING
SOURCE CONFLICT:
  • {source_conflict} ({source_domain})
  
TARGET CONFLICTS:
  • {', '.join(mapping['target_conflicts'][:3])} ({target_domain})
  {f"  • ... and {len(mapping['target_conflicts']) - 3} more" if len(mapping['target_conflicts']) > 3 else ""}

UNIVERSAL PATTERN: {mapping['pattern'].upper().replace('_', ' ')}
  {mapping['pattern_description']}

ABSTRACT STRATEGY:
  {mapping['abstract_strategy']}

RESOLUTION APPROACH:
  {mapping['resolution_template']}
"""
        
        if detailed and 'example_source' in mapping:
            explanation += f"""
CONCRETE EXAMPLES:
  Source ({source_domain}): {mapping['example_source']}
  Target ({target_domain}): {mapping['example_target']}
"""
        
        explanation += f"""
ADAPTATION NOTE:
  {mapping['adaptation_note']}

TRANSFER CONFIDENCE: {mapping['transfer_confidence']:.1%}
"""
        
        return explanation
    
    def get_pattern_summary(self) -> str:
        """Get summary of all patterns and their coverage"""
        
        summary = """
 CROSS-DOMAIN CONFLICT PATTERN SUMMARY 
"""
        
        for pattern_name, pattern in self.patterns.items():
            health_count = len(pattern['domains'].get('health', []))
            edu_count = len(pattern['domains'].get('education', []))
            travel_count = len(pattern['domains'].get('travel', []))
            
            summary += f"""
{pattern_name.upper().replace('_', ' ')}:
  Description: {pattern['description']}
  Coverage: Health={health_count}, Education={edu_count}, Travel={travel_count}
  Confidence: {pattern['transfer_confidence']:.1%}
"""
        
        return summary


# TEST
if __name__ == "__main__":
    mapper = ConflictMapper()
    
    print("="*70)
    print("TESTING COMPLETE CONFLICT MAPPINGS")
    print("="*70)
    
    # Test 1: Show pattern summary
    print(mapper.get_pattern_summary())
    
    # Test 2: Health → Education mappings
    print("\n" + "="*70)
    print("TEST: Health → Education Mappings")
    print("="*70)
    
    health_to_edu = mapper.get_all_mappings('health', 'education')
    print(f"\n✓ Found {len(health_to_edu)} total mappings")
    
    for i, m in enumerate(health_to_edu[:5], 1):
        print(f"\n{i}. {m['source_conflict']} → {m['target_conflicts'][0]}")
        print(f"   Pattern: {m['pattern']}")
        print(f"   Confidence: {m['transfer_confidence']:.1%}")
    
    # Test 3: Detailed explanation
    print("\n" + "="*70)
    print("TEST: Detailed Mapping Explanation")
    print("="*70)
    
    explanation = mapper.explain_mapping('budget_vs_protein', 'health', 'education')
    print(explanation)
    
    # Test 4: Coverage statistics
    print("\n" + "="*70)
    print("TEST: Coverage Statistics")
    print("="*70)
    
    domains = ['health', 'education', 'travel']
    for source in domains:
        for target in domains:
            if source != target:
                mappings = mapper.get_all_mappings(source, target)
                print(f"{source:10s} → {target:10s}: {len(mappings):2d} mappings")
    
    print("\n" + "="*70)
    print("✓ All tests complete!")
    print("="*70)