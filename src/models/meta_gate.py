"""
Meta-labeling gate - Execute signals only when reliable
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import get_config, LABELS_DIR, PROCESSED_DATA_DIR, RESULTS_DIR
from src.utils.helpers import load_dataframe, save_dataframe

def create_meta_labels(features_df, labels_df, predictions_df, horizon=1):
    """Create meta-labels: 1 if base prediction was correct, 0 otherwise"""
    
    label_col = f'label_{horizon}d'
    
    # Merge all data
    df = features_df.merge(
        labels_df[['Date', 'Ticker', label_col]],
        on=['Date', 'Ticker'],
        how='inner'
    )
    
    # Drop NaN labels
    df = df.dropna(subset=[label_col])
    
    # Simulate base model predictions (use simple rule)
    df['base_prediction'] = 0  # Default HOLD
    
    # Simple rule: BUY if RSI < 30, SELL if RSI > 70
    if 'rsi_14' in df.columns:
        df.loc[df['rsi_14'] < 30, 'base_prediction'] = 1  # BUY
        df.loc[df['rsi_14'] > 70, 'base_prediction'] = -1  # SELL
    
    # Convert labels to same scale
    true_labels = df[label_col].map({-1: -1, 0: 0, 1: 1})
    
    # Meta-label: 1 if prediction matches truth (ignoring HOLD)
    df['correct'] = 0
    df.loc[
        (df['base_prediction'] != 0) & 
        (df['base_prediction'] == true_labels),
        'correct'
    ] = 1
    
    # Meta-label: only for non-HOLD predictions
    df['should_execute'] = 0
    df.loc[df['base_prediction'] != 0, 'should_execute'] = df.loc[df['base_prediction'] != 0, 'correct']
    
    print(f"\nMeta-labels created:")
    print(f"  Total predictions: {len(df)}")
    print(f"  Non-HOLD predictions: {(df['base_prediction'] != 0).sum()}")
    print(f"  Correct predictions: {df['correct'].sum()}")
    print(f"  Accuracy (non-HOLD): {df['correct'].mean():.3f}")
    
    return df

def train_meta_gate(df, horizon=1):
    """Train logistic regression gate"""
    
    print(f"\n{'='*60}")
    print(f"Training Meta-Labeling Gate - {horizon}d horizon")
    print('='*60)
    
    # Features for gate
    gate_features = []
    
    # Base prediction strength
    gate_features.append('base_prediction')
    
    # AI-Index (if available)
    if 'ai_index' in df.columns:
        df['ai_index_filled'] = df['ai_index'].fillna(df['ai_index'].mean())
        gate_features.append('ai_index_filled')
    
    # Regime features
    regime_cols = ['volume_zscore', 'volatility_10d', 'rsi_14']
    for col in regime_cols:
        if col in df.columns:
            gate_features.append(col)
    
    print(f"Gate features: {gate_features}")
    
    # Filter to non-HOLD predictions only
    df_filtered = df[df['base_prediction'] != 0].copy()
    
    # Drop rows with NaN in gate features
    df_filtered = df_filtered.dropna(subset=gate_features)
    
    print(f"Training samples: {len(df_filtered)}")
    
    if len(df_filtered) < 100:
        print("Insufficient data for gate training")
        return None, None
    
    X = df_filtered[gate_features]
    y = df_filtered['correct']
    
    # Time series CV
    tscv = TimeSeriesSplit(n_splits=3)
    
    fold_results = []
    
    for fold, (train_idx, test_idx) in enumerate(tscv.split(X), 1):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        # Scale
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train gate
        gate = LogisticRegression(random_state=42, class_weight='balanced')
        gate.fit(X_train_scaled, y_train)
        
        # Predict
        y_pred = gate.predict(X_test_scaled)
        
        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        
        fold_results.append({
            'fold': fold,
            'accuracy': acc,
            'precision': prec,
            'recall': rec
        })
        
        print(f"Fold {fold}: Acc={acc:.3f}, Prec={prec:.3f}, Rec={rec:.3f}")
    
    # Average
    avg_acc = np.mean([r['accuracy'] for r in fold_results])
    avg_prec = np.mean([r['precision'] for r in fold_results])
    avg_rec = np.mean([r['recall'] for r in fold_results])
    
    print(f"\nAverage: Acc={avg_acc:.3f}, Prec={avg_prec:.3f}, Rec={avg_rec:.3f}")
    
    results = {
        'fold_results': fold_results,
        'avg_accuracy': avg_acc,
        'avg_precision': avg_prec,
        'avg_recall': avg_rec,
        'gate_features': gate_features
    }
    
    return None, results

def main():
    """Main execution"""
    print("="*60)
    print("META-LABELING GATE")
    print("="*60)
    
    config = get_config()
    
    # Load data
    print("\nLoading features...")
    tech_file = PROCESSED_DATA_DIR / "technical_features.parquet"
    features_df = load_dataframe(tech_file)
    
    # CRITICAL FIX: Remove timezone from features_df
    features_df['Date'] = pd.to_datetime(features_df['Date']).dt.tz_localize(None)
    
    # Try to load AI-index
    ai_file = PROCESSED_DATA_DIR / "ai_index.parquet"
    if ai_file.exists():
        try:
            ai_df = load_dataframe(ai_file)
            # Remove timezone from AI-index too
            ai_df['Date'] = pd.to_datetime(ai_df['Date']).dt.tz_localize(None)
            
            features_df = features_df.merge(
                ai_df[['Date', 'Ticker', 'ai_index']],
                on=['Date', 'Ticker'],
                how='left'
            )
            print("AI-Index merged")
        except Exception as e:
            print(f"Warning: Could not merge AI-Index: {e}")
    
    labels_df = load_dataframe(LABELS_DIR / "all_labels.parquet")
    # Remove timezone from labels too
    labels_df['Date'] = pd.to_datetime(labels_df['Date']).dt.tz_localize(None)
    
    # Train gate for each horizon
    all_results = {}
    
    for horizon in config.horizons:
        print(f"\n{'#'*60}")
        print(f"HORIZON: {horizon} days")
        print('#'*60)
        
        try:
            # Create meta-labels
            meta_df = create_meta_labels(features_df, labels_df, None, horizon)
            
            # Train gate
            gate, results = train_meta_gate(meta_df, horizon)
            
            if results:
                all_results[f'{horizon}d'] = results
        except Exception as e:
            print(f"\n✗ Error processing {horizon}d: {e}")
            continue
    
    # Save results
    if all_results:
        results_list = []
        for horizon, res in all_results.items():
            results_list.append({
                'Horizon': horizon,
                'Accuracy': res['avg_accuracy'],
                'Precision': res['avg_precision'],
                'Recall': res['avg_recall']
            })
        
        results_df = pd.DataFrame(results_list)
        output = RESULTS_DIR / "tables" / "meta_gate_results.csv"
        results_df.to_csv(output, index=False)
        
        print("\n" + "="*60)
        print("META-GATE COMPLETE")
        print("="*60)
        print(f"\nResults saved to: {output}")
        print("\nSummary:")
        print(results_df.to_string(index=False))
    else:
        print("\n⚠️  No meta-gate results generated")

if __name__ == "__main__":
    main()