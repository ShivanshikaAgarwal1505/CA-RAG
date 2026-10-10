"""
Analyze retrieval results and generate insights
"""

import json
import matplotlib.pyplot as plt
import numpy as np

def analyze_results():
    # Load evaluation results
    with open('../data/retrieval_evaluation.json', 'r') as f:
        results = json.load(f)
    
    # Calculate averages
    methods = ['conflict', 'semantic', 'hybrid']
    avg_precision = {m: np.mean(results[m]) for m in methods}
    
    # Plot
    plt.figure(figsize=(10, 6))
    
    # Bar chart
    plt.subplot(1, 2, 1)
    plt.bar(methods, [avg_precision[m] for m in methods], 
            color=['#2ecc71', '#3498db', '#9b59b6'])
    plt.ylabel('Precision@3')
    plt.title('Retrieval Method Comparison')
    plt.ylim(0, 1)
    
    # Add value labels on bars
    for i, m in enumerate(methods):
        plt.text(i, avg_precision[m] + 0.02, f'{avg_precision[m]:.2f}', 
                ha='center')
    
    # Box plot (if you have results for multiple cases)
    plt.subplot(1, 2, 2) 
    plt.boxplot([results[m] for m in methods], labels=methods)
    plt.ylabel('Precision@3')
    plt.title('Precision Distribution')
    plt.ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig('../results/retrieval_comparison.png', dpi=300)
    print("✓ Plot saved to results/retrieval_comparison.png")
    
    # Print summary
    print("\n" + "="*50)
    print("RETRIEVAL ANALYSIS SUMMARY")
    print("="*50)
    
    for method in methods:
        print(f"\n{method.upper()}:")
        print(f"  Average Precision@3: {avg_precision[method]:.3f}")
        print(f"  Min: {min(results[method]):.3f}")
        print(f"  Max: {max(results[method]):.3f}")
    
    # Calculate improvement
    if avg_precision['conflict'] > avg_precision['semantic']:
        improvement = (avg_precision['conflict'] - avg_precision['semantic']) / avg_precision['semantic'] * 100
        print(f"\n🎉 Conflict-aware is {improvement:.1f}% better than semantic!")
    

if __name__ == "__main__":
    # Create results directory if needed
    import os
    os.makedirs('../results', exist_ok=True)
    
    analyze_results()