"""
Enhanced Experiment Tracker

Stores detailed information for each test case:
1. Generated solutions for all systems
2. Retrieved examples (with IDs and sources)
3. Cross-domain transfer details
4. Conflict mappings used

Usage: Replace or extend existing experiment logging
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from pathlib import Path


class EnhancedExperimentTracker:
    """Track detailed experiment information including solutions and retrieval details"""
    
    def __init__(self, results_dir: str = '../results'):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.solutions_dir = self.results_dir / 'solutions'
        self.solutions_dir.mkdir(exist_ok=True)
        
        self.retrievals_dir = self.results_dir / 'retrievals'
        self.retrievals_dir.mkdir(exist_ok=True)
        
        self.cross_domain_dir = self.results_dir / 'cross_domain_details'
        self.cross_domain_dir.mkdir(exist_ok=True)
        
        print(f"✓ Enhanced tracker initialized")
        print(f"  Solutions: {self.solutions_dir}")
        print(f"  Retrievals: {self.retrievals_dir}")
        print(f"  Cross-domain: {self.cross_domain_dir}")
    
    def save_test_case_results(self, test_case: Dict, all_solutions: Dict[str, Dict], 
                               metrics_results: Dict[str, Dict]):
        """
        Save complete results for a single test case
        
        Args:
            test_case: Test case with query and metadata
            all_solutions: Solutions from all systems
            metrics_results: Evaluation metrics for all systems
        """
        
        test_id = test_case['id']
        domain = test_case['domain']
        
        # 1. Save all solutions
        self._save_solutions(test_id, domain, test_case, all_solutions)
        
        # 2. Save retrieval details
        self._save_retrievals(test_id, domain, all_solutions)
        
        # 3. Save cross-domain details (if exists)
        if 'cross_domain' in all_solutions:
            self._save_cross_domain_details(test_id, domain, all_solutions['cross_domain'])
        
        # 4. Save combined summary
        self._save_test_summary(test_id, domain, test_case, all_solutions, metrics_results)
    
    def _save_solutions(self, test_id: str, domain: str, test_case: Dict, 
                       all_solutions: Dict[str, Dict]):
        """Save generated solutions for all systems"""
        
        solutions_file = self.solutions_dir / f"{test_id}_solutions.json"
        
        solutions_data = {
            'test_id': test_id,
            'domain': domain,
            'query': test_case['query'],
            'timestamp': datetime.now().isoformat(),
            'solutions': {}
        }
        
        for system_name, solution_data in all_solutions.items():
            solutions_data['solutions'][system_name] = {
                'solution_text': solution_data.get('solution', ''),
                'solution_length': len(solution_data.get('solution', '')),
                'method': solution_data.get('method', ''),
                'num_examples': solution_data.get('num_examples', 0)
            }
            
            # Add cross-domain specific info
            if system_name == 'cross_domain':
                solutions_data['solutions'][system_name]['cross_domain_count'] = \
                    solution_data.get('cross_domain_count', 0)
        
        with open(solutions_file, 'w', encoding='utf-8') as f:
            json.dump(solutions_data, f, indent=2, ensure_ascii=False)
        
        # Also save individual solution text files for easy reading
        for system_name, solution_data in all_solutions.items():
            solution_txt = self.solutions_dir / f"{test_id}_{system_name}.txt"
            with open(solution_txt, 'w', encoding='utf-8') as f:
                f.write(f"TEST: {test_id}\n")
                f.write(f"SYSTEM: {system_name}\n")
                f.write(f"DOMAIN: {domain}\n")
                f.write(f"QUERY: {test_case['query']}\n")
                f.write("="*70 + "\n\n")
                f.write(solution_data.get('solution', ''))
    
    def _save_retrievals(self, test_id: str, domain: str, all_solutions: Dict[str, Dict]):
        """Save retrieval details for all systems"""
        
        retrievals_file = self.retrievals_dir / f"{test_id}_retrievals.json"
        
        retrievals_data = {
            'test_id': test_id,
            'domain': domain,
            'timestamp': datetime.now().isoformat(),
            'systems': {}
        }
        
        for system_name, solution_data in all_solutions.items():
            system_retrievals = {
                'num_examples': solution_data.get('num_examples', 0),
                'retrieved_cases': solution_data.get('retrieved_cases', []),
                'method': solution_data.get('method', '')
            }
            
            # Add domain info for cross-domain
            if system_name == 'cross_domain':
                system_retrievals['cross_domain_count'] = \
                    solution_data.get('cross_domain_count', 0)
                system_retrievals['same_domain_count'] = \
                    solution_data.get('num_examples', 0) - solution_data.get('cross_domain_count', 0)
            
            retrievals_data['systems'][system_name] = system_retrievals
        
        with open(retrievals_file, 'w', encoding='utf-8') as f:
            json.dump(retrievals_data, f, indent=2)
    
    def _save_cross_domain_details(self, test_id: str, domain: str, 
                                   cross_domain_solution: Dict):
        """Save detailed cross-domain transfer information"""
        
        details_file = self.cross_domain_dir / f"{test_id}_cross_domain.json"
        
        # This will be populated by compare_systems if we pass retrieval details
        cross_domain_data = {
            'test_id': test_id,
            'target_domain': domain,
            'timestamp': datetime.now().isoformat(),
            'retrieved_cases': cross_domain_solution.get('retrieved_cases', []),
            'cross_domain_count': cross_domain_solution.get('cross_domain_count', 0),
            'total_examples': cross_domain_solution.get('num_examples', 0),
            'same_domain_count': cross_domain_solution.get('num_examples', 0) - 
                                cross_domain_solution.get('cross_domain_count', 0)
        }
        
        with open(details_file, 'w', encoding='utf-8') as f:
            json.dump(cross_domain_data, f, indent=2)
        
        # Also create readable text version
        details_txt = self.cross_domain_dir / f"{test_id}_cross_domain.txt"
        with open(details_txt, 'w', encoding='utf-8') as f:
            f.write(f"CROSS-DOMAIN TRANSFER DETAILS\n")
            f.write("="*70 + "\n\n")
            f.write(f"Test ID: {test_id}\n")
            f.write(f"Target Domain: {domain}\n")
            f.write(f"Total Examples Retrieved: {cross_domain_data['total_examples']}\n")
            f.write(f"Same-Domain Examples: {cross_domain_data['same_domain_count']}\n")
            f.write(f"Cross-Domain Examples: {cross_domain_data['cross_domain_count']}\n\n")
            
            f.write("Retrieved Cases:\n")
            for i, case_id in enumerate(cross_domain_data['retrieved_cases'], 1):
                f.write(f"  {i}. {case_id}\n")
    
    def _save_test_summary(self, test_id: str, domain: str, test_case: Dict,
                          all_solutions: Dict[str, Dict], 
                          metrics_results: Dict[str, Dict]):
        """Save combined summary for test case"""
        
        summary_file = self.results_dir / f"{test_id}_summary.json"
        
        summary = {
            'test_id': test_id,
            'domain': domain,
            'query': test_case['query'],
            'expected_conflicts': test_case.get('expected_conflicts', []),
            'timestamp': datetime.now().isoformat(),
            'systems': {}
        }
        
        for system_name in all_solutions.keys():
            summary['systems'][system_name] = {
                'solution_length': len(all_solutions[system_name].get('solution', '')),
                'num_examples': all_solutions[system_name].get('num_examples', 0),
                'method': all_solutions[system_name].get('method', ''),
                'metrics': metrics_results.get(system_name, {})
            }
            
            if system_name == 'cross_domain':
                summary['systems'][system_name]['cross_domain_count'] = \
                    all_solutions[system_name].get('cross_domain_count', 0)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
    
    def generate_cross_domain_report(self):
        """Generate summary report of all cross-domain transfers"""
        
        report_file = self.results_dir / 'cross_domain_summary_report.txt'
        
        # Collect all cross-domain files
        cross_domain_files = list(self.cross_domain_dir.glob('*_cross_domain.json'))
        
        if not cross_domain_files:
            print("⚠️  No cross-domain data found")
            return
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("CROSS-DOMAIN TRANSFER SUMMARY REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Test Cases: {len(cross_domain_files)}\n\n")
            
            total_retrievals = 0
            total_cross_domain = 0
            by_domain = {}
            
            for file_path in sorted(cross_domain_files):
                with open(file_path, 'r') as jf:
                    data = json.load(jf)
                
                test_id = data['test_id']
                domain = data['target_domain']
                cross_count = data['cross_domain_count']
                total_count = data['total_examples']
                
                if domain not in by_domain:
                    by_domain[domain] = {'tests': 0, 'cross_domain': 0, 'total': 0}
                
                by_domain[domain]['tests'] += 1
                by_domain[domain]['cross_domain'] += cross_count
                by_domain[domain]['total'] += total_count
                
                total_retrievals += total_count
                total_cross_domain += cross_count
                
                f.write(f"{test_id}:\n")
                f.write(f"  Domain: {domain}\n")
                f.write(f"  Cross-domain examples: {cross_count}/{total_count}\n")
                f.write(f"  Cases: {', '.join(data['retrieved_cases'])}\n\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("SUMMARY BY DOMAIN\n")
            f.write("="*80 + "\n\n")
            
            for domain, stats in by_domain.items():
                f.write(f"{domain.upper()}:\n")
                f.write(f"  Test cases: {stats['tests']}\n")
                f.write(f"  Total retrievals: {stats['total']}\n")
                f.write(f"  Cross-domain: {stats['cross_domain']}\n")
                f.write(f"  Cross-domain rate: {stats['cross_domain']/stats['total']*100:.1f}%\n\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("OVERALL STATISTICS\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total retrievals: {total_retrievals}\n")
            f.write(f"Cross-domain retrievals: {total_cross_domain}\n")
            f.write(f"Cross-domain rate: {total_cross_domain/total_retrievals*100:.1f}%\n")
        
        print(f"\n✓ Generated cross-domain report: {report_file}")


# TEST
if __name__ == "__main__":
    print("="*70)
    print("TESTING ENHANCED EXPERIMENT TRACKER")
    print("="*70)
    
    tracker = EnhancedExperimentTracker()
    
    # Mock test case
    test_case = {
        'id': 'TEST_H01',
        'domain': 'health',
        'query': '19F; Anemia; Budget ₹80/day; Vegan',
        'expected_conflicts': ['budget_vs_protein', 'vegan_vs_protein']
    }
    
    # Mock solutions
    all_solutions = {
        'zero_shot': {
            'solution': 'Generic health advice here...',
            'method': 'zero-shot',
            'num_examples': 0
        },
        'semantic': {
            'solution': 'Semantic RAG solution here...',
            'method': 'semantic',
            'num_examples': 3,
            'retrieved_cases': ['HC_001', 'HC_004', 'HC_010']
        },
        'conflict_aware': {
            'solution': 'Conflict-aware solution here...',
            'method': 'conflict',
            'num_examples': 3,
            'retrieved_cases': ['HC_001', 'HC_004', 'HC_014']
        },
        'cross_domain': {
            'solution': 'Cross-domain solution here...',
            'method': 'cross-domain',
            'num_examples': 3,
            'cross_domain_count': 1,
            'retrieved_cases': ['HC_001', 'ED_010', 'HC_014']
        }
    }
    
    # Mock metrics
    metrics_results = {
        'zero_shot': {'csr': 0.6, 'crq': 0.1, 'sf': 0.7, 'overall': 0.45},
        'semantic': {'csr': 0.6, 'crq': 0.22, 'sf': 0.7, 'overall': 0.49},
        'conflict_aware': {'csr': 0.6, 'crq': 0.7, 'sf': 0.8, 'overall': 0.69},
        'cross_domain': {'csr': 0.8, 'crq': 0.6, 'sf': 0.8, 'overall': 0.73}
    }
    
    # Test save
    print("\nSaving test case results...")
    tracker.save_test_case_results(test_case, all_solutions, metrics_results)
    
    print("\nGenerating cross-domain report...")
    tracker.generate_cross_domain_report()
    
    print("\n" + "="*70)
    print("✓ Test complete! Check ../results/ for generated files")
    print("="*70)