"""
Statistical Analysis of Experiment Results

Performs:
1. Paired t-tests (Conflict-Aware vs Baselines)
2. Effect size calculation (Cohen's d)
3. Confidence intervals
"""

import json
import numpy as np
from scipy import stats
from pathlib import Path


class StatisticalAnalysis:
    """Perform statistical tests on experiment results"""
    
    def __init__(self, results_path='../results/experiment_results.json'):
        with open(results_path, 'r', encoding='utf-8') as f:
            self.results = json.load(f)
        
        print(f"✓ Loaded {len(self.results)} experiment results\n")
    
    def paired_t_test(self, system1: str, system2: str, metric: str = 'overall'):
        """
        Perform paired t-test comparing two systems
        
        Args:
            system1: First system name
            system2: Second system name
            metric: Metric to compare ('csr', 'crq', 'sf', 'overall')
            
        Returns:
            Dict with t-statistic, p-value, and interpretation
        """
        scores1 = []
        scores2 = []
        
        for result in self.results:
            if (system1 in result['evaluation'] and 
                system2 in result['evaluation']):
                scores1.append(result['evaluation'][system1][metric])
                scores2.append(result['evaluation'][system2][metric])
        
        if len(scores1) < 2:
            return {
                'error': 'Insufficient data for t-test',
                'n': len(scores1)
            }
        
        # Perform paired t-test
        t_stat, p_value = stats.ttest_rel(scores1, scores2)
        
        # Calculate means
        mean1 = np.mean(scores1)
        mean2 = np.mean(scores2)
        
        # Effect size (Cohen's d)
        diff = np.array(scores1) - np.array(scores2)
        cohens_d = np.mean(diff) / np.std(diff, ddof=1)
        
        # Interpretation
        if p_value < 0.001:
            significance = "***"
            interpretation = "highly significant"
        elif p_value < 0.01:
            significance = "**"
            interpretation = "very significant"
        elif p_value < 0.05:
            significance = "*"
            interpretation = "significant"
        else:
            significance = "ns"
            interpretation = "not significant"
        
        return {
            'system1': system1,
            'system2': system2,
            'metric': metric,
            'n': len(scores1),
            'mean1': mean1,
            'mean2': mean2,
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'significance': significance,
            'interpretation': interpretation
        }
    
    def calculate_confidence_interval(self, system: str, metric: str = 'overall', 
                                     confidence: float = 0.95):
        """
        Calculate confidence interval for a system's performance
        
        Args:
            system: System name
            metric: Metric to analyze
            confidence: Confidence level (default 0.95 for 95% CI)
            
        Returns:
            Dict with mean, CI, and margin of error
        """
        scores = []
        
        for result in self.results:
            if system in result['evaluation']:
                scores.append(result['evaluation'][system][metric])
        
        if len(scores) < 2:
            return {'error': 'Insufficient data'}
        
        scores = np.array(scores)
        mean = np.mean(scores)
        sem = stats.sem(scores)  # Standard error of mean
        
        # Calculate CI
        ci = stats.t.interval(confidence, len(scores)-1, loc=mean, scale=sem)
        
        return {
            'system': system,
            'metric': metric,
            'n': len(scores),
            'mean': mean,
            'std': np.std(scores, ddof=1),
            'ci_lower': ci[0],
            'ci_upper': ci[1],
            'margin_of_error': (ci[1] - ci[0]) / 2,
            'confidence_level': confidence
        }
    
    def run_all_tests(self):
        """Run comprehensive statistical analysis"""
        
        systems = ['zero_shot', 'semantic', 'conflict_aware', 'hybrid']
        metrics = ['csr', 'crq', 'sf', 'overall']
        
        print("="*80)
        print("STATISTICAL ANALYSIS")
        print("="*80)
        
        # 1. Main comparisons: Conflict-Aware vs others
        print("\n1. PAIRED T-TESTS: Conflict-Aware vs Baselines")
        print("-"*80)
        
        for system in ['zero_shot', 'semantic', 'hybrid']:
            for metric in metrics:
                result = self.paired_t_test('conflict_aware', system, metric)
                
                if 'error' not in result:
                    print(f"\nConflict-Aware vs {system.replace('_', ' ').title()} ({metric.upper()}):")
                    print(f"  Mean (Conflict-Aware): {result['mean1']:.3f}")
                    print(f"  Mean ({system}): {result['mean2']:.3f}")
                    print(f"  Difference: {result['mean1'] - result['mean2']:+.3f}")
                    print(f"  t-statistic: {result['t_statistic']:.3f}")
                    print(f"  p-value: {result['p_value']:.4f} {result['significance']}")
                    print(f"  Cohen's d: {result['cohens_d']:.3f}")
                    print(f"  Result: {result['interpretation']}")
        
        # 2. Confidence intervals
        print("\n\n2. CONFIDENCE INTERVALS (95%)")
        print("-"*80)
        
        for system in systems:
            ci = self.calculate_confidence_interval(system, 'overall')
            
            if 'error' not in ci:
                print(f"\n{system.replace('_', ' ').title()}:")
                print(f"  Mean: {ci['mean']:.3f}")
                print(f"  95% CI: [{ci['ci_lower']:.3f}, {ci['ci_upper']:.3f}]")
                print(f"  Margin of error: ±{ci['margin_of_error']:.3f}")
        
        # 3. Effect sizes
        print("\n\n3. EFFECT SIZES (Cohen's d)")
        print("-"*80)
        print("\nInterpretation:")
        print("  Small effect:   d = 0.2")
        print("  Medium effect:  d = 0.5")
        print("  Large effect:   d = 0.8")
        
        for system in ['zero_shot', 'semantic', 'hybrid']:
            result = self.paired_t_test('conflict_aware', system, 'overall')
            
            if 'error' not in result:
                d = result['cohens_d']
                
                if abs(d) < 0.2:
                    effect = "negligible"
                elif abs(d) < 0.5:
                    effect = "small"
                elif abs(d) < 0.8:
                    effect = "medium"
                else:
                    effect = "large"
                
                print(f"\nConflict-Aware vs {system.replace('_', ' ').title()}:")
                print(f"  Cohen's d: {d:.3f} ({effect} effect)")
        
        # 4. Summary
        print("\n\n4. SUMMARY")
        print("-"*80)
        
        # Count significant improvements
        significant_count = 0
        total_comparisons = 0
        
        for system in ['zero_shot', 'semantic']:
            for metric in metrics:
                result = self.paired_t_test('conflict_aware', system, metric)
                if 'error' not in result:
                    total_comparisons += 1
                    if result['p_value'] < 0.05:
                        significant_count += 1
        
        print(f"\nSignificant improvements: {significant_count}/{total_comparisons}")
        print(f"Percentage: {significant_count/total_comparisons*100:.1f}%")
        
        # Best system
        print("\n" + "="*80)
        
        means = {}
        for system in systems:
            scores = [r['evaluation'][system]['overall'] 
                     for r in self.results 
                     if system in r['evaluation']]
            if scores:
                means[system] = np.mean(scores)
        
        if means:
            best_system = max(means, key=means.get)
            print(f"✓ Best performing system: {best_system.replace('_', ' ').title()}")
            print(f"  Average overall score: {means[best_system]:.3f}")
        
        print("="*80 + "\n")
    
    def save_report(self, output_path='../results/statistical_analysis.txt'):
        """Save statistical analysis to text file"""
        
        import sys
        from io import StringIO
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = report_buffer = StringIO()
        
        self.run_all_tests()
        
        sys.stdout = old_stdout
        report_text = report_buffer.getvalue()
        
        # Save to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"✓ Saved statistical analysis to {output_path}")


def main():
    """Run statistical analysis and save report"""
    
    analyzer = StatisticalAnalysis()
    analyzer.run_all_tests()
    analyzer.save_report()


if __name__ == "__main__":
    main()