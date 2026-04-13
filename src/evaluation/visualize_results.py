"""Visualize model results and create comparison plots"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import RESULTS_DIR

def load_all_results():
    """Load baseline and boosting results"""
    baseline_df = pd.read_csv(RESULTS_DIR / "tables" / "baseline_results.csv")
    boosting_df = pd.read_csv(RESULTS_DIR / "tables" / "boosting_results.csv")
    
    all_results = pd.concat([baseline_df, boosting_df], ignore_index=True)
    return all_results

def plot_f1_comparison():
    """Plot F1-Macro scores for all models"""
    results = load_all_results()
    
    # Create pivot table
    pivot = results.pivot(index='Horizon', columns='Model', values='Avg_F1_Macro')
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    pivot.plot(kind='bar', ax=ax, width=0.8)
    
    ax.set_title('F1-Macro Score Comparison Across Models and Horizons', fontsize=14, fontweight='bold')
    ax.set_xlabel('Prediction Horizon', fontsize=12)
    ax.set_ylabel('F1-Macro Score', fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 0.5)
    
    plt.tight_layout()
    output = RESULTS_DIR / "figures" / "f1_comparison.png"
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"Saved: {output}")
    plt.show()

def plot_accuracy_comparison():
    """Plot accuracy for all models"""
    results = load_all_results()
    
    pivot = results.pivot(index='Horizon', columns='Model', values='Avg_Accuracy')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    pivot.plot(kind='bar', ax=ax, width=0.8)
    
    ax.set_title('Accuracy Comparison Across Models and Horizons', fontsize=14, fontweight='bold')
    ax.set_xlabel('Prediction Horizon', fontsize=12)
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 1.0)
    
    plt.tight_layout()
    output = RESULTS_DIR / "figures" / "accuracy_comparison.png"
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"Saved: {output}")
    plt.show()

def create_summary_table():
    """Create formatted summary table"""
    results = load_all_results()
    
    # Best model per horizon
    best_models = []
    for horizon in results['Horizon'].unique():
        horizon_data = results[results['Horizon'] == horizon]
        best_f1 = horizon_data.loc[horizon_data['Avg_F1_Macro'].idxmax()]
        best_acc = horizon_data.loc[horizon_data['Avg_Accuracy'].idxmax()]
        
        best_models.append({
            'Horizon': horizon,
            'Best_F1_Model': best_f1['Model'],
            'Best_F1_Score': best_f1['Avg_F1_Macro'],
            'Best_Acc_Model': best_acc['Model'],
            'Best_Acc_Score': best_acc['Avg_Accuracy']
        })
    
    summary_df = pd.DataFrame(best_models)
    
    print("\n" + "="*70)
    print("BEST MODELS BY HORIZON")
    print("="*70)
    print(summary_df.to_string(index=False))
    
    output = RESULTS_DIR / "tables" / "best_models_summary.csv"
    summary_df.to_csv(output, index=False)
    print(f"\nSaved: {output}")
    
    return summary_df

def plot_horizon_performance():
    """Plot how performance degrades with horizon"""
    results = load_all_results()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # F1 by horizon
    for model in results['Model'].unique():
        model_data = results[results['Model'] == model]
        ax1.plot(model_data['Horizon'], model_data['Avg_F1_Macro'], marker='o', label=model, linewidth=2)
    
    ax1.set_title('F1-Macro vs Prediction Horizon', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Horizon', fontsize=11)
    ax1.set_ylabel('F1-Macro', fontsize=11)
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # Accuracy by horizon
    for model in results['Model'].unique():
        model_data = results[results['Model'] == model]
        ax2.plot(model_data['Horizon'], model_data['Avg_Accuracy'], marker='o', label=model, linewidth=2)
    
    ax2.set_title('Accuracy vs Prediction Horizon', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Horizon', fontsize=11)
    ax2.set_ylabel('Accuracy', fontsize=11)
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    output = RESULTS_DIR / "figures" / "horizon_performance.png"
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"Saved: {output}")
    plt.show()

def main():
    print("="*70)
    print("MODEL RESULTS VISUALIZATION")
    print("="*70)
    
    # Create all visualizations
    print("\n1. Creating F1 comparison plot...")
    plot_f1_comparison()
    
    print("\n2. Creating accuracy comparison plot...")
    plot_accuracy_comparison()
    
    print("\n3. Creating horizon performance plot...")
    plot_horizon_performance()
    
    print("\n4. Creating summary table...")
    create_summary_table()
    
    print("\n" + "="*70)
    print("VISUALIZATION COMPLETE")
    print("="*70)
    print(f"\nAll plots saved to: {RESULTS_DIR / 'figures'}")
    print(f"All tables saved to: {RESULTS_DIR / 'tables'}")

if __name__ == "__main__":
    main()