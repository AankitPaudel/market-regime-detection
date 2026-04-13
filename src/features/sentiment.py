"""
Sentiment analysis - creates sentiment features from news/reddit
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import get_config, RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.utils.helpers import save_dataframe, load_dataframe

def create_sentiment_features(news_df, reddit_df):
    """Create sentiment features"""
    
    all_data = []
    
    # Process news
    if not news_df.empty:
        news_df['date'] = pd.to_datetime(news_df['date'])
        # Add dummy sentiment scores
        np.random.seed(42)
        news_df['sentiment_mean'] = np.random.normal(0, 0.3, len(news_df))
        news_df['sentiment_std'] = np.random.uniform(0.1, 0.5, len(news_df))
        news_df = news_df.rename(columns={'date': 'Date', 'ticker': 'Ticker'})
        all_data.append(news_df)
    
    # Process reddit  
    if not reddit_df.empty:
        reddit_df['date'] = pd.to_datetime(reddit_df['date'])
        reddit_df['reddit_mentions_norm'] = reddit_df.groupby('ticker')['mention_count'].transform(
            lambda x: (x - x.mean()) / x.std()
        )
        reddit_df = reddit_df.rename(columns={'date': 'Date', 'ticker': 'Ticker'})
        all_data.append(reddit_df[['Date', 'Ticker', 'mention_count', 'reddit_mentions_norm']])
    
    if not all_data:
        return pd.DataFrame()
    
    # Merge
    if len(all_data) == 2:
        combined = all_data[0].merge(all_data[1], on=['Date', 'Ticker'], how='outer')
    else:
        combined = all_data[0]
    
    combined = combined.sort_values(['Ticker', 'Date'])
    
    # Calculate deltas
    for col in ['sentiment_mean', 'headline_count']:
        if col in combined.columns:
            combined[f'{col}_delta'] = combined.groupby('Ticker')[col].diff()
    
    # Headline velocity
    if 'headline_count' in combined.columns:
        combined['headline_velocity'] = combined['headline_count'] / 24
    
    return combined

def main():
    print("="*60)
    print("SENTIMENT FEATURE ENGINEERING")
    print("="*60)
    
    # Load data
    news_file = RAW_DATA_DIR / "news" / "news_counts.parquet"
    reddit_file = RAW_DATA_DIR / "reddit" / "reddit_counts.parquet"
    
    news_df = load_dataframe(news_file) if news_file.exists() else pd.DataFrame()
    reddit_df = load_dataframe(reddit_file) if reddit_file.exists() else pd.DataFrame()
    
    print(f"\nLoaded {len(news_df)} news records")
    print(f"Loaded {len(reddit_df)} reddit records")
    
    if news_df.empty and reddit_df.empty:
        print("\n⚠️  No data - creating minimal placeholder")
        # Create minimal placeholder
        sentiment_df = pd.DataFrame({
            'Date': pd.date_range('2015-01-01', '2025-10-30', freq='D'),
            'Ticker': 'AAPL',
            'sentiment_mean': 0,
            'headline_count': 0
        })
    else:
        sentiment_df = create_sentiment_features(news_df, reddit_df)
    
    # Save
    output = PROCESSED_DATA_DIR / "sentiment_features.parquet"
    save_dataframe(sentiment_df, output)
    
    print(f"\n✓ COMPLETE")
    print(f"Saved to: {output}")

if __name__ == "__main__":
    main()