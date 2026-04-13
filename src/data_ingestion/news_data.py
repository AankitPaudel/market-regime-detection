"""
News data ingestion from NewsAPI
"""
import pandas as pd
import requests
from datetime import datetime, timedelta
from pathlib import Path
import time
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import get_config, RAW_DATA_DIR
from src.utils.helpers import save_dataframe

class NewsDataFetcher:
    """Fetch news headlines from NewsAPI"""
    
    def __init__(self, api_key=None, config=None):
        self.config = config if config else get_config()
        self.api_key = api_key or getattr(self.config, 'newsapi_key', None)
        self.cache_dir = RAW_DATA_DIR / "news"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.api_key or self.api_key == "YOUR_NEWSAPI_KEY_HERE":
            print("Warning: No NewsAPI key configured")
            self.api_key = None
    
    def fetch_headlines(self, ticker, start_date, end_date):
        """Fetch headlines for a ticker"""
        if not self.api_key:
            print(f"Skipping {ticker} - no API key")
            return pd.DataFrame()
        
        # NewsAPI free tier: 100 requests/day, 1 month history
        base_url = "https://newsapi.org/v2/everything"
        
        headlines = []
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Map ticker to company name
        company_names = {
            'AAPL': 'Apple',
            'GOOGL': 'Google OR Alphabet',
            'MSFT': 'Microsoft',
            'TSLA': 'Tesla',
            'NVDA': 'Nvidia'
        }
        
        query = company_names.get(ticker, ticker)
        
        print(f"\nFetching news for {ticker} ({query})...")
        
        # Fetch in chunks (NewsAPI limit: 1 month per request)
        while current_date < end:
            chunk_end = min(current_date + timedelta(days=30), end)
            
            params = {
                'q': query,
                'from': current_date.strftime('%Y-%m-%d'),
                'to': chunk_end.strftime('%Y-%m-%d'),
                'language': 'en',
                'sortBy': 'publishedAt',
                'apiKey': self.api_key,
                'pageSize': 100
            }
            
            try:
                response = requests.get(base_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    for article in articles:
                        headlines.append({
                            'ticker': ticker,
                            'date': article['publishedAt'][:10],
                            'time': article['publishedAt'],
                            'title': article['title'],
                            'source': article['source']['name'],
                            'url': article['url']
                        })
                    
                    print(f"  {current_date.strftime('%Y-%m')} to {chunk_end.strftime('%Y-%m')}: {len(articles)} articles")
                    
                elif response.status_code == 429:
                    print("  Rate limit hit - stopping")
                    break
                else:
                    print(f"  Error: {response.status_code}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"  Error: {e}")
            
            current_date = chunk_end + timedelta(days=1)
        
        if headlines:
            df = pd.DataFrame(headlines)
            print(f"✓ Fetched {len(df)} headlines for {ticker}")
            return df
        else:
            print(f"✗ No headlines for {ticker}")
            return pd.DataFrame()
    
    def aggregate_daily_counts(self, headlines_df):
        """Aggregate headline counts by day"""
        if headlines_df.empty:
            return pd.DataFrame()
        
        daily = headlines_df.groupby(['ticker', 'date']).agg({
            'title': 'count',
            'source': 'nunique'
        }).reset_index()
        
        daily.columns = ['ticker', 'date', 'headline_count', 'source_count']
        daily['date'] = pd.to_datetime(daily['date'])
        
        return daily

def main():
    """Main execution - fetch news or create dummy data"""
    print("="*60)
    print("NEWS DATA INGESTION")
    print("="*60)
    
    config = get_config()
    fetcher = NewsDataFetcher(config=config)
    
    if not fetcher.api_key:
        print("\n⚠️  NO NEWSAPI KEY FOUND")
        print("Creating dummy news data instead...")
        print("\nTo use real news data:")
        print("1. Get free API key from: https://newsapi.org/")
        print("2. Add to config.yaml: newsapi_key: 'YOUR_KEY'")
        
        # Create dummy news data
        dates = pd.date_range(start='2015-01-01', end='2025-10-30', freq='D')
        dummy_data = []
        
        for ticker in config.tickers:
            for date in dates:
                # Random headline count (0-20 per day)
                import random
                count = random.randint(0, 20)
                if count > 0:
                    dummy_data.append({
                        'ticker': ticker,
                        'date': date,
                        'headline_count': count,
                        'source_count': random.randint(1, min(count, 10))
                    })
        
        news_df = pd.DataFrame(dummy_data)
        print(f"\n✓ Created {len(news_df)} dummy news records")
    
    else:
        # Fetch real news (limited by API)
        print("\n⚠️  NewsAPI free tier limits:")
        print("  - 100 requests/day")
        print("  - 1 month of history only")
        print("\nFetching sample (last 30 days only)...")
        
        end_date = '2025-10-30'
        start_date = '2025-10-01'
        
        all_headlines = []
        for ticker in config.tickers:
            df = fetcher.fetch_headlines(ticker, start_date, end_date)
            if not df.empty:
                all_headlines.append(df)
        
        if all_headlines:
            combined = pd.concat(all_headlines, ignore_index=True)
            news_df = fetcher.aggregate_daily_counts(combined)
        else:
            news_df = pd.DataFrame()
    
    # Save
    if not news_df.empty:
        output = RAW_DATA_DIR / "news" / "news_counts.parquet"
        save_dataframe(news_df, output)
        
        print(f"\n✓ COMPLETE")
        print(f"Saved to: {output}")
        print(f"Total records: {len(news_df)}")
    else:
        print("\n✗ No news data collected")

if __name__ == "__main__":
    main()