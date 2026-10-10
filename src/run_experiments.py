"""
Run Complete Experiments:
- Load all test queries
- Run all 5 systems on each query (including cross-domain)
- Evaluate with metrics
- Save results with enhanced tracking
- Print summary
"""

import json
from compare_systems import SystemComparison
from metrics import Metrics
from constraint_extractor import ConstraintExtractor
from enhanced_experiment_tracker import EnhancedExperimentTracker  # NEW: Added
from pathlib import Path


class ExperimentRunner:
    """Run and evaluate all experiments"""
    
    def __init__(self, test_queries_path='../data/test_queries.json'):
        self.comparator = SystemComparison()
        self.metrics = Metrics()
        self.extractor = ConstraintExtractor()
        self.tracker = EnhancedExperimentTracker()  # NEW: Added tracker
        
        # Load test queries
        with open(test_queries_path, 'r', encoding='utf-8') as f:
            self.test_data = json.load(f)
        
        print(f"✓ Loaded test queries:")
        for domain in ['health', 'education', 'travel']:
            count = len(self.test_data.get(domain, []))
            print(f"  - {domain}: {count} queries")
    
    def run_all_experiments(self, domains=None, max_per_domain=None):
        """
        Run experiments on all or selected test cases
        
        Args:
            domains: List of domains to test (default: all)
            max_per_domain: Limit queries per domain (default: all)
            
        Returns:
            List of experiment results
        """
        if domains is None:
            domains = ['health', 'education', 'travel']
        
        all_results = []
        
        print("\n" + "="*80)
        print("STARTING EXPERIMENTS")
        print("="*80)
        
        for domain in domains:
            test_cases = self.test_data.get(domain, [])
            
            if max_per_domain:
                test_cases = test_cases[:max_per_domain]
            
            print(f"\n{'='*80}")
            print(f"DOMAIN: {domain.upper()} ({len(test_cases)} queries)")
            print(f"{'='*80}")
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"\n[{i}/{len(test_cases)}] {test_case['id']}")
                print(f"Query: {test_case['query'][:70]}...")
                
                # Add constraints to test case (needed for evaluation)
                try:
                    test_case['constraints'] = self.extractor.extract(
                        test_case['query'],
                        test_case['domain']
                    )
                except Exception as e:
                    print(f"  ⚠️  Constraint extraction failed: {e}")
                    test_case['constraints'] = {
                        'hard_constraints': [],
                        'soft_constraints': [],
                        'goals': []
                    }
                
                # Run all systems
                try:
                    solutions = self.comparator.run_all_systems(test_case)
                    
                    # Evaluate each system
                    evaluation = {}
                    for system_name, solution in solutions.items():
                        scores = {
                            'csr': self.metrics.constraint_satisfaction_rate(solution, test_case),
                            'crq': self.metrics.conflict_resolution_quality(solution, test_case),
                            'sf': self.metrics.solution_feasibility(solution),
                        }
                        scores['overall'] = self.metrics.overall_score(solution, test_case)
                        evaluation[system_name] = scores
                        
                        print(f"  {system_name:15s}: Overall={scores['overall']:.3f} "
                              f"(CSR={scores['csr']:.2f}, CRQ={scores['crq']:.2f}, SF={scores['sf']:.2f})")
                    
                    # NEW: Save detailed tracking for this test case
                    try:
                        self.tracker.save_test_case_results(test_case, solutions, evaluation)
                        
                        # Show cross-domain info if available
                        if 'cross_domain' in solutions:
                            cross_count = solutions['cross_domain'].get('cross_domain_count', 0)
                            if cross_count > 0:
                                print(f"  ⭐ Cross-domain: {cross_count} examples from other domains")
                        
                        print(f"  ✓ Saved detailed tracking")
                    except Exception as e:
                        print(f"  ⚠️  Tracking save failed: {e}")
                    
                    # Store result
                    all_results.append({
                        'test_case': test_case,
                        'solutions': solutions,
                        'evaluation': evaluation
                    })
                
                except Exception as e:
                    print(f"  ❌ Error running systems: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        
        print(f"\n{'='*80}")
        print(f"✓ Completed {len(all_results)} experiments")
        print(f"{'='*80}\n")
        
        # NEW: Generate cross-domain summary report
        print("\n" + "="*80)
        print("GENERATING CROSS-DOMAIN TRANSFER REPORT")
        print("="*80)
        try:
            self.tracker.generate_cross_domain_report()
        except Exception as e:
            print(f"⚠️  Cross-domain report generation failed: {e}")
        
        return all_results
    
    def save_results(self, results, output_path='../results/experiment_results.json'):
        """Save results to JSON file"""
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved results to {output_path}")
    
    def print_summary(self, results):
        """Print aggregate summary of all experiments"""
        
        if not results:
            print("No results to summarize!")
            return
        
        # NEW: Changed to 5 systems (added cross_domain)
        systems = ['zero_shot', 'semantic', 'conflict_aware', 'hybrid', 'cross_domain']
        metrics = ['csr', 'crq', 'sf', 'overall']
        metric_names = {
            'csr': 'Constraint Satisfaction',
            'crq': 'Conflict Resolution',
            'sf': 'Solution Feasibility',
            'overall': 'Overall Score'
        }
        
        print("\n" + "="*80)
        print("EXPERIMENT RESULTS SUMMARY")
        print("="*80)
        print(f"\nTotal experiments: {len(results)}")
        
        # Calculate averages for each system
        for metric in metrics:
            print(f"\n{metric_names[metric].upper()}:")
            print("-"*80)
            
            for system in systems:
                scores = []
                for result in results:
                    if system in result['evaluation']:
                        scores.append(result['evaluation'][system][metric])
                
                if scores:
                    avg = sum(scores) / len(scores)
                    std = (sum((x - avg) ** 2 for x in scores) / len(scores)) ** 0.5
                    min_score = min(scores)
                    max_score = max(scores)
                    
                    print(f"  {system:15s}: "
                          f"Mean={avg:.3f} Std={std:.3f} "
                          f"Min={min_score:.3f} Max={max_score:.3f}")
        
        # Improvement analysis
        print(f"\n{'='*80}")
        print("IMPROVEMENT ANALYSIS")
        print("="*80)
        
        for metric in metrics:
            semantic_scores = []
            conflict_scores = []
            cross_domain_scores = []  # NEW: Added cross-domain
            
            for result in results:
                if 'semantic' in result['evaluation']:
                    semantic_scores.append(result['evaluation']['semantic'][metric])
                if 'conflict_aware' in result['evaluation']:
                    conflict_scores.append(result['evaluation']['conflict_aware'][metric])
                if 'cross_domain' in result['evaluation']:  # NEW
                    cross_domain_scores.append(result['evaluation']['cross_domain'][metric])
            
            if semantic_scores and conflict_scores:
                semantic_avg = sum(semantic_scores) / len(semantic_scores)
                conflict_avg = sum(conflict_scores) / len(conflict_scores)
                improvement = ((conflict_avg - semantic_avg) / semantic_avg) * 100
                
                print(f"\n{metric_names[metric]}:")
                print(f"  Semantic baseline:     {semantic_avg:.3f}")
                print(f"  Conflict-aware:        {conflict_avg:.3f}")
                print(f"  Improvement:           {improvement:+.1f}%")
                
                # NEW: Add cross-domain comparison
                if cross_domain_scores:
                    cross_avg = sum(cross_domain_scores) / len(cross_domain_scores)
                    cross_improvement = ((cross_avg - semantic_avg) / semantic_avg) * 100
                    print(f"  Cross-domain:          {cross_avg:.3f}")
                    print(f"  Cross-domain improvement: {cross_improvement:+.1f}%")
        
        print("\n" + "="*80)


def main():
    """Run full experiment suite"""
    
    runner = ExperimentRunner()
    
    # Option 1: Quick test (2 queries per domain)
    print("\n" + "="*80)
    print("EXPERIMENT OPTIONS")
    print("="*80)
    print("1. Quick test (2 queries per domain = 6 total)")
    print("2. Full health domain (10 queries)")
    print("3. Full experiment (20 queries)")
    
    try:
        choice = input("\nSelect option [1/2/3]: ").strip()
    except:
        choice = "1"  # Default
    
    if choice == "1":
        # Quick test
        results = runner.run_all_experiments(
            domains=['health', 'education', 'travel'],
            max_per_domain=2
        )
    elif choice == "2":
        # Full health
        results = runner.run_all_experiments(
            domains=['health'],
            max_per_domain=None
        )
    else:
        # Full experiment
        results = runner.run_all_experiments()
    
    # Save and summarize
    runner.save_results(results)
    runner.print_summary(results)
    
    # Save summary to text file
    import sys
    from io import StringIO
    
    # Capture summary output
    old_stdout = sys.stdout
    sys.stdout = summary_buffer = StringIO()
    runner.print_summary(results)
    sys.stdout = old_stdout
    
    summary_text = summary_buffer.getvalue()
    
    with open('../results/experiment_summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary_text)
    
    print("\n✓ Saved summary to results/experiment_summary.txt")
    
    # NEW: Generate cross-domain visualizations
    print("\n" + "="*80)
    print("GENERATING CROSS-DOMAIN VISUALIZATIONS")
    print("="*80)
    try:
        from cross_domain_visualizer import CrossDomainVisualizer
        visualizer = CrossDomainVisualizer()
        visualizer.generate_all_visualizations()
    except Exception as e:
        print(f"⚠️  Visualization generation failed: {e}")
        print("   (This is optional - main results are still saved)")


if __name__ == "__main__":
    main()