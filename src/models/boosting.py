"""LightGBM and XGBoost models"""
import pandas as pd
import numpy as np
from pathlib import Path
import lightgbm as lgb
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score, f1_score, roc_auc_score
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import get_config, LABELS_DIR, PROCESSED_DATA_DIR, RESULTS_DIR, MODELS_DIR
from src.utils.helpers import load_dataframe

def prepare_data(features_df, labels_df, horizon=1):
    """Merge features and labels"""
    label_col = f'label_{horizon}d'
    
    df = features_df.merge(
        labels_df[['Date', 'Ticker', label_col]],
        on=['Date', 'Ticker'],
        how='inner'
    )
    
    df = df.dropna(subset=[label_col])
    
    feature_cols = [col for col in df.columns if col not in 
                   ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume', label_col]]
    
    df = df.dropna(subset=feature_cols)
    
    X = df[feature_cols]
    y = df[label_col]
    dates = df['Date']
    
    # Convert labels to 0, 1, 2 for classification
    y_mapped = y.map({-1: 0, 0: 1, 1: 2})
    
    print(f"\nData shape: {X.shape}")
    print(f"Features: {len(feature_cols)}")
    print(f"Label distribution:")
    print(y.value_counts())
    
    return X, y_mapped, dates, feature_cols

def calculate_class_weights(y):
    """Calculate class weights for imbalanced data"""
    from sklearn.utils.class_weight import compute_class_weight
    
    classes = np.unique(y)
    weights = compute_class_weight('balanced', classes=classes, y=y)
    return dict(zip(classes, weights))

def train_lightgbm(X, y, dates):
    """Train LightGBM with time series CV"""
    print(f"\n{'='*60}")
    print(f"Training: LightGBM")
    print('='*60)
    
    tscv = TimeSeriesSplit(n_splits=5)
    fold_scores = []
    
    # Calculate class weights
    class_weights = calculate_class_weights(y)
    print(f"Class weights: {class_weights}")
    
    for fold, (train_idx, test_idx) in enumerate(tscv.split(X), 1):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        # LightGBM parameters
        params = {
            'objective': 'multiclass',
            'num_class': 3,
            'metric': 'multi_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'random_state': 42,
            'n_jobs': -1
        }
        
        # Create datasets
        train_data = lgb.Dataset(X_train, label=y_train)
        test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        
        # Train
        model = lgb.train(
            params,
            train_data,
            num_boost_round=500,
            valid_sets=[test_data],
            callbacks=[lgb.early_stopping(stopping_rounds=50), lgb.log_evaluation(0)]
        )
        
        # Predict
        y_pred_proba = model.predict(X_test, num_iteration=model.best_iteration)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        # Metrics
        acc = accuracy_score(y_test, y_pred)
        f1_macro = f1_score(y_test, y_pred, average='macro')
        
        fold_scores.append({'fold': fold, 'accuracy': acc, 'f1_macro': f1_macro})
        
        print(f"Fold {fold}: Accuracy={acc:.4f}, F1-Macro={f1_macro:.4f}")
    
    avg_acc = np.mean([s['accuracy'] for s in fold_scores])
    avg_f1 = np.mean([s['f1_macro'] for s in fold_scores])
    
    print(f"\nAverage: Accuracy={avg_acc:.4f}, F1-Macro={avg_f1:.4f}")
    
    return {
        'fold_scores': fold_scores,
        'avg_accuracy': avg_acc,
        'avg_f1_macro': avg_f1
    }

def train_xgboost(X, y, dates):
    """Train XGBoost with time series CV"""
    print(f"\n{'='*60}")
    print(f"Training: XGBoost")
    print('='*60)
    
    tscv = TimeSeriesSplit(n_splits=5)
    fold_scores = []
    
    # Calculate class weights
    class_weights = calculate_class_weights(y)
    sample_weights = np.array([class_weights[label] for label in y])
    
    for fold, (train_idx, test_idx) in enumerate(tscv.split(X), 1):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        weights_train = sample_weights[train_idx]
        
        # XGBoost parameters
        params = {
            'objective': 'multi:softprob',
            'num_class': 3,
            'eval_metric': 'mlogloss',
            'max_depth': 6,
            'learning_rate': 0.05,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'n_jobs': -1,
            'tree_method': 'hist'
        }
        
        # Train
        model = xgb.XGBClassifier(**params, n_estimators=500, early_stopping_rounds=50)
        model.fit(
            X_train, y_train,
            sample_weight=weights_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Predict
        y_pred = model.predict(X_test)
        
        # Metrics
        acc = accuracy_score(y_test, y_pred)
        f1_macro = f1_score(y_test, y_pred, average='macro')
        
        fold_scores.append({'fold': fold, 'accuracy': acc, 'f1_macro': f1_macro})
        
        print(f"Fold {fold}: Accuracy={acc:.4f}, F1-Macro={f1_macro:.4f}")
    
    avg_acc = np.mean([s['accuracy'] for s in fold_scores])
    avg_f1 = np.mean([s['f1_macro'] for s in fold_scores])
    
    print(f"\nAverage: Accuracy={avg_acc:.4f}, F1-Macro={avg_f1:.4f}")
    
    return {
        'fold_scores': fold_scores,
        'avg_accuracy': avg_acc,
        'avg_f1_macro': avg_f1
    }

def main():
    print("="*60)
    print("BOOSTING MODELS (LightGBM & XGBoost)")
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
        
        X, y, dates, feature_cols = prepare_data(features_df, labels_df, horizon)
        
        # Train LightGBM
        lgb_results = train_lightgbm(X, y, dates)
        
        # Train XGBoost
        xgb_results = train_xgboost(X, y, dates)
        
        all_results[f'{horizon}d'] = {
            'LightGBM': lgb_results,
            'XGBoost': xgb_results
        }
    
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
    output_file = RESULTS_DIR / "tables" / "boosting_results.csv"
    results_df.to_csv(output_file, index=False)
    
    print("\n" + "="*60)
    print("BOOSTING MODELS COMPLETE")
    print("="*60)
    print(f"\nResults saved to: {output_file}")
    print("\nSummary:")
    print(results_df.to_string(index=False))
    
    # Compare with baselines
    baseline_file = RESULTS_DIR / "tables" / "baseline_results.csv"
    if baseline_file.exists():
        baseline_df = pd.read_csv(baseline_file)
        
        print("\n" + "="*60)
        print("COMPARISON: Boosting vs Baselines")
        print("="*60)
        
        all_models = pd.concat([baseline_df, results_df])
        pivot = all_models.pivot_table(
            index='Horizon',
            columns='Model',
            values='Avg_F1_Macro'
        )
        print("\nF1-Macro Scores by Model:")
        print(pivot.to_string())

if __name__ == "__main__":
    main()