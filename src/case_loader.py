import json
import pandas as pd
import os
from pathlib import Path
from typing import List, Dict

class CaseLoader:
    """Load and preprocess your 63-case dataset"""
    
    def __init__(self, dataset_path='../data/'):
        self.dataset_path = Path(dataset_path)
        self.cases = []
    
    def load_all_cases(self) -> List[Dict]:
        """
        Load all cases from the three CSV files
        
        Returns:
            List of case dictionaries
        """
        print(f"Loading cases from {self.dataset_path}...")
        
        all_cases = []
        
        # Load health cases
        health_file = self.dataset_path / "AFSL_MultiDomain_Dataset - Health_Cases.csv"
        if health_file.exists():
            health_cases = self._load_domain_csv(health_file, 'health')
            all_cases.extend(health_cases)
            print(f"  ✓ Loaded {len(health_cases)} health cases")
        
        # Load education cases
        edu_file = self.dataset_path / "AFSL_MultiDomain_Dataset - Education_Cases.csv"
        if edu_file.exists():
            edu_cases = self._load_domain_csv(edu_file, 'education')
            all_cases.extend(edu_cases)
            print(f"  ✓ Loaded {len(edu_cases)} education cases")
        
        # Load travel cases
        travel_file = self.dataset_path / "AFSL_MultiDomain_Dataset - Travel_Cases.csv"
        if travel_file.exists():
            travel_cases = self._load_domain_csv(travel_file, 'travel')
            all_cases.extend(travel_cases)
            print(f"  ✓ Loaded {len(travel_cases)} travel cases")
        
        if not all_cases:
            print("⚠ No case files found. Using sample cases.")
            return self._create_sample_cases()
        
        print(f"\n✓ Total: {len(all_cases)} cases loaded")
        return all_cases
    
    def _load_domain_csv(self, filepath: Path, domain: str) -> List[Dict]:
        """Load cases from a domain-specific CSV file"""
        df = pd.read_csv(filepath)
    
        cases = []
        for idx, row in df.iterrows():
            # BUILD QUERY FROM METADATA for constraint extraction
            if domain == 'health':
                query_parts = []
                if pd.notna(row.get('Age')): query_parts.append(f"{int(row['Age'])}{'M' if row.get('Gender')=='Male' else 'F'}")
                if pd.notna(row.get('Problem')): query_parts.append(row['Problem'])
                if pd.notna(row.get('Hard_Constraints')): query_parts.append(row['Hard_Constraints'])
                if pd.notna(row.get('Soft_Constraints')): query_parts.append(row['Soft_Constraints'])
                if pd.notna(row.get('Current_Diet')): query_parts.append(f"Current diet: {row['Current_Diet']}")
                query = "; ".join(query_parts)
        
            elif domain == 'education':
                query_parts = []
                if pd.notna(row.get('Level')): query_parts.append(row['Level'])
                if pd.notna(row.get('Problem')): query_parts.append(row['Problem'])
                if pd.notna(row.get('Hard_Constraints')): query_parts.append(row['Hard_Constraints'])
                if pd.notna(row.get('Soft_Constraints')): query_parts.append(row['Soft_Constraints'])
                if pd.notna(row.get('Current_Situation')): query_parts.append(row['Current_Situation'])
                query = "; ".join(query_parts)
        
            elif domain == 'travel':
                query_parts = []
                if pd.notna(row.get('Traveler_Type')): query_parts.append(row['Traveler_Type'])
                if pd.notna(row.get('Destination')): query_parts.append(f"to {row['Destination']}")
                if pd.notna(row.get('Duration_Days')): query_parts.append(f"{row['Duration_Days']} days")
                if pd.notna(row.get('Hard_Constraints')): query_parts.append(row['Hard_Constraints'])
                if pd.notna(row.get('Soft_Constraints')): query_parts.append(row['Soft_Constraints'])
                if pd.notna(row.get('Travel_Preferences')): query_parts.append(row['Travel_Preferences'])
                query = "; ".join(query_parts)
            else:
                query = ""
        
            case = {
                'id': row.get('Case_ID', f"{domain.upper()[:2]}_{idx+1:03d}"),
                'domain': domain,
                'query': query,  # ← NOW POPULATED!
                'solution': row.get('Expert_Solution', row.get('Solution', '')),
                'metadata': {}
            }
        
            # Add any additional columns as metadata
            for col in df.columns:
                if col not in ['Case_ID', 'Expert_Solution', 'Solution']:
                    case['metadata'][col] = row[col]
        
            # Skip completely empty cases (the "nan" cases)
            if pd.isna(case['id']) or case['id'] == 'nan':
                continue
            
            cases.append(case)
    
        return cases
    
    def _create_sample_cases(self) -> List[Dict]:
        """Create sample cases for testing if no dataset found"""
        print("Creating 10 sample cases for testing...")
        
        samples = [
            {
                'id': 'HC_001',
                'domain': 'health',
                'query': '22F, hair fall, vegetarian, hostel mess, ₹150/day budget, prefer quick meals',
                'solution': 'Focus on biotin-rich vegetarian foods like peanuts, almonds, dal. Supplement with vitamin C from citrus fruits. Breakfast: Peanut butter on whole wheat. Lunch/Dinner: Dal with rice and vegetables.',
                'metadata': {'age': 22, 'gender': 'F', 'complexity': 'medium'}
            },
            {
                'id': 'HC_002',
                'domain': 'health',
                'query': '25M, want to gain muscle, non-veg, gym available, ₹300/day budget, willing to cook',
                'solution': 'High protein diet with chicken, eggs, fish. Breakfast: 4 eggs + oats. Lunch: Chicken breast 200g + rice. Dinner: Fish + vegetables. Snacks: Protein shake, peanuts.',
                'metadata': {'age': 25, 'gender': 'M', 'complexity': 'medium'}
            },
            {
                'id': 'HC_003',
                'domain': 'health',
                'query': '19F, anemia (iron deficiency), vegetarian, home cooking, ₹200/day, no time for elaborate meals',
                'solution': 'Iron-rich vegetarian foods: spinach, beetroot, jaggery, dates. Pair with vitamin C for absorption. Simple meals: Spinach dal, beetroot salad, iron-fortified cereals.',
                'metadata': {'age': 19, 'gender': 'F', 'complexity': 'high'}
            },
            {
                'id': 'HC_004',
                'domain': 'health',
                'query': '30M, pre-diabetic, need low carb diet, ₹250/day, prefer tasty food',
                'solution': 'Low GI foods: brown rice, whole grains, vegetables, lean protein. Avoid: white rice, sugar, processed foods. Meals: Grilled chicken/fish, salads, cauliflower rice.',
                'metadata': {'age': 30, 'gender': 'M', 'complexity': 'medium'}
            },
            {
                'id': 'HC_005',
                'domain': 'health',
                'query': '21F, weight loss goal, vegan preferred, ₹100/day budget, hostel mess only',
                'solution': 'Low calorie vegan options from mess: vegetables, dal, salads. Avoid fried items. Portion control important. Supplement with fruits. Skip rice, double vegetables.',
                'metadata': {'age': 21, 'gender': 'F', 'complexity': 'high'}
            },
            {
                'id': 'EC_001',
                'domain': 'education',
                'query': '3rd semester M.Tech, completed ML basics, need 4 courses, interested in CV and NLP, want high GPA professors',
                'solution': 'Course selection: 1) Deep Learning (prereq satisfied, CV-related), 2) NLP Fundamentals (high GPA prof), 3) Computer Vision (interest aligned), 4) Statistics (easy, GPA boost).',
                'metadata': {'semester': 3, 'program': 'M.Tech', 'complexity': 'medium'}
            },
            {
                'id': 'EC_002',
                'domain': 'education',
                'query': 'Final year B.Tech, prerequisites done, need easy courses for GPA, max 15 hours/week workload',
                'solution': 'Easy courses with light workload: Database Systems (project-based, 8hrs), Web Development (easy prof, 6hrs), Total: 14hrs/week, both have high GPA averages.',
                'metadata': {'semester': 8, 'program': 'B.Tech', 'complexity': 'low'}
            },
            {
                'id': 'TR_001',
                'domain': 'travel',
                'query': '2 friends, ₹15000 total budget, 5 days, beach destination, want water sports and nightlife',
                'solution': 'Goa trip: Stay in budget hostel (₹800/night), water sports at Baga Beach (₹2000/person), nightlife at Tito\'s. Total: Accommodation ₹4000, activities ₹6000, food ₹5000.',
                'metadata': {'travelers': 2, 'days': 5, 'complexity': 'medium'}
            },
            {
                'id': 'TR_002',
                'domain': 'travel',
                'query': 'Solo trip, ₹8000 budget, 3 days, spiritual destination, prefer mountains, March travel',
                'solution': 'McLeodganj: Buddhist monasteries, mountain views. Stay in dharamshala (₹500/night), visit Dalai Lama temple, trek to Triund. Budget: Stay ₹1500, food ₹2000, travel ₹3000, activities ₹1500.',
                'metadata': {'travelers': 1, 'days': 3, 'complexity': 'low'}
            },
            {
                'id': 'TR_003',
                'domain': 'travel',
                'query': 'Family of 4, ₹30000 budget, 7 days, kid-friendly destination, educational activities preferred',
                'solution': 'Agra + Jaipur circuit: Taj Mahal, Amber Fort. Educational value high. Stay in mid-range hotels (₹2500/night). Budget: Accommodation ₹17500, food ₹7000, travel ₹3500, entry fees ₹2000.',
                'metadata': {'travelers': 4, 'days': 7, 'complexity': 'high'}
            }
        ]
        
        print(f"✓ Created {len(samples)} sample cases")
        return samples
    
    def preprocess_cases(self, cases: List[Dict]) -> List[Dict]:
        """
        Add constraint and conflict annotations to cases
        
        This will use your constraint_extractor and conflict_detector
        to automatically annotate cases if they don't have annotations
        """
        from constraint_extractor import ConstraintExtractor
        from conflict_detector import ConflictDetector
        
        extractor = ConstraintExtractor()
        detector = ConflictDetector()
        
        print("\nPreprocessing cases (extracting constraints and conflicts)...")
        print("This will take a few minutes with Groq API calls...")
        
        processed = []
        for i, case in enumerate(cases):
            case_id = case.get('id', f'case_{i}')
            print(f"  [{i+1}/{len(cases)}] Processing {case_id}...", end=' ', flush=True)
            
            # Extract constraints if not present
            if 'constraints' not in case:
                try:
                    case['constraints'] = extractor.extract(
                        case['query'], 
                        case['domain']
                    )
                except Exception as e:
                    print(f"✗ Error: {e}")
                    case['constraints'] = {'hard_constraints': [], 'soft_constraints': [], 'goals': []}
                    processed.append(case)
                    continue
            
            # Detect conflicts if not present
            # Detect conflicts if not present
            if 'conflicts' not in case and case['constraints']:
                try:
                    case['conflicts'] = detector.detect_conflicts(case)  # ← Pass entire case!
                
                except Exception as e:
                    print(f"✗ Conflict detection error: {e}")
                    case['conflicts'] = []
            
            # Add resolution quality score (placeholder)
            if 'resolution_quality' not in case:
                # Simple heuristic: fewer conflicts = better resolution
                num_conflicts = len(case.get('conflicts', []))
                case['resolution_quality'] = max(0.3, 1.0 - (num_conflicts * 0.2))
            
            processed.append(case)
            
            # Show summary
            num_hard = len(case['constraints'].get('hard_constraints', []))
            num_soft = len(case['constraints'].get('soft_constraints', []))
            num_conflicts = len(case.get('conflicts', []))
            print(f"✓ (H:{num_hard}, S:{num_soft}, C:{num_conflicts})")
        
        print(f"\n✓ Preprocessed {len(processed)} cases")
        return processed
    
    def save_processed_cases(self, cases: List[Dict], output_path='../data/processed_cases.json'):
        """Save preprocessed cases for future use"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cases, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved processed cases to {output_path}")
        
        # Also save summary statistics
        self._save_summary(cases, output_path.parent / 'preprocessing_summary.txt')
    
    def _save_summary(self, cases: List[Dict], summary_path: Path):
        """Save preprocessing summary"""
        with open(summary_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write("CASE PREPROCESSING SUMMARY\n")
            f.write("="*70 + "\n\n")
            
            # Overall stats
            f.write(f"Total cases: {len(cases)}\n\n")
            
            # Domain breakdown
            for domain in ['health', 'education', 'travel']:
                domain_cases = [c for c in cases if c['domain'] == domain]
                f.write(f"{domain.capitalize()}: {len(domain_cases)} cases\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("CONSTRAINT STATISTICS\n")
            f.write("="*70 + "\n\n")
            
            # Constraint stats
            total_hard = sum(len(c['constraints'].get('hard_constraints', [])) for c in cases)
            total_soft = sum(len(c['constraints'].get('soft_constraints', [])) for c in cases)
            total_goals = sum(len(c['constraints'].get('goals', [])) for c in cases)
            
            f.write(f"Total hard constraints: {total_hard}\n")
            f.write(f"Total soft constraints: {total_soft}\n")
            f.write(f"Total goals: {total_goals}\n")
            f.write(f"Avg hard per case: {total_hard/len(cases):.1f}\n")
            f.write(f"Avg soft per case: {total_soft/len(cases):.1f}\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("CONFLICT STATISTICS\n")
            f.write("="*70 + "\n\n")
            
            # Conflict stats
            total_conflicts = sum(len(c.get('conflicts', [])) for c in cases)
            cases_with_conflicts = sum(1 for c in cases if len(c.get('conflicts', [])) > 0)
            
            f.write(f"Total conflicts detected: {total_conflicts}\n")
            f.write(f"Cases with conflicts: {cases_with_conflicts}/{len(cases)}\n")
            f.write(f"Avg conflicts per case: {total_conflicts/len(cases):.1f}\n")
            
            # Conflict type breakdown
            conflict_types = {}
            for case in cases:
                for conflict in case.get('conflicts', []):
                    ctype = conflict['type']
                    conflict_types[ctype] = conflict_types.get(ctype, 0) + 1
            
            if conflict_types:
                f.write("\nConflict types:\n")
                for ctype, count in sorted(conflict_types.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"  {ctype}: {count}\n")
        
        print(f"✓ Saved summary to {summary_path}")


# TEST
if __name__ == "__main__":
    loader = CaseLoader()
    
    # Load cases
    cases = loader.load_all_cases()
    
    if not cases:
        print("❌ No cases loaded!")
        exit()
    
    print(f"\nLoaded {len(cases)} cases:")
    for domain in ['health', 'education', 'travel']:
        count = sum(1 for c in cases if c['domain'] == domain)
        print(f"  {domain.capitalize()}: {count} cases")
    
    # Show sample case
    print("\n" + "="*70)
    print("SAMPLE CASE")
    print("="*70)
    sample = cases[0]
    print(f"ID: {sample['id']}")
    print(f"Domain: {sample['domain']}")
    print(f"Query: {sample['query'][:100]}...")
    if sample.get('solution'):
        print(f"Solution: {sample['solution'][:100]}...")
    
    # Preprocess option
    print("\n" + "="*70)
    print("PREPROCESSING OPTIONS")
    print("="*70)
    print("\nPreprocessing will:")
    print("  1. Extract constraints from all cases using Groq API")
    print("  2. Detect conflicts in each case")
    print("  3. Save results to data/processed_cases.json")
    print(f"\nThis will make ~{len(cases)} API calls and take ~{len(cases)//10} minutes.")
    
    try:
        choice = input("\nPreprocess cases now? [y/N]: ").strip().lower()
        
        if choice == 'y':
            processed_cases = loader.preprocess_cases(cases)
            loader.save_processed_cases(processed_cases)
            
            # Show sample
            print("\n" + "="*70)
            print("SAMPLE PROCESSED CASE")
            print("="*70)
            sample = processed_cases[0]
            print(f"ID: {sample['id']}")
            print(f"Query: {sample['query']}")
            print(f"\nConstraints:")
            print(f"  Hard: {len(sample['constraints'].get('hard_constraints', []))}")
            for c in sample['constraints'].get('hard_constraints', []):
                print(f"    - {c['type']}: {c['value']}")
            print(f"  Soft: {len(sample['constraints'].get('soft_constraints', []))}")
            for c in sample['constraints'].get('soft_constraints', []):
                print(f"    - {c['type']}: {c['value']} (strength: {c['strength']})")
            print(f"\nConflicts: {len(sample.get('conflicts', []))}")
            for conflict in sample.get('conflicts', []):
                print(f"  - {conflict['type']} (severity: {conflict['severity']:.2f})")
                resolution = conflict.get('resolution_strategy', 'See solution for resolution')
                print(f"    Resolution: {resolution}")
        else:
            print("\nSkipping preprocessing.")
            print("Your cases are loaded and ready.")
            print("Run this script again with 'y' when ready to preprocess.")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting.")