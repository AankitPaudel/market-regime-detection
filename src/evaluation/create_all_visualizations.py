"""
Create all visualization plots for the project
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import RESULTS_DIR, RAW_DATA_DIR, LABELS_DIR
from src.utils.helpers import load_dataframe

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def plot_price_history():
    """Plot price history for all tickers"""
    
    print("\n1. Creating price history plot...")
    
    prices = load_dataframe(RAW_DATA_DIR / "prices" / "all_tickers.parquet")
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()
    
    tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
    
    for i, ticker in enumerate(tickers):
        data = prices[prices['Ticker'] == ticker]
        axes[i].plot(data['Date'], data['Close'], linewidth=1.5)
        axes[i].set_title(f'{ticker} Price History', fontsize=12, fontweight='bold')
        axes[i].set_xlabel('Date')
        axes[i].set_ylabel('Price ($)')
        axes[i].grid(alpha=0.3)
        axes[i].tick_params(axis='x', rotation=45)
    
    # Remove empty subplot
    axes[5].axis('off')
    
    plt.tight_layout()
    output = RESULTS_DIR / "figures" / "price_history.png"
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"   Saved: {output}")
    plt.close()

def plot_label_distributions():
    """Plot label distributions"""
    
    print("\n2. Creating label distribution plots...")
    
    labels = load_dataframe(LABELS_DIR / "all_labels.parquet")
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    label_cols = ['label_1d', 'label_3d', 'label_5d']
    label_names = {-1: 'SELL', 0: 'HOLD', 1: 'BUY'}
    
    for i, col in enumerate(label_cols):
        counts = labels[col].value_counts().sort_index()
        bars = axes[i].bar(range(len(counts)), counts.values, 
                          color=['red', 'gray', 'green'], alpha=0.7)
        axes[i].set_xticks(range(len(counts)))
        axes[i].set_xticklabels([label_names[idx] for idx in counts.index])
        axes[i].set_title(f'{col.upper()} Distribution', fontsize=12, fontweight='bold')
        axes[i].set_ylabel('Count')
        axes[i].grid(axis='y', alpha=0.3)
        
        # Add percentage labels
        total = counts.sum()
        for j, bar in enumerate(bars):
            height = bar.get_height()
            axes[i].text(bar.get_x() + bar.get_width()/2., height,
                        f'{height/total:.1%}',
                        ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    output = RESULTS_DIR / "figures" / "label_distributions.png"
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"   Saved: {output}")
    plt.close()

def plot_model_comparison():
    """Plot model comparison"""
    
    print("\n3. Creating model comparison plot...")
    
    # Load all results
    baseline_file = RESULTS_DIR / "tables" / "baseline_results.csv"
    boosting_file = RESULTS_DIR / "tables" / "boosting_results.csv"
    
    if not baseline_file.exists() or not boosting_file.exists():
        print("   Skipping - results files not found")
        return
    
    baseline_df = pd.read_csv(baseline_file)
    boosting_df = pd.read_csv(boosting_file)
    
    all_results = pd.concat([baseline_df, boosting_df], ignore_index=True)
    
    # F1 comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    pivot_f1 = all_results.pivot(index='Horizon', columns='Model', values='Avg_F1_Macro')
    pivot_f1.plot(kind='bar', ax=ax1, width=0.8)
    ax1.set_title('F1-Macro Score by Model and Horizon', fontsize=13, fontweight='bold')
    ax1.set_xlabel('Prediction Horizon')
    ax1.set_ylabel('F1-Macro Score')
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0)
    ax1.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylim(0, 0.5)
    
    # Accuracy comparison
    pivot_acc = all_results.pivot(index='Horizon', columns='Model', values='Avg_Accuracy')
    pivot_acc.plot(kind='bar', ax=ax2, width=0.8)
    ax2.set_title('Accuracy by Model and Horizon', fontsize=13, fontweight='bold')
    ax2.set_xlabel('Prediction Horizon')
    ax2.set_ylabel('Accuracy')
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0)
    ax2.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_ylim(0, 1.0)
    
    plt.tight_layout()
    output = RESULTS_DIR / "figures" / "model_comparison.png"
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"   Saved: {output}")
    plt.close()

def plot_backtest_results():
    """Plot backtest results"""
    
    print("\n4. Creating backtest results plot...")
    
    backtest_file = RESULTS_DIR / "tables" / "backtest_results.csv"
    
    if not backtest_file.exists():
        print("   Skipping - backtest results not found")
        return
    
    backtest_df = pd.read_csv(backtest_file)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Sharpe Ratio
    axes[0, 0].bar(backtest_df['Horizon'], backtest_df['Sharpe_Ratio'], 
                   color='steelblue', alpha=0.7)
    axes[0, 0].set_title('Sharpe Ratio by Horizon', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Horizon')
    axes[0, 0].set_ylabel('Sharpe Ratio')
    axes[0, 0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    axes[0, 0].grid(axis='y', alpha=0.3)
    
    # Win Rate
    axes[0, 1].bar(backtest_df['Horizon'], backtest_df['Win_Rate'] * 100, 
                   color='green', alpha=0.7)
    axes[0, 1].set_title('Win Rate by Horizon', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Horizon')
    axes[0, 1].set_ylabel('Win Rate (%)')
    axes[0, 1].axhline(y=50, color='red', linestyle='--', alpha=0.5)
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # Max Drawdown
    axes[1, 0].bar(backtest_df['Horizon'], backtest_df['Max_Drawdown'] * 100, 
                   color='red', alpha=0.7)
    axes[1, 0].set_title('Maximum Drawdown by Horizon', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Horizon')
    axes[1, 0].set_ylabel('Max Drawdown (%)')
    axes[1, 0].grid(axis='y', alpha=0.3)
    
    # CAGR
    axes[1, 1].bar(backtest_df['Horizon'], backtest_df['CAGR'] * 100, 
                   color='purple', alpha=0.7)
    axes[1, 1].set_title('CAGR by Horizon', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Horizon')
    axes[1, 1].set_ylabel('CAGR (%)')
    axes[1, 1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    axes[1, 1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output = RESULTS_DIR / "figures" / "backtest_performance.png"
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"   Saved: {output}")
    plt.close()

def plot_ai_index_distribution():
    """Plot AI-Index distribution if available"""
    
    print("\n5. Creating AI-Index distribution plot...")
    
    from src.utils.config import PROCESSED_DATA_DIR
    ai_file = PROCESSED_DATA_DIR / "ai_index.parquet"
    
    if not ai_file.exists():
        print("   Skipping - AI-Index not found")
        return
    
    ai_df = load_dataframe(ai_file)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Distribution
    axes[0].hist(ai_df['ai_index'].dropna(), bins=50, alpha=0.7, color='purple', edgecolor='black')
    axes[0].set_title('AI-Intensity Index Distribution', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('AI-Index A(t)')
    axes[0].set_ylabel('Frequency')
    axes[0].grid(axis='y', alpha=0.3)
    axes[0].axvline(x=0.5, color='red', linestyle='--', label='Median')
    axes[0].legend()
    
    # Time series (sample)
    sample_ticker = 'AAPL'
    sample_data = ai_df[ai_df['Ticker'] == sample_ticker].sort_values('Date')
    
    axes[1].plot(sample_data['Date'], sample_data['ai_index'], linewidth=1, alpha=0.7)
    axes[1].set_title(f'AI-Index Over Time ({sample_ticker})', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Date')
    axes[1].set_ylabel('AI-Index A(t)')
    axes[1].grid(alpha=0.3)
    axes[1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    output = RESULTS_DIR / "figures" / "ai_index_distribution.png"
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"   Saved: {output}")
    plt.close()

def create_summary_table():
    """Create summary comparison table"""
    
    print("\n6. Creating summary table...")
    
    baseline_file = RESULTS_DIR / "tables" / "baseline_results.csv"
    boosting_file = RESULTS_DIR / "tables" / "boosting_results.csv"
    backtest_file = RESULTS_DIR / "tables" / "backtest_results.csv"
    
    if not all([baseline_file.exists(), boosting_file.exists()]):
        print("   Skipping - results files not found")
        return
    
    baseline_df = pd.read_csv(baseline_file)
    boosting_df = pd.read_csv(boosting_file)
    
    all_results = pd.concat([baseline_df, boosting_df], ignore_index=True)
    
    # Find best model for each horizon
    best_models = []
    for horizon in all_results['Horizon'].unique():
        horizon_data = all_results[all_results['Horizon'] == horizon]
        best_idx = horizon_data['Avg_F1_Macro'].idxmax()
        best = horizon_data.loc[best_idx]
        best_models.append({
            'Horizon': horizon,
            'Best_Model': best['Model'],
            'F1_Macro': best['Avg_F1_Macro'],
            'Accuracy': best['Avg_Accuracy']
        })
    
    summary_df = pd.DataFrame(best_models)
    
    # Add backtest metrics if available
    if backtest_file.exists():
        backtest_df = pd.read_csv(backtest_file)
        summary_df = summary_df.merge(
            backtest_df[['Horizon', 'Sharpe_Ratio', 'Win_Rate', 'Max_Drawdown']],
            on='Horizon',
            how='left'
        )
    
    output = RESULTS_DIR / "tables" / "project_summary.csv"
    summary_df.to_csv(output, index=False)
    print(f"   Saved: {output}")
    
    print("\n" + "="*70)
    print("PROJECT SUMMARY")
    print("="*70)
    print(summary_df.to_string(index=False))

def main():
    """Main execution"""
    print("="*60)
    print("CREATING ALL VISUALIZATIONS")
    print("="*60)
    
    plot_price_history()
    plot_label_distributions()
    plot_model_comparison()
    plot_backtest_results()
    plot_ai_index_distribution()
    create_summary_table()
    
    print("\n" + "="*60)
    print("✓ ALL VISUALIZATIONS COMPLETE")
    print("="*60)
    print(f"\nAll figures saved to: {RESULTS_DIR / 'figures'}")
    print(f"All tables saved to: {RESULTS_DIR / 'tables'}")

if __name__ == "__main__":
    main()