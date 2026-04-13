"""Create BUY/SELL/HOLD labels"""
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import get_config, RAW_DATA_DIR, LABELS_DIR
from src.utils.helpers import create_forward_returns, create_labels, save_dataframe, load_dataframe, print_class_distribution

def create_all_labels(prices_df, horizons, buy_threshold=0.02, sell_threshold=-0.02):
    all_labels = []
    
    for ticker in prices_df['Ticker'].unique():
        print(f"\nProcessing {ticker}...")
        
        ticker_df = prices_df[prices_df['Ticker'] == ticker].copy()
        ticker_df = ticker_df.sort_values('Date').set_index('Date')
        
        returns_df = create_forward_returns(ticker_df, horizons=horizons, price_col='Close')
        
        for h in horizons:
            return_col = f'return_{h}d'
            label_col = f'label_{h}d'
            
            labels = create_labels(returns_df[return_col], buy_threshold, sell_threshold)
            returns_df[label_col] = labels
            
            valid = labels.dropna()
            print(f"  {h}d: {len(valid)} labels")
            print_class_distribution(valid, f"{ticker} - {h}d")
        
        returns_df['Ticker'] = ticker
        returns_df = returns_df.reset_index()
        all_labels.append(returns_df)
    
    combined = pd.concat(all_labels, ignore_index=True)
    return combined.sort_values(['Date', 'Ticker'])

def main():
    print("="*60)
    print("LABEL CREATION")
    print("="*60)
    
    config = get_config()
    
    prices_file = RAW_DATA_DIR / "prices" / "all_tickers.parquet"
    if not prices_file.exists():
        raise FileNotFoundError("Run price_data.py first!")
    
    prices_df = load_dataframe(prices_file)
    print(f"Loaded {len(prices_df)} rows")
    
    labels_df = create_all_labels(prices_df, config.horizons, config.buy_threshold, config.sell_threshold)
    
    output = LABELS_DIR / "all_labels.parquet"
    save_dataframe(labels_df, output)
    
    print("\n✓ COMPLETE")
    print(f"Saved to: {output}")

if __name__ == "__main__":
    main()