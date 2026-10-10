"""
Master Script for Week 6 Experiments

Runs the complete experimental pipeline:
1. Load test queries
2. Run all 4 systems on all queries
3. Evaluate with metrics
4. Generate visualizations
5. Perform statistical analysis
6. Save all results

Usage:
    python master_experiment.py
"""

from run_experiments import ExperimentRunner
from visualize_results import Visualizer
from statistical_analysis import StatisticalAnalysis
import time
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80 + "\n")


def main():
    """Run complete experimental pipeline"""
    
    start_time = time.time()
    
    print_header("WEEK 6: COMPREHENSIVE EXPERIMENTAL EVALUATION")
    
    print("This script will:")
    print("  1. Run 4 systems on all test queries")
    print("  2. Evaluate results with 3 metrics")
    print("  3. Generate visualizations")
    print("  4. Perform statistical analysis")
    print("  5. Save all results\n")
    
    # Check if results already exist
    results_path = Path('../results/experiment_results.json')
    
    if results_path.exists():
        print("⚠️  Existing results found at results/experiment_results.json")
        print("\nOptions:")
        print("  1. Load existing results (skip experiments)")
        print("  2. Run experiments again (overwrites existing)")
        
        try:
            choice = input("\nSelect option [1/2]: ").strip()
        except:
            choice = "1"
        
        if choice == "2":
            run_experiments = True
        else:
            run_experiments = False
    else:
        run_experiments = True
    
    # Step 1: Run experiments (if needed)
    if run_experiments:
        print_header("STEP 1: RUNNING EXPERIMENTS")
        
        print("Experiment options:")
        print("  1. Quick test (2 queries per domain = 6 total, ~10 minutes)")
        print("  2. Medium test (4 queries per domain = 12 total, ~30 minutes)")
        print("  3. Full experiment (all 20 queries, ~60 minutes)")
        
        try:
            exp_choice = input("\nSelect option [1/2/3]: ").strip()
        except:
            exp_choice = "1"
        
        runner = ExperimentRunner()
        
        if exp_choice == "1":
            results = runner.run_all_experiments(max_per_domain=2)
        elif exp_choice == "2":
            results = runner.run_all_experiments(max_per_domain=4)
        else:
            results = runner.run_all_experiments()
        
        # Save results
        runner.save_results(results)
        runner.print_summary(results)
        
        # Save text summary
        import sys
        from io import StringIO
        
        old_stdout = sys.stdout
        sys.stdout = summary_buffer = StringIO()
        runner.print_summary(results)
        sys.stdout = old_stdout
        
        summary_text = summary_buffer.getvalue()
        
        with open('../results/experiment_summary.txt', 'w', encoding='utf-8') as f:
            f.write(summary_text)
        
        print("\n✓ Saved experiment summary to results/experiment_summary.txt")
    
    else:
        print_header("STEP 1: LOADING EXISTING RESULTS")
        print("✓ Using existing results from results/experiment_results.json")
    
    # Step 2: Generate visualizations
    print_header("STEP 2: GENERATING VISUALIZATIONS")
    
    try:
        visualizer = Visualizer()
        visualizer.generate_all_plots()
    except Exception as e:
        print(f"⚠️  Visualization error: {e}")
        print("Continuing with statistical analysis...")
    
    # Step 3: Statistical analysis
    print_header("STEP 3: STATISTICAL ANALYSIS")
    
    try:
        analyzer = StatisticalAnalysis()
        analyzer.run_all_tests()
        analyzer.save_report()
    except Exception as e:
        print(f"⚠️  Statistical analysis error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    print_header("WEEK 6 EXPERIMENTS COMPLETE!")
    
    print(f"Total time: {minutes}m {seconds}s\n")
    
    print("Generated files:")
    print("  📊 results/experiment_results.json - Raw experimental data")
    print("  📄 results/experiment_summary.txt - Text summary")
    print("  📈 results/system_comparison.png - Main comparison chart")
    print("  📈 results/overall_scores.png - Overall performance")
    print("  📈 results/improvement_analysis.png - Improvement over baseline")
    print("  📈 results/domain_breakdown.png - Domain-specific analysis")
    print("  📊 results/statistical_analysis.txt - Statistical tests\n")
    
    print("="*80)
    print("Experimental evaluation is complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExperiment interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()