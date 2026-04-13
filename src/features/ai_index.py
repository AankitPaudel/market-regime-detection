"""
AI-Intensity Index A(t) - Detects AI-dominated market regimes
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import get_config, PROCESSED_DATA_DIR, RAW_DATA_DIR
from src.utils.helpers import save_dataframe, load_dataframe

def calculate_ai_index(features_df, sentiment_df=None):
    """Calculate AI-Intensity Index A(t)"""
    
    print("\nCalculating AI-Intensity Index A(t)...")
    
    df = features_df.copy()
    
    # Required components
    required_cols = ['volume_zscore', 'gap_pct', 'range_pct']
    
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        print(f"Warning: Missing columns: {missing}")
        for col in missing:
            df[col] = 0
    
    # Merge sentiment if available
    if sentiment_df is not None and not sentiment_df.empty:
        print("Merging sentiment features...")
        
        # Ensure Date column exists
        if 'Date' not in sentiment_df.columns and 'date' in sentiment_df.columns:
            sentiment_df = sentiment_df.rename(columns={'date': 'Date'})
        if 'Ticker' not in sentiment_df.columns and 'ticker' in sentiment_df.columns:
            sentiment_df = sentiment_df.rename(columns={'ticker': 'Ticker'})
        
        # CRITICAL FIX: Remove timezone from both DataFrames
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        sentiment_df['Date'] = pd.to_datetime(sentiment_df['Date']).dt.tz_localize(None)
        
        # Select available columns
        merge_cols = ['Date', 'Ticker']
        optional_cols = ['headline_velocity', 'sentiment_mean_delta']
        for col in optional_cols:
            if col in sentiment_df.columns:
                merge_cols.append(col)
        
        if len(merge_cols) > 2:  # More than just Date and Ticker
            try:
                df = df.merge(
                    sentiment_df[merge_cols],
                    on=['Date', 'Ticker'],
                    how='left'
                )
                print(f"  ✓ Merged columns: {merge_cols}")
            except Exception as e:
                print(f"  Warning: Could not merge sentiment: {e}")
    
    # AI-Index components
    ai_components = []
    
    if 'volume_zscore' in df.columns:
        ai_components.append('volume_zscore')
    
    if 'gap_pct' in df.columns:
        df['gap_pct_abs'] = df['gap_pct'].abs()
        ai_components.append('gap_pct_abs')
    
    if 'range_pct' in df.columns:
        ai_components.append('range_pct')
    
    if 'headline_velocity' in df.columns:
        df['headline_velocity'] = df['headline_velocity'].fillna(0)
        ai_components.append('headline_velocity')
    
    if 'sentiment_mean_delta' in df.columns:
        df['sentiment_delta_abs'] = df['sentiment_mean_delta'].fillna(0).abs()
        ai_components.append('sentiment_delta_abs')
    
    # VIX delta
    market_file = RAW_DATA_DIR / "prices" / "market_context.parquet"
    if market_file.exists():
        try:
            market_df = load_dataframe(market_file)
            market_df.index = pd.to_datetime(market_df.index).tz_localize(None)  # Remove timezone
            market_df['vix_delta'] = market_df['volatility_index'].diff().abs()
            
            df = df.merge(
                market_df[['vix_delta']],
                left_on='Date',
                right_index=True,
                how='left'
            )
            
            if 'vix_delta' in df.columns:
                df['vix_delta'] = df['vix_delta'].fillna(0)
                ai_components.append('vix_delta')
        except Exception as e:
            print(f"  Warning: Could not load VIX data: {e}")
    
    print(f"AI-Index components: {ai_components}")
    
    if not ai_components:
        print("Error: No AI-Index components available!")
        return pd.DataFrame()
    
    # Calculate AI-Index per ticker
    all_indices = []
    
    for ticker in df['Ticker'].unique():
        ticker_df = df[df['Ticker'] == ticker].copy().sort_values('Date')
        
        # Extract components
        component_matrix = ticker_df[ai_components].values
        
        # Remove NaN
        valid_mask = ~np.isnan(component_matrix).any(axis=1)
        component_matrix_clean = component_matrix[valid_mask]
        
        if len(component_matrix_clean) < 252:
            print(f"  {ticker}: Using simple normalization")
            scaler = StandardScaler()
            standardized = scaler.fit_transform(component_matrix)
            ai_index = np.nanmean(standardized, axis=1)
        else:
            print(f"  {ticker}: Using PCA approach")
            scaler = StandardScaler()
            standardized = scaler.fit_transform(component_matrix_clean)
            
            pca = PCA(n_components=1)
            pca_scores = pca.fit_transform(standardized)
            
            ai_index_clean = pca_scores.flatten()
            ai_index = np.full(len(component_matrix), np.nan)
            ai_index[valid_mask] = ai_index_clean
        
        # Rolling rank normalization
        ai_index_ranked = pd.Series(ai_index).rolling(
            window=252, min_periods=50
        ).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1] if len(x) > 0 else np.nan
        )
        
        ticker_df['ai_index_raw'] = ai_index
        ticker_df['ai_index'] = ai_index_ranked
        
        all_indices.append(ticker_df[['Date', 'Ticker', 'ai_index_raw', 'ai_index']])
    
    ai_df = pd.concat(all_indices, ignore_index=True)
    
    print(f"\n✓ AI-Index calculated for {len(ai_df)} rows")
    print(f"  Mean: {ai_df['ai_index'].mean():.3f}")
    print(f"  Std: {ai_df['ai_index'].std():.3f}")
    
    return ai_df

def main():
    print("="*60)
    print("AI-INTENSITY INDEX CALCULATION")
    print("="*60)
    
    # Load features
    print("\nLoading technical features...")
    tech_file = PROCESSED_DATA_DIR / "technical_features.parquet"
    if not tech_file.exists():
        print("Error: Technical features not found!")
        return
    
    features_df = load_dataframe(tech_file)
    print(f"Loaded {len(features_df)} rows")
    
    # Load sentiment (optional)
    sentiment_file = PROCESSED_DATA_DIR / "sentiment_features.parquet"
    if sentiment_file.exists():
        try:
            sentiment_df = load_dataframe(sentiment_file)
            print(f"Loaded {len(sentiment_df)} sentiment rows")
        except Exception as e:
            print(f"Warning: Could not load sentiment: {e}")
            sentiment_df = None
    else:
        print("No sentiment features (using technical only)")
        sentiment_df = None
    
    # Calculate AI-Index
    ai_df = calculate_ai_index(features_df, sentiment_df)
    
    if ai_df.empty:
        print("\n✗ Failed to calculate AI-Index")
        return
    
    # Save
    output = PROCESSED_DATA_DIR / "ai_index.parquet"
    save_dataframe(ai_df, output)
    
    print("\n✓ COMPLETE")
    print(f"Saved to: {output}")

if __name__ == "__main__":
    main()