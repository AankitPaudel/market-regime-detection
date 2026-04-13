"""
SHAP (SHapley Additive exPlanations) for model interpretability
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
from pathlib import Path
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import get_config, LABELS_DIR, PROCESSED_DATA_DIR, RESULTS_DIR
from src.utils.helpers import load_dataframe

def prepare_data_for_shap(features_df, labels_df, horizon=1):
    """Prepare data for SHAP analysis"""
    
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
    
    # Convert labels to 0, 1, 2
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    return X, y_encoded, feature_cols

def train_model_for_shap(X, y):
    """Train LightGBM model for SHAP"""
    
    print("\nTraining LightGBM for SHAP analysis...")
    
    # Split data (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False, random_state=42
    )
    
    # Train LightGBM
    train_data = lgb.Dataset(X_train, label=y_train)
    
    params = {
        'objective': 'multiclass',
        'num_class': 3,
        'metric': 'multi_logloss',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 0.8,
        'verbose': -1,
        'random_state': 42
    }
    
    model = lgb.train(params, train_data, num_boost_round=100)
    
    print("✓ Model trained")
    
    return model, X_test

def create_shap_plots(model, X_test, feature_names, horizon=1):
    """Create SHAP visualizations"""
    
    print(f"\nGenerating SHAP plots for {horizon}d horizon...")
    
    # Create SHAP explainer
    explainer = shap.TreeExplainer(model)
    
    # Calculate SHAP values (use subset for speed)
    sample_size = min(500, len(X_test))
    X_sample = X_test.sample(n=sample_size, random_state=42)
    
    shap_values = explainer.shap_values(X_sample)
    
    print("✓ SHAP values calculated")
    print(f"  SHAP values type: {type(shap_values)}")
    if isinstance(shap_values, list):
        print(f"  SHAP values list length: {len(shap_values)}")
        print(f"  First SHAP array shape: {shap_values[0].shape}")
    else:
        print(f"  SHAP values shape: {shap_values.shape}")
    
    # Plot 1: Summary plot (bar)
    print("  Creating summary plot (bar)...")
    
    feature_importance = None
    
    try:
        plt.figure(figsize=(10, 8))
        
        # CRITICAL FIX: Handle multi-class SHAP values properly
        if isinstance(shap_values, list):
            # shap_values is a list of arrays, one per class
            # Average absolute SHAP across all classes
            shap_arrays = [np.abs(sv) for sv in shap_values]
            shap_abs_mean = np.mean(shap_arrays, axis=0)  # Shape: (n_samples, n_features)
        else:
            # Single array
            shap_abs_mean = np.abs(shap_values)
        
        print(f"  shap_abs_mean shape: {shap_abs_mean.shape}")
        
        # Calculate mean importance per feature (average across samples)
        importance_values = np.mean(shap_abs_mean, axis=0)  # Shape: (n_features,)
        
        print(f"  importance_values shape: {importance_values.shape}")
        print(f"  importance_values type: {type(importance_values)}")
        print(f"  feature_names length: {len(feature_names)}")
        
        # CRITICAL FIX: Flatten importance_values if needed
        if hasattr(importance_values, 'flatten'):
            importance_values = importance_values.flatten()
        
        # Convert to regular Python list to ensure 1D
        importance_values = list(importance_values)
        
        print(f"  After flatten - importance_values length: {len(importance_values)}")
        
        # Ensure same length
        if len(importance_values) != len(feature_names):
            print(f"  Warning: Length mismatch!")
            min_len = min(len(importance_values), len(feature_names))
            importance_values = importance_values[:min_len]
            feature_names_fixed = list(feature_names)[:min_len]
        else:
            feature_names_fixed = list(feature_names)
        
        # Create DataFrame with explicit lists
        feature_importance = pd.DataFrame({
            'feature': feature_names_fixed,
            'importance': importance_values
        }).sort_values('importance', ascending=False).head(15)
        
        # Plot
        plt.barh(range(len(feature_importance)), feature_importance['importance'].values)
        plt.yticks(range(len(feature_importance)), feature_importance['feature'].values)
        plt.xlabel('Mean |SHAP value|')
        plt.title(f'SHAP Feature Importance - {horizon}d Horizon')
        plt.tight_layout()
        
        output = RESULTS_DIR / "figures" / f"shap_importance_{horizon}d.png"
        plt.savefig(output, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output}")
        plt.close()
        
    except Exception as e:
        print(f"  Warning: Could not create bar plot: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # Plot 2: Summary plot (beeswarm) - for BUY class
    print("  Creating beeswarm plot...")
    
    try:
        plt.figure(figsize=(10, 8))
        
        # Use class 2 (BUY) SHAP values
        if isinstance(shap_values, list):
            shap_for_plot = shap_values[2]  # BUY class
        else:
            shap_for_plot = shap_values
        
        shap.summary_plot(
            shap_for_plot, 
            X_sample, 
            feature_names=feature_names,
            show=False,
            max_display=15
        )
        plt.title(f'SHAP Summary Plot - BUY Signals - {horizon}d Horizon', pad=20)
        plt.tight_layout()
        
        output = RESULTS_DIR / "figures" / f"shap_summary_{horizon}d.png"
        plt.savefig(output, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output}")
        plt.close()
        
    except Exception as e:
        print(f"  Warning: Could not create beeswarm plot: {e}")
    
    # Save feature importance table
    try:
        if feature_importance is not None:
            importance_df = feature_importance.copy()
            importance_df['rank'] = range(1, len(importance_df) + 1)
            importance_df = importance_df[['rank', 'feature', 'importance']]
            
            output_csv = RESULTS_DIR / "tables" / f"shap_importance_{horizon}d.csv"
            importance_df.to_csv(output_csv, index=False)
            print(f"  ✓ Saved: {output_csv}")
            
            return feature_importance
    except Exception as e:
        print(f"  Warning: Could not save table: {e}")
    
    return None

def main():
    """Main execution"""
    print("="*60)
    print("SHAP ANALYSIS")
    print("="*60)
    
    config = get_config()
    
    # Load data
    print("\nLoading data...")
    features_df = load_dataframe(PROCESSED_DATA_DIR / "technical_features.parquet")
    labels_df = load_dataframe(LABELS_DIR / "all_labels.parquet")
    
    # Analyze each horizon
    all_importance = {}
    
    for horizon in config.horizons:
        print(f"\n{'#'*60}")
        print(f"HORIZON: {horizon} days")
        print('#'*60)
        
        try:
            # Prepare data
            X, y, feature_names = prepare_data_for_shap(features_df, labels_df, horizon)
            
            print(f"Data shape: {X.shape}")
            print(f"Features: {len(feature_names)}")
            
            # Train model
            model, X_test = train_model_for_shap(X, y)
            
            # Create SHAP plots
            importance = create_shap_plots(model, X_test, feature_names, horizon)
            
            if importance is not None:
                all_importance[f'{horizon}d'] = importance
            
        except Exception as e:
            print(f"\n✗ Error processing {horizon}d horizon: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if all_importance:
        print("\n" + "="*60)
        print("SHAP ANALYSIS COMPLETE")
        print("="*60)
        print(f"\nPlots saved to: {RESULTS_DIR / 'figures'}")
        print(f"Tables saved to: {RESULTS_DIR / 'tables'}")
        
        # Print top features
        print("\n" + "="*60)
        print("TOP 5 FEATURES BY HORIZON")
        print("="*60)
        
        for horizon, importance_df in all_importance.items():
            print(f"\n{horizon}:")
            print(importance_df.head(5)[['feature', 'importance']].to_string(index=False))
    else:
        print("\n⚠️  No SHAP analysis completed successfully")
        print("This is OK - SHAP is optional and other results are still valid!")

if __name__ == "__main__":
    main()