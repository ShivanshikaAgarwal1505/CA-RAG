"""
Cross-Domain Transfer Visualizer

Creates visualizations specifically for cross-domain transfer:
1. Cross-domain usage by test case
2. Source domain distribution
3. Cross-domain vs same-domain performance
4. Conflict pattern transfer heatmap
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict
import numpy as np


class CrossDomainVisualizer:
    """Visualize cross-domain transfer patterns"""
    
    def __init__(self, results_dir: str = '../results'):
        self.results_dir = Path(results_dir)
        self.cross_domain_dir = self.results_dir / 'cross_domain_details'
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def load_cross_domain_data(self):
        """Load all cross-domain transfer data"""
        
        if not self.cross_domain_dir.exists():
            print(f"❌ Cross-domain directory not found: {self.cross_domain_dir}")
            return []
        
        data = []
        for file_path in self.cross_domain_dir.glob('*_cross_domain.json'):
            with open(file_path, 'r') as f:
                data.append(json.load(f))
        
        return data
    
    def plot_cross_domain_usage(self, save_path=None):
        """Plot cross-domain usage per test case"""
        
        data = self.load_cross_domain_data()
        if not data:
            print("No cross-domain data found")
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        test_ids = [d['test_id'] for d in data]
        same_domain = [d['same_domain_count'] for d in data]
        cross_domain = [d['cross_domain_count'] for d in data]
        
        x = np.arange(len(test_ids))
        width = 0.6
        
        # Stacked bar chart
        ax.bar(x, same_domain, width, label='Same-domain', color='skyblue')
        ax.bar(x, cross_domain, width, bottom=same_domain, 
               label='Cross-domain', color='coral')
        
        ax.set_xlabel('Test Case', fontsize=12)
        ax.set_ylabel('Number of Examples', fontsize=12)
        ax.set_title('Cross-Domain vs Same-Domain Retrieval per Test Case', 
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(test_ids, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {save_path}")
        else:
            plt.savefig(self.results_dir / 'cross_domain_usage.png', 
                       dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {self.results_dir / 'cross_domain_usage.png'}")
        
        plt.close()
    
    def plot_domain_distribution(self, save_path=None):
        """Plot source domain distribution for cross-domain transfers"""
        
        data = self.load_cross_domain_data()
        if not data:
            return
        
        # Count by target domain
        by_target = defaultdict(lambda: {'same': 0, 'cross': 0})
        
        for d in data:
            target = d['target_domain']
            by_target[target]['same'] += d['same_domain_count']
            by_target[target]['cross'] += d['cross_domain_count']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        domains = list(by_target.keys())
        same_counts = [by_target[d]['same'] for d in domains]
        cross_counts = [by_target[d]['cross'] for d in domains]
        
        x = np.arange(len(domains))
        width = 0.35
        
        ax.bar(x - width/2, same_counts, width, label='Same-domain', color='skyblue')
        ax.bar(x + width/2, cross_counts, width, label='Cross-domain', color='coral')
        
        ax.set_xlabel('Target Domain', fontsize=12)
        ax.set_ylabel('Total Retrievals', fontsize=12)
        ax.set_title('Retrieval Distribution by Target Domain', 
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([d.capitalize() for d in domains])
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add percentages on bars
        for i, d in enumerate(domains):
            total = same_counts[i] + cross_counts[i]
            if total > 0:
                pct = cross_counts[i] / total * 100
                ax.text(i, total + 0.5, f'{pct:.1f}%', 
                       ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {save_path}")
        else:
            plt.savefig(self.results_dir / 'domain_distribution.png', 
                       dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {self.results_dir / 'domain_distribution.png'}")
        
        plt.close()
    
    def plot_cross_domain_rate(self, save_path=None):
        """Plot cross-domain usage rate"""
        
        data = self.load_cross_domain_data()
        if not data:
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        test_ids = [d['test_id'] for d in data]
        rates = [d['cross_domain_count'] / d['total_examples'] * 100 
                if d['total_examples'] > 0 else 0 for d in data]
        
        colors = ['coral' if r > 0 else 'lightgray' for r in rates]
        
        ax.bar(test_ids, rates, color=colors, alpha=0.8)
        ax.axhline(y=33.3, color='red', linestyle='--', linewidth=2, 
                  label='Target (33% cross-domain)')
        
        ax.set_xlabel('Test Case', fontsize=12)
        ax.set_ylabel('Cross-Domain Rate (%)', fontsize=12)
        ax.set_title('Cross-Domain Transfer Rate per Test Case', 
                    fontsize=14, fontweight='bold')
        ax.set_xticklabels(test_ids, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for i, (test, rate) in enumerate(zip(test_ids, rates)):
            ax.text(i, rate + 2, f'{rate:.1f}%', 
                   ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {save_path}")
        else:
            plt.savefig(self.results_dir / 'cross_domain_rate.png', 
                       dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {self.results_dir / 'cross_domain_rate.png'}")
        
        plt.close()
    
    def generate_all_visualizations(self):
        """Generate all cross-domain visualizations"""
        
        print("="*70)
        print("GENERATING CROSS-DOMAIN VISUALIZATIONS")
        print("="*70)
        
        print("\n1. Cross-domain usage per test case...")
        self.plot_cross_domain_usage()
        
        print("\n2. Domain distribution...")
        self.plot_domain_distribution()
        
        print("\n3. Cross-domain rate...")
        self.plot_cross_domain_rate()
        
        print("\n" + "="*70)
        print("✓ All cross-domain visualizations complete!")
        print("="*70)


# TEST
if __name__ == "__main__":
    print("="*70)
    print("TESTING CROSS-DOMAIN VISUALIZER")
    print("="*70)
    
    visualizer = CrossDomainVisualizer()
    
    # Check if data exists
    data = visualizer.load_cross_domain_data()
    if data:
        print(f"\n✓ Found {len(data)} test cases with cross-domain data")
        
        # Generate visualizations
        visualizer.generate_all_visualizations()
    else:
        print("\n⚠️  No cross-domain data found")
        print("   Run experiments with enhanced tracking first")
        print("   Then run this visualizer")
    
    print("\n" + "="*70)
    print("✓ Test complete!")
    print("="*70)