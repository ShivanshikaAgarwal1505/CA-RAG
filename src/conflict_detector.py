"""
ENHANCED Conflict Detector - ALL DOMAINS
Adds comprehensive rules for education and travel
"""
import re
from typing import List, Dict

class ConflictDetector:
    """Detects conflicts between constraints in planning cases"""
    
    def __init__(self):
        self.health_rules = self._init_health_rules()
        self.education_rules = self._init_education_rules()
        self.travel_rules = self._init_travel_rules()
    
    def _init_health_rules(self) -> List[Dict]:
        """Health domain conflict rules"""
        return [
            {
                'name': 'budget_vs_protein',
                'severity': 0.8,
                'check': lambda case: self._check_budget_protein(case),
                'description': 'Low budget conflicts with high protein requirement'
            },
            {
                'name': 'budget_vs_supplements',
                'severity': 0.7,
                'check': lambda case: self._check_budget_supplements(case),
                'description': 'Budget constraints conflict with supplement needs'
            },
            {
                'name': 'no_kitchen_vs_nutrition',
                'severity': 0.6,
                'check': lambda case: self._check_kitchen_nutrition(case),
                'description': 'No cooking facility limits nutritional options'
            },
            {
                'name': 'time_vs_meal_prep',
                'severity': 0.5,
                'check': lambda case: self._check_time_prep(case),
                'description': 'Time constraint conflicts with meal preparation needs'
            },
            {
                'name': 'diet_vs_protein',
                'severity': 0.7,
                'check': lambda case: self._check_diet_protein(case),
                'description': 'Dietary restrictions limit protein sources'
            },
            {
            'name': 'vegan_vs_protein',
            'severity': 0.85,
            'check': lambda case: self._check_vegan_protein(case),
            'description': 'Vegan diet severely limits protein sources'
        },
        {
            'name': 'medical_condition_vs_diet',
            'severity': 0.9,
            'check': lambda case: self._check_medical_diet(case),
            'description': 'Medical condition requires specific diet modifications'
        },
        {
            'name': 'extreme_goal_vs_timeline',
            'severity': 0.95,
            'check': lambda case: self._check_unrealistic_goals(case),
            'description': 'Goal timeline is unrealistic given constraints'
        }
        ]
    
    def _get_constraint_value(self, constraints: List[Dict], constraint_type: str):
        """Extract value from constraint by type"""
        for c in constraints:
            if c.get('type') == constraint_type:
                val = c.get('value')
                if isinstance(val, str) and val.replace('.', '').isdigit():
                    return float(val)
                return val
        return None
    
    def _get_search_text(self, case: Dict) -> str:
        """Get searchable text from case (query + goals)"""
        query = case.get('query', '').lower()
        goals = case.get('constraints', {}).get('goals', [])
        goals_text = ' '.join(str(g) for g in goals).lower()
        return query + ' ' + goals_text
    
    # ============= HEALTH RULES =============
    
    def _check_budget_protein(self, case: Dict) -> bool:
        """Check budget vs protein needs"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        budget = self._get_constraint_value(hard, 'budget')
        
        if budget and budget < 200:
            text = self._get_search_text(case)
            keywords = ['protein', 'muscle', 'hair fall', 'hair loss', 
                       'anemia', 'fatigue', 'iron', 'weight gain', 
                       'underweight', 'gym', 'workout', 'bulking']
            return any(kw in text for kw in keywords)
        return False
    
    def _check_budget_supplements(self, case: Dict) -> bool:
        """Check budget vs supplement needs"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        budget = self._get_constraint_value(hard, 'budget')
        
        if budget and budget < 250:
            text = self._get_search_text(case)
            keywords = ['biotin', 'supplement', 'vitamin', 'omega', 
                       'protein powder', 'whey', 'creatine', 'no supplements']
            return any(kw in text for kw in keywords)
        return False
    
    def _check_kitchen_nutrition(self, case: Dict) -> bool:
        """Check no kitchen vs nutritional needs"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        facility = self._get_constraint_value(hard, 'facility')
        
        if facility and 'no kitchen' in str(facility).lower():
            text = self._get_search_text(case)
            complex_goals = ['weight gain', 'muscle', 'anemia', 'pcos', 
                            'diabetes', 'cholesterol', 'thyroid', 'nutrition',
                            'bulking', 'cutting', 'diet plan']
            return any(goal in text for goal in complex_goals)
        return False
    
    def _check_time_prep(self, case: Dict) -> bool:
        """Check time constraint vs meal prep"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        time = self._get_constraint_value(hard, 'time')
        
        if time and time < 20:
            text = self._get_search_text(case)
            complex = ['meal prep', 'specific diet', 'muscle gain', 
                      'weight gain', 'bodybuilding', 'custom plan']
            return any(c in text for c in complex)
        return False
    
    def _check_diet_protein(self, case: Dict) -> bool:
        """Check veg diet vs protein goals"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        diet = self._get_constraint_value(hard, 'diet')
        
        if diet and ('veg' in str(diet).lower() or 'vegetarian' in str(diet).lower()):
            text = self._get_search_text(case)
            protein_goals = ['muscle', 'protein', 'weight gain', 
                            'strength', 'gym', 'workout', 'bodybuilding',
                            'bulking', '60g', '70g', '80g', '90g', '100g']
            return any(goal in text for goal in protein_goals)
        return False
    
    def _check_vegan_protein(self, case: Dict) -> bool:
        """Check vegan diet + high protein need"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        diet = self._get_constraint_value(hard, 'diet')
    
        if diet and 'vegan' in str(diet).lower():
            text = self._get_search_text(case)
            protein_needs = ['protein', 'muscle', 'strength', 'gain', 'bodybuilding']
            return any(word in text for word in protein_needs)
        return False

    def _check_medical_diet(self, case: Dict) -> bool:
        """Check medical condition requiring specific diet"""
        text = self._get_search_text(case)
        conditions = ['diabetes', 'pcos', 'hypertension', 'thyroid', 'kidney', 'anemia']
        return any(condition in text for condition in conditions)

    def _check_unrealistic_goals(self, case: Dict) -> bool:
        """Check if goal is unrealistic (e.g., '12kg in 3 months')"""
        text = self._get_search_text(case)
    
        # Pattern: large number + unit + short timeframe
        unrealistic_patterns = [
            r'(\d+)\s*kg.*(\d+)\s*months?',
            r'gain\s+(\d+).*(\d+)\s*months?',
        ]
    
        for pattern in unrealistic_patterns:
            match = re.search(pattern, text)
            if match:
                amount = int(match.group(1))
                timeframe = int(match.group(2))
            
                # 12kg in 3 months = 4kg/month (unrealistic)
                if amount / timeframe > 3:
                    return True
        return False
    
    # ============= EDUCATION RULES =============
    
    def _init_education_rules(self) -> List[Dict]:
        """Education domain conflict rules - ENHANCED"""
        return [
             {
            'name': 'workload_vs_gpa',
            'severity': 0.85,
            'check': lambda case: self._check_workload_gpa(case),
            'description': 'Heavy course workload conflicts with high GPA target'
        },
        {
            'name': 'prerequisites_vs_timeline',
            'severity': 0.9,
            'check': lambda case: self._check_prerequisites_timeline(case),
            'description': 'Missing prerequisites conflicts with graduation timeline'
        },
        {
            'name': 'theory_heavy_vs_time',
            'severity': 0.7,
            'check': lambda case: self._check_theory_time(case),
            'description': 'Theory-heavy courses conflict with time constraints'
        },
        {
            'name': 'multiple_projects_vs_capacity',
            'severity': 0.75,
            'check': lambda case: self._check_projects_capacity(case),
            'description': 'Multiple project-based courses exceed student capacity'
        },
        {
            'name': 'math_anxiety_vs_requirements',
            'severity': 0.8,
            'check': lambda case: self._check_math_anxiety(case),
            'description': 'Math-heavy requirements conflict with student anxiety/weakness'
        },
        {
            'name': 'exam_schedule_vs_workload',
            'severity': 0.65,
            'check': lambda case: self._check_exam_schedule(case),
            'description': 'Overlapping exam schedules create workload conflicts'
        },
        {
            'name': 'language_barrier_vs_theory',
            'severity': 0.7,
            'check': lambda case: self._check_language_theory(case),
            'description': 'Language barrier conflicts with theory-heavy content'
        },
        {
            'name': 'part_time_work_vs_study',
            'severity': 0.85,
            'check': lambda case: self._check_work_study(case),
            'description': 'Part-time work hours conflict with study requirements'
        },
        {
            'name': 'specialization_vs_breadth',
            'severity': 0.6,
            'check': lambda case: self._check_specialization_breadth(case),
            'description': 'Specialization focus conflicts with breadth requirements'
        },
        {
            'name': 'research_vs_coursework',
            'severity': 0.8,
            'check': lambda case: self._check_research_coursework(case),
            'description': 'Research commitments conflict with coursework load'
        },
        {
                'name': 'course_count_vs_workload',
                'severity': 0.8,
                'check': lambda case: self._check_course_workload(case),
                'description': 'Course count conflicts with workload constraint'
            },
            {
                'name': 'gpa_vs_difficulty',
                'severity': 0.7,
                'check': lambda case: self._check_gpa_difficulty(case),
                'description': 'GPA goal conflicts with difficult/interesting courses'
            },
            {
                'name': 'time_vs_courses',
                'severity': 0.9,
                'check': lambda case: self._check_time_courses(case),
                'description': 'Limited time conflicts with course requirements'
            },
            {
                'name': 'prerequisites_vs_interests',
                'severity': 0.6,
                'check': lambda case: self._check_prereq_interest(case),
                'description': 'Lack of prerequisites limits interesting course options'
            }
        ]
    
    def _check_course_workload(self, case: Dict) -> bool:
        """Check if course count conflicts with workload limit"""
        text = self._get_search_text(case)
        
        # Check for high course count (5+) with low workload (<20hrs)
        high_count = any(word in text for word in ['5 courses', '6 courses', '7 courses', 'exactly 5'])
        low_workload = any(word in text for word in ['15hrs', '12hrs', '10hrs', 'max 20', 'max 15'])
        
        return high_count and low_workload
    
    def _check_gpa_difficulty(self, case: Dict) -> bool:
        """Check if high GPA goal conflicts with course difficulty"""
        text = self._get_search_text(case)
        
        # High GPA target
        high_gpa = any(word in text for word in ['8.5', '9.0', '8+', 'high gpa', 'need gpa'])
        
        # Difficult/interesting courses mentioned
        difficult = any(word in text for word in ['deep learning', 'nlp', 'advanced', 
                                                  'research', 'theory', 'difficult',
                                                  'machine learning', 'computer vision'])
        
        return high_gpa and difficult
    
    def _check_time_courses(self, case: Dict) -> bool:
        """Check if time constraint conflicts with course load"""
        text = self._get_search_text(case)
        
        # Low time available
        low_time = any(word in text for word in ['15hrs', '12hrs', '10hrs', 'max 15', 'max 20'])
        
        # Multiple courses or rigorous courses
        many_courses = any(word in text for word in ['4 courses', '5 courses', '6 courses'])
        
        return low_time and many_courses
    
    def _check_prereq_interest(self, case: Dict) -> bool:
        """Check if lack of prereqs limits interesting options"""
        text = self._get_search_text(case)
        
        # No prerequisites
        no_prereq = any(word in text for word in ['no prerequisites', 'basic only', 
                                                  'beginner', 'no prereq'])
        
        # Wants advanced/interesting topics
        advanced = any(word in text for word in ['ai', 'ml', 'deep learning', 'advanced',
                                                'research', 'cv', 'nlp'])
        
        return no_prereq and advanced
    
    def _check_workload_gpa(self, case: Dict) -> bool:
        """Check heavy workload vs high GPA target"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        soft = case.get('constraints', {}).get('soft_constraints', [])
    
        # Check course count
        course_count = 0
        for c in hard:
            if c.get('type') == 'courses':
                val = c.get('value', 0)
                if isinstance(val, int):
                    course_count = val
                elif isinstance(val, str):
                    # Extract number like "4 courses" or "exactly 5"
                    match = re.search(r'(\d+)', str(val))
                    if match:
                        course_count = int(match.group(1))
    
        # Check GPA preference
        text = self._get_search_text(case)
        high_gpa = any(word in text for word in ['gpa', 'high gpa', '3.8', '3.9', '4.0', 'gpa friendly'])
    
        # Conflict if 5+ courses AND high GPA preference
        return course_count >= 5 and high_gpa

    def _check_prerequisites_timeline(self, case: Dict) -> bool:
        """Check missing prerequisites vs graduation timeline"""
        text = self._get_search_text(case)
    
        # Keywords for prerequisite issues
        prereq_issues = ['failed', 'missing prerequisite', 'prerequisite block', 
                         'retake', 'blocked', 'cannot take']
    
        # Keywords for urgent timeline
        urgent = ['must graduate', 'final year', 'final semester', 
                  'last semester', 'graduation timeline']
    
        has_prereq_issue = any(word in text for word in prereq_issues)
        has_urgent_timeline = any(word in text for word in urgent)
    
        return has_prereq_issue and has_urgent_timeline

    def _check_theory_time(self, case: Dict) -> bool:
        """Check theory-heavy courses vs time constraints"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        text = self._get_search_text(case)
    
        # Check for time constraint
        time_value = self._get_constraint_value(hard, 'time')
        has_time_limit = time_value and time_value < 20  # Less than 20 hrs/week
    
        # Check for theory-heavy courses
        theory_keywords = ['theory', 'theoretical', 'algorithms', 
                          'mathematics', 'proofs', 'derivations']
        has_theory = any(word in text for word in theory_keywords)
    
        return has_time_limit and has_theory

    def _check_projects_capacity(self, case: Dict) -> bool:
        """Check multiple project courses vs student capacity"""
        text = self._get_search_text(case)
        soft = case.get('constraints', {}).get('soft_constraints', [])

        # Count project mentions
        project_count = text.count('project')
    
        # Check for capacity concerns
        capacity_issues = ['limited time', 'part-time', 'working', 
                          'internship', 'research']
        has_capacity_issue = any(word in text for word in capacity_issues)
    
        # Also check soft constraints for project preference strength
        high_project_preference = False
        for c in soft:
            if 'project' in str(c.get('value', '')).lower():
                strength = c.get('strength', 0)
                if strength > 0.7:
                    high_project_preference = True
    
        return (project_count >= 3 or high_project_preference) and has_capacity_issue

    def _check_math_anxiety(self, case: Dict) -> bool:
        """Check math-heavy requirements vs student weakness"""
        text = self._get_search_text(case)
        hard = case.get('constraints', {}).get('hard_constraints', [])
    
        # Math weakness indicators
        math_weak = ['math anxiety', 'weak in math', 'avoid math', 
                     'struggles with', 'poor at math', 'linear algebra']
        has_weakness = any(word in text for word in math_weak)
    
        # Math requirement indicators
        math_required = ['ml', 'machine learning', 'deep learning', 
                        'ai', 'statistics', 'probability']
        needs_math = any(word in text for word in math_required)
    
        return has_weakness and needs_math

    def _check_exam_schedule(self, case: Dict) -> bool:
        """Check overlapping exams vs workload"""
        text = self._get_search_text(case)
    
        # Exam-heavy indicators
        exam_heavy = ['exam heavy', 'multiple exams', '4-5 exams', 
                      'exam overload', 'exam schedule']
    
        # High course load
        course_count_high = any(word in text for word in ['5 courses', '6 courses', 'overload'])
    
        return any(word in text for word in exam_heavy) and course_count_high

    def _check_language_theory(self, case: Dict) -> bool:
        """Check language barrier vs theory content"""
        text = self._get_search_text(case)
    
        # Language barrier
        language_issue = ['non-native', 'language barrier', 'english difficulty', 
                         'international student']
        has_language_barrier = any(word in text for word in language_issue)
    
        # Theory-heavy courses
        theory_heavy = ['theory', 'essay', 'written exam', 'report', 'paper']
        has_theory = any(word in text for word in theory_heavy)
    
        return has_language_barrier and has_theory

    def _check_work_study(self, case: Dict) -> bool:
        """Check part-time work vs study requirements"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        text = self._get_search_text(case)
    
        # Work hours
        work_indicators = ['part-time', 'full-time job', 'working', '20 hours', 
                          '30 hours', '40 hours', 'employed']
        has_work = any(word in text for word in work_indicators)
    
        # High study requirements
        study_heavy = ['4 courses', '5 courses', 'heavy workload', 
                      'research', 'thesis']
        has_heavy_study = any(word in text for word in study_heavy)
    
        return has_work and has_heavy_study

    def _check_specialization_breadth(self, case: Dict) -> bool:
        """Check specialization focus vs breadth requirements"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        soft = case.get('constraints', {}).get('soft_constraints', [])
        text = self._get_search_text(case)
    
        # Specialization desire
        specialization = ['ml-heavy', 'focus on', 'specialize', 'deep learning only', 
                         'pure ml']
        wants_specialization = any(word in text for word in specialization)
    
        # Breadth requirements
        breadth = ['core courses', 'breadth requirement', 'must take', 
                  'required courses', 'elective requirement']
        has_breadth_req = any(word in text for word in breadth)
    
        return wants_specialization and has_breadth_req

    def _check_research_coursework(self, case: Dict) -> bool:
        """Check research commitments vs coursework"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        text = self._get_search_text(case)
    
        # Research commitment
        research_words = ['research', 'thesis', 'phd', 'lab work', 
                        'publication', 'paper deadline']
        has_research = any(word in text for word in research_words)
    
        # High coursework
        high_coursework = ['4 courses', '5 courses', 'full course load']
        has_high_coursework = any(word in text for word in high_coursework)
    
        return has_research and has_high_coursework
    
    # ============= TRAVEL RULES =============
    
    def _init_travel_rules(self) -> List[Dict]:
        """Travel domain conflict rules - ENHANCED"""
        return [
            {
            'name': 'budget_vs_luxury',
            'severity': 0.9,
            'check': lambda case: self._check_budget_luxury(case),
            'description': 'Budget conflicts with luxury preferences'
        },
        {
            'name': 'budget_vs_activities',
            'severity': 0.6,
            'check': lambda case: self._check_budget_activities(case),
            'description': 'Budget limits activity preferences'
        },
        {
            'name': 'short_duration_vs_distance',
            'severity': 0.85,
            'check': lambda case: self._check_duration_distance(case),
            'description': 'Short trip duration conflicts with long-distance destination'
        },
        {
            'name': 'group_size_vs_budget',
            'severity': 0.7,
            'check': lambda case: self._check_group_budget(case),
            'description': 'Large group size complicates budget accommodation'
        },
        {
            'name': 'luxury_vs_adventure',
            'severity': 0.65,
            'check': lambda case: self._check_luxury_adventure(case),
            'description': 'Luxury accommodation conflicts with adventure activities'
        },
        {
            'name': 'weather_vs_timeline',
            'severity': 0.8,
            'check': lambda case: self._check_weather_timeline(case),
            'description': 'Fixed timeline conflicts with seasonal weather requirements'
        },
        {
            'name': 'family_vs_adventure',
            'severity': 0.75,
            'check': lambda case: self._check_family_adventure(case),
            'description': 'Family with kids conflicts with adventure activities'
        },
        {
            'name': 'solo_vs_safety',
            'severity': 0.7,
            'check': lambda case: self._check_solo_safety(case),
            'description': 'Solo travel conflicts with safety concerns in certain destinations'
        },
        {
            'name': 'flight_budget_vs_destination',
            'severity': 0.9,
            'check': lambda case: self._check_flight_budget(case),
            'description': 'Flight costs exceed budget for distant destinations'
        },
        {
            'name': 'accessibility_vs_remote',
            'severity': 0.65,
            'check': lambda case: self._check_accessibility_remote(case),
            'description': 'Accessibility needs conflict with remote destination'
        }
        ]
    
    def _check_budget_luxury(self, case: Dict) -> bool:
        """EXISTING - already in your code"""
        # Your existing implementation
        pass

    def _check_budget_activities(self, case: Dict) -> bool:
        """EXISTING - already in your code"""
        # Your existing implementation
        pass

    def _check_duration_distance(self, case: Dict) -> bool:
        """Check short trip vs long-distance destination"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        text = self._get_search_text(case)
    
        # Short duration
        duration = self._get_constraint_value(hard, 'duration')
        is_short = duration and duration <= 3  # 3 days or less
    
        # Long-distance destinations (from query)
        long_distance = ['leh', 'ladakh', 'andaman', 'kashmir', 
                        'northeast', 'international']
        has_long_distance = any(dest in text for dest in long_distance)
    
        return is_short and has_long_distance

    def _check_group_budget(self, case: Dict) -> bool:
        """Check large group vs budget constraints"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
    
        # Group size
        group_size = self._get_constraint_value(hard, 'group_size')
        is_large_group = group_size and group_size >= 6
    
        # Budget per person
        budget = self._get_constraint_value(hard, 'budget')
        is_tight_budget = budget and budget < 15000
    
        return is_large_group and is_tight_budget

    def _check_luxury_adventure(self, case: Dict) -> bool:
        """Check luxury accommodation vs adventure activities"""
        soft = case.get('constraints', {}).get('soft_constraints', [])
        text = self._get_search_text(case)
    
        # Luxury preference
        wants_luxury = False
        for pref in soft:
            pref_val = str(pref.get('value', '')).lower()
            if any(word in pref_val for word in ['luxury', '5-star', 'resort']):
                if pref.get('strength', 0) > 0.7:
                    wants_luxury = True
    
        # Adventure activities
        adventure = ['trek', 'camping', 'rafting', 'paragliding', 
                    'scuba', 'hiking', 'backpacking']
        wants_adventure = any(activity in text for activity in adventure)
    
        return wants_luxury and wants_adventure

    def _check_weather_timeline(self, case: Dict) -> bool:
        """Check fixed dates vs seasonal weather needs"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        text = self._get_search_text(case)
    
        # Fixed dates mentioned
        has_fixed_dates = any(word in text for word in ['march', 'april', 'june', 
                                                     'fixed dates', 'specific dates'])
    
        # Weather-dependent destinations
        weather_sensitive = ['monsoon', 'snow', 'winter', 'summer', 
                            'leh', 'ladakh', 'manali', 'snowfall']
        is_weather_sensitive = any(word in text for word in weather_sensitive)
    
        return has_fixed_dates and is_weather_sensitive

    def _check_family_adventure(self, case: Dict) -> bool:
        """Check family with kids vs adventure activities"""
        text = self._get_search_text(case)
    
        # Family with kids
        has_kids = any(word in text for word in ['kids', 'children', 'family', 
                                                 'age 5', 'age 8', 'toddler'])
    
        # Adventure activities
        adventure = ['trek', 'trekking', 'camping', 'rafting', 'diving', 
                    'paragliding', 'adventure']
        wants_adventure = any(activity in text for activity in adventure)
    
        return has_kids and wants_adventure

    def _check_solo_safety(self, case: Dict) -> bool:
        """Check solo travel vs safety concerns"""
        text = self._get_search_text(case)
    
        # Solo traveler
        is_solo = 'solo' in text
    
        # Destinations with safety concerns (generic check)
        safety_concern_destinations = ['remote', 'isolated', 'trek', 'camping']
        has_safety_concern = any(word in text for word in safety_concern_destinations)
    
        return is_solo and has_safety_concern

    def _check_flight_budget(self, case: Dict) -> bool:
        """Check if flight costs dominate budget for distant destinations"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        text = self._get_search_text(case)
    
        # Budget
        budget = self._get_constraint_value(hard, 'budget')
    
        # Flight-necessary destinations
        flight_destinations = ['leh', 'andaman', 'kashmir', 'northeast', 
                              'international', 'goa from delhi', 'kerala from mumbai']
        needs_flight = any(dest in text for dest in flight_destinations)
    
        # Conflict if budget < 20000 and needs expensive flights
        return needs_flight and budget and budget < 20000

    def _check_accessibility_remote(self, case: Dict) -> bool:
        """Check accessibility needs vs remote destination"""
        hard = case.get('constraints', {}).get('hard_constraints', [])
        soft = case.get('constraints', {}).get('soft_constraints', [])
        text = self._get_search_text(case)
    
        # Accessibility needs (seniors, disabilities, comfort)
        accessibility_needs = ['senior', 'elderly', '60+', 'wheelchair', 
                            'limited mobility', 'easy access']
        has_accessibility_need = any(word in text for word in accessibility_needs)
    
        # Remote destinations
        remote = ['trek', 'camping', 'remote', 'offbeat', 'isolated', 
                 'difficult terrain']
        is_remote = any(word in text for word in remote)
    
        return has_accessibility_need and is_remote

    # ============= MAIN DETECTION =============
    
    def detect_conflicts(self, case: Dict) -> List[Dict]:
        """
        Detect conflicts in a case
        
        Args:
            case: Case with constraints
            
        Returns:
            List of conflicts with severity
        """
        domain = case.get('domain', '')
        
        # Get domain rules
        if domain == 'health':
            rules = self.health_rules
        elif domain == 'education':
            rules = self.education_rules
        elif domain == 'travel':
            rules = self.travel_rules
        else:
            return []
        
        # Check each rule
        conflicts = []
        for rule in rules:
            try:
                if rule['check'](case):
                    conflicts.append({
                        'type': rule['name'],
                        'severity': rule['severity'],
                        'description': rule['description'],
                        'resolution_strategy': f"Address {rule['name']} conflict"
                    })
            except Exception as e:
                continue
        
        return conflicts
    
    def calculate_resolution_quality(self, case: Dict) -> float:
        """Calculate resolution quality (0-1, higher=better)"""
        conflicts = case.get('conflicts', [])
        
        if not conflicts:
            return 1.0
        
        avg_severity = sum(c['severity'] for c in conflicts) / len(conflicts)
        quality = 1.0 - avg_severity
        
        return max(0.0, min(1.0, quality))


# TEST
if __name__ == "__main__":
    from constraint_extractor import ConstraintExtractor
    
    detector = ConflictDetector()
    extractor = ConstraintExtractor()
    
    # Test cases for all domains
    test_cases = [
        ("19F; Anemia + PCOS; Budget ₹80/day; Vegan; Hostel mess; Need 50g protein", "health"),
        ("M.Tech; Need 5 courses; Deep Learning + NLP; High GPA; Max 20hrs/week", "education"),
        ("Solo; ₹8000 budget; 5 days; Beach; Want scuba, parasailing", "travel")
    ]
    
    print("="*70)
    print("TESTING ENHANCED CONFLICT DETECTOR")
    print("="*70)
    
    for query, domain in test_cases:
        print(f"\n{'='*70}")
        print(f"Domain: {domain.upper()}")
        print(f"Query: {query}")
        print(f"{'='*70}")
        
        # Extract constraints
        constraints = extractor.extract(query, domain)
        
        # Build case
        case = {
            'query': query,
            'domain': domain,
            'constraints': constraints
        }
        
        # Detect conflicts
        conflicts = detector.detect_conflicts(case)
        
        print(f"\nConflicts detected: {len(conflicts)}")
        for conflict in conflicts:
            print(f"  • {conflict['type']} (severity: {conflict['severity']:.2f})")
            print(f"    {conflict['description']}")
    
    print("\n" + "="*70)
    print("✓ All domains tested!")
    print("="*70)