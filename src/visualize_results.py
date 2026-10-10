"""
Generate Visualizations for Experiment Results

Creates:
1. Bar chart comparing 4 systems
2. Breakdown by metric
3. Domain-specific analysis
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


class Visualizer:
    """Generate plots from experiment results"""
    
    def __init__(self, results_path='../results/experiment_results.json'):
        with open(results_path, 'r', encoding='utf-8') as f:
            self.results = json.load(f)
        
        print(f"✓ Loaded {len(self.results)} experiment results")
    
    def plot_system_comparison(self, save_path='../results/system_comparison.png'):
        """
        Main comparison plot: 4 systems across 3 metrics
        """
        systems = ['zero_shot', 'semantic', 'conflict_aware', 'hybrid']
        system_labels = ['Zero-shot', 'Semantic\nRAG', 'Conflict-Aware\nRAG', 'Hybrid\nRAG']
        metrics = ['csr', 'crq', 'sf']
        metric_labels = ['Constraint\nSatisfaction', 'Conflict\nResolution', 'Solution\nFeasibility']
        
        # Calculate averages
        avg_scores = {system: {metric: [] for metric in metrics} for system in systems}
        
        for result in self.results:
            for system in systems:
                if system in result['evaluation']:
                    for metric in metrics:
                        avg_scores[system][metric].append(
                            result['evaluation'][system][metric]
                        )
        
        # Compute means
        means = {system: {} for system in systems}
        for system in systems:
            for metric in metrics:
                if avg_scores[system][metric]:
                    means[system][metric] = np.mean(avg_scores[system][metric])
                else:
                    means[system][metric] = 0.0
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 7))
        
        x = np.arange(len(metrics))
        width = 0.2
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        for i, system in enumerate(systems):
            values = [means[system][m] for m in metrics]
            bars = ax.bar(x + i*width, values, width, label=system_labels[i], 
                         color=colors[i], alpha=0.8)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=9)
        
        ax.set_ylabel('Score (0-1)', fontsize=12, fontweight='bold')
        ax.set_title('System Performance Comparison Across Metrics', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels(metric_labels, fontsize=11)
        ax.legend(fontsize=10, loc='upper left')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_ylim([0, 1.1])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved comparison plot to {save_path}")
        plt.close()
    
    def plot_overall_scores(self, save_path='../results/overall_scores.png'):
        """
        Plot overall scores for all systems
        """
        systems = ['zero_shot', 'semantic', 'conflict_aware', 'hybrid']
        system_labels = ['Zero-shot', 'Semantic RAG', 'Conflict-Aware RAG', 'Hybrid RAG']
        
        # Calculate overall averages
        overall_scores = {system: [] for system in systems}
        
        for result in self.results:
            for system in systems:
                if system in result['evaluation']:
                    overall_scores[system].append(
                        result['evaluation'][system]['overall']
                    )
        
        means = [np.mean(overall_scores[s]) if overall_scores[s] else 0 
                for s in systems]
        stds = [np.std(overall_scores[s]) if overall_scores[s] else 0 
               for s in systems]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(systems))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        bars = ax.bar(x, means, color=colors, alpha=0.8, yerr=stds, 
                     capsize=5, error_kw={'linewidth': 2})
        
        # Add value labels
        for i, (bar, mean, std) in enumerate(zip(bars, means, stds)):
            ax.text(bar.get_x() + bar.get_width()/2., mean + std,
                   f'{mean:.3f}\n±{std:.3f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_ylabel('Overall Score (0-1)', fontsize=12, fontweight='bold')
        ax.set_title('Overall System Performance\n(Weighted Average of All Metrics)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(system_labels, fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_ylim([0, 1.1])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved overall scores plot to {save_path}")
        plt.close()
    
    def plot_improvement_analysis(self, save_path='../results/improvement_analysis.png'):
        """
        Show improvement of conflict-aware over semantic baseline
        """
        metrics = ['csr', 'crq', 'sf', 'overall']
        metric_labels = ['Constraint\nSatisfaction', 'Conflict\nResolution', 
                        'Solution\nFeasibility', 'Overall\nScore']
        
        improvements = []
        
        for metric in metrics:
            semantic_scores = []
            conflict_scores = []
            
            for result in self.results:
                if ('semantic' in result['evaluation'] and 
                    'conflict_aware' in result['evaluation']):
                    semantic_scores.append(result['evaluation']['semantic'][metric])
                    conflict_scores.append(result['evaluation']['conflict_aware'][metric])
            
            if semantic_scores and conflict_scores:
                semantic_avg = np.mean(semantic_scores)
                conflict_avg = np.mean(conflict_scores)
                improvement = ((conflict_avg - semantic_avg) / semantic_avg) * 100
                improvements.append(improvement)
            else:
                improvements.append(0)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(metrics))
        colors = ['#45B7D1' if imp > 0 else '#FF6B6B' for imp in improvements]
        
        bars = ax.bar(x, improvements, color=colors, alpha=0.8)
        
        # Add value labels
        for bar, imp in zip(bars, improvements):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{imp:+.1f}%',
                   ha='center', va='bottom' if imp > 0 else 'top', 
                   fontsize=11, fontweight='bold')
        
        ax.set_ylabel('Improvement (%)', fontsize=12, fontweight='bold')
        ax.set_title('Conflict-Aware RAG Improvement over Semantic Baseline', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(metric_labels, fontsize=11)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved improvement analysis to {save_path}")
        plt.close()
    
    def plot_domain_breakdown(self, save_path='../results/domain_breakdown.png'):
        """
        Compare systems across different domains
        """
        systems = ['zero_shot', 'semantic', 'conflict_aware', 'hybrid']
        system_labels = ['Zero-shot', 'Semantic', 'Conflict-Aware', 'Hybrid']
        domains = ['health', 'education', 'travel']
        
        # Calculate scores by domain
        domain_scores = {domain: {system: [] for system in systems} 
                        for domain in domains}
        
        for result in self.results:
            domain = result['test_case']['domain']
            for system in systems:
                if system in result['evaluation']:
                    domain_scores[domain][system].append(
                        result['evaluation'][system]['overall']
                    )
        
        # Compute means
        means = {domain: {} for domain in domains}
        for domain in domains:
            for system in systems:
                if domain_scores[domain][system]:
                    means[domain][system] = np.mean(domain_scores[domain][system])
                else:
                    means[domain][system] = 0.0
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(domains))
        width = 0.2
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        for i, system in enumerate(systems):
            values = [means[d][system] for d in domains]
            ax.bar(x + i*width, values, width, label=system_labels[i], 
                  color=colors[i], alpha=0.8)
        
        ax.set_ylabel('Overall Score (0-1)', fontsize=12, fontweight='bold')
        ax.set_title('System Performance by Domain', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels([d.capitalize() for d in domains], fontsize=11)
        ax.legend(fontsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_ylim([0, 1.1])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved domain breakdown to {save_path}")
        plt.close()
    
    def generate_all_plots(self):
        """Generate all visualization plots"""
        
        print("\n" + "="*70)
        print("GENERATING VISUALIZATIONS")
        print("="*70 + "\n")
        
        self.plot_system_comparison()
        self.plot_overall_scores()
        self.plot_improvement_analysis()
        self.plot_domain_breakdown()
        
        print("\n" + "="*70)
        print("✓ All visualizations complete!")
        print("="*70)


def main():
    """Generate all plots from experiment results"""
    
    visualizer = Visualizer()
    visualizer.generate_all_plots()


if __name__ == "__main__":
    main()