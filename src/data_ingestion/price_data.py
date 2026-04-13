"""Price data from Yahoo Finance"""
import pandas as pd
import yfinance as yf
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import get_config, RAW_DATA_DIR, MARKET_TIMEZONE
from src.utils.helpers import save_dataframe

class PriceDataFetcher:
    def __init__(self, config=None):
        self.config = config if config else get_config()
        self.cache_dir = RAW_DATA_DIR / "prices"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_ticker_data(self, ticker: str, start_date: str = None, end_date: str = None, force_refresh: bool = False) -> pd.DataFrame:
        start_date = start_date or self.config.start_date
        end_date = end_date or self.config.end_date
        
        cache_file = self.cache_dir / f"{ticker}_{start_date}_{end_date}.parquet"
        
        if not force_refresh and cache_file.exists():
            print(f"Loading {ticker} from cache")
            return pd.read_parquet(cache_file)
        
        print(f"Fetching {ticker} from Yahoo Finance...")
        
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(start=start_date, end=end_date, auto_adjust=True, actions=False)
        
        if df.empty:
            raise ValueError(f"No data for {ticker}")
        
        df = df.reset_index()
        df['Date'] = pd.to_datetime(df['Date'])
        
        if df['Date'].dt.tz is None:
            df['Date'] = df['Date'].dt.tz_localize(MARKET_TIMEZONE)
        else:
            df['Date'] = df['Date'].dt.tz_convert(MARKET_TIMEZONE)
        
        df['Ticker'] = ticker
        df = df[['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df = df.sort_values('Date').reset_index(drop=True)
        
        save_dataframe(df, cache_file, format='parquet')
        print(f"✓ Fetched {len(df)} days for {ticker}")
        
        return df
    
    def fetch_all_tickers(self, tickers=None, **kwargs) -> pd.DataFrame:
        tickers = tickers or self.config.tickers
        all_data = []
        
        for ticker in tickers:
            try:
                df = self.fetch_ticker_data(ticker, **kwargs)
                all_data.append(df)
            except Exception as e:
                print(f"Error with {ticker}: {e}")
        
        combined = pd.concat(all_data, ignore_index=True)
        combined = combined.sort_values(['Date', 'Ticker']).reset_index(drop=True)
        
        print(f"\n✓ Fetched {len(tickers)} tickers, {len(combined)} rows")
        return combined

def main():
    print("="*60)
    print("PRICE DATA INGESTION")
    print("="*60)
    
    fetcher = PriceDataFetcher()
    prices_df = fetcher.fetch_all_tickers()
    
    output = RAW_DATA_DIR / "prices" / "all_tickers.parquet"
    save_dataframe(prices_df, output)
    
    print("\n✓ COMPLETE")
    print(f"Saved to: {output}")

if __name__ == "__main__":
    main()