"""Baseline models - Logistic Regression & Random Forest"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score, f1_score
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import get_config, LABELS_DIR, PROCESSED_DATA_DIR, RESULTS_DIR
from src.utils.helpers import load_dataframe, save_dataframe

def prepare_data(features_df, labels_df, horizon=1):
    """Merge features and labels"""
    # Select label column
    label_col = f'label_{horizon}d'
    
    # Merge on Date and Ticker
    df = features_df.merge(
        labels_df[['Date', 'Ticker', label_col]],
        on=['Date', 'Ticker'],
        how='inner'
    )
    
    # Remove rows with NaN labels
    df = df.dropna(subset=[label_col])
    
    # Feature columns (exclude Date, Ticker, and OHLCV)
    feature_cols = [col for col in df.columns if col not in 
                   ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume', label_col]]
    
    # Remove rows with NaN features
    df = df.dropna(subset=feature_cols)
    
    X = df[feature_cols]
    y = df[label_col]
    dates = df['Date']
    tickers = df['Ticker']
    
    print(f"\nData shape: {X.shape}")
    print(f"Features: {len(feature_cols)}")
    print(f"Label distribution:")
    print(y.value_counts())
    
    return X, y, dates, tickers, feature_cols

def train_baseline_models(X, y, dates):
    """Train Logistic Regression and Random Forest with time series CV"""
    
    # Time series cross-validation
    tscv = TimeSeriesSplit(n_splits=5)
    
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced', n_jobs=-1)
    }
    
    results = {}
    
    for model_name, model in models.items():
        print(f"\n{'='*60}")
        print(f"Training: {model_name}")
        print('='*60)
        
        fold_scores = []
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X), 1):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train
            model.fit(X_train_scaled, y_train)
            
            # Predict
            y_pred = model.predict(X_test_scaled)
            
            # Metrics
            acc = accuracy_score(y_test, y_pred)
            f1_macro = f1_score(y_test, y_pred, average='macro')
            
            fold_scores.append({'fold': fold, 'accuracy': acc, 'f1_macro': f1_macro})
            
            print(f"Fold {fold}: Accuracy={acc:.4f}, F1-Macro={f1_macro:.4f}")
        
        # Average scores
        avg_acc = np.mean([s['accuracy'] for s in fold_scores])
        avg_f1 = np.mean([s['f1_macro'] for s in fold_scores])
        
        print(f"\nAverage: Accuracy={avg_acc:.4f}, F1-Macro={avg_f1:.4f}")
        
        results[model_name] = {
            'fold_scores': fold_scores,
            'avg_accuracy': avg_acc,
            'avg_f1_macro': avg_f1
        }
    
    return results

def main():
    print("="*60)
    print("BASELINE MODELS")
    print("="*60)
    
    config = get_config()
    
    # Load data
    print("\nLoading data...")
    features_df = load_dataframe(PROCESSED_DATA_DIR / "technical_features.parquet")
    labels_df = load_dataframe(LABELS_DIR / "all_labels.parquet")
    
    print(f"Features: {features_df.shape}")
    print(f"Labels: {labels_df.shape}")
    
    # Train for each horizon
    all_results = {}
    
    for horizon in config.horizons:
        print(f"\n{'#'*60}")
        print(f"HORIZON: {horizon} days")
        print('#'*60)
        
        X, y, dates, tickers, feature_cols = prepare_data(features_df, labels_df, horizon)
        
        results = train_baseline_models(X, y, dates)
        all_results[f'{horizon}d'] = results
    
    # Save results
    results_df = []
    for horizon, models_results in all_results.items():
        for model_name, metrics in models_results.items():
            results_df.append({
                'Horizon': horizon,
                'Model': model_name,
                'Avg_Accuracy': metrics['avg_accuracy'],
                'Avg_F1_Macro': metrics['avg_f1_macro']
            })
    
    results_df = pd.DataFrame(results_df)
    output_file = RESULTS_DIR / "tables" / "baseline_results.csv"
    results_df.to_csv(output_file, index=False)
    
    print("\n" + "="*60)
    print("BASELINE MODELS COMPLETE")
    print("="*60)
    print(f"\nResults saved to: {output_file}")
    print("\nSummary:")
    print(results_df.to_string(index=False))

if __name__ == "__main__":
    main()