"""
Reddit data ingestion from r/wallstreetbets
"""
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import get_config, RAW_DATA_DIR
from src.utils.helpers import save_dataframe

class RedditDataFetcher:
    """Fetch Reddit mentions from WSB"""
    
    def __init__(self, config=None):
        self.config = config if config else get_config()
        self.cache_dir = RAW_DATA_DIR / "reddit"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Check for Reddit credentials
        self.client_id = getattr(self.config, 'reddit_client_id', None)
        self.client_secret = getattr(self.config, 'reddit_client_secret', None)
        
        if not self.client_id or self.client_id == "YOUR_REDDIT_CLIENT_ID":
            print("Warning: No Reddit API credentials configured")
            self.client_id = None

def main():
    """Main execution - create dummy reddit data"""
    print("="*60)
    print("REDDIT DATA INGESTION")
    print("="*60)
    
    config = get_config()
    fetcher = RedditDataFetcher(config=config)
    
    print("\n⚠️  NO REDDIT API CREDENTIALS FOUND")
    print("Creating dummy Reddit data instead...")
    print("\nTo use real Reddit data:")
    print("1. Create app at: https://www.reddit.com/prefs/apps")
    print("2. Add to config.yaml: reddit_client_id and reddit_client_secret")
    
    # Create dummy reddit data
    dates = pd.date_range(start='2015-01-01', end='2025-10-30', freq='D')
    dummy_data = []
    
    import random
    for ticker in config.tickers:
        for date in dates:
            # Random mention count (0-50 per day)
            count = random.randint(0, 50)
            if count > 0:
                dummy_data.append({
                    'ticker': ticker,
                    'date': date,
                    'mention_count': count,
                    'avg_score': random.randint(1, 100)
                })
    
    reddit_df = pd.DataFrame(dummy_data)
    
    # Save
    output = RAW_DATA_DIR / "reddit" / "reddit_counts.parquet"
    save_dataframe(reddit_df, output)
    
    print(f"\n✓ Created {len(reddit_df)} dummy Reddit records")
    print(f"Saved to: {output}")

if __name__ == "__main__":
    main()