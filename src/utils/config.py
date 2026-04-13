"""Configuration management"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LABELS_DIR = DATA_DIR / "labels"
RESULTS_DIR = PROJECT_ROOT / "results"
MODELS_DIR = RESULTS_DIR / "models"

for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, LABELS_DIR, RESULTS_DIR, MODELS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

DEFAULT_TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
DEFAULT_START_DATE = '2015-01-01'
DEFAULT_END_DATE = '2025-10-30'
DEFAULT_HORIZONS = [1, 3, 5]
TRADING_DAYS_PER_YEAR = 252
MARKET_TIMEZONE = 'America/New_York'
RANDOM_SEED = 42

def load_config(config_path: str = None) -> Dict[str, Any]:
    if config_path is None:
        config_path = PROJECT_ROOT / "config.yaml"
    
    if not os.path.exists(config_path):
        print(f"Warning: Config not found at {config_path}, using defaults")
        return {}
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

class Config:
    def __init__(self, config_dict: Dict[str, Any] = None):
        if config_dict is None:
            config_dict = {}
        
        for key, value in config_dict.items():
            setattr(self, key, value)
        
        self.tickers = getattr(self, 'tickers', DEFAULT_TICKERS)
        self.start_date = getattr(self, 'start_date', DEFAULT_START_DATE)
        self.end_date = getattr(self, 'end_date', DEFAULT_END_DATE)
        self.horizons = getattr(self, 'horizons', DEFAULT_HORIZONS)
        self.random_state = getattr(self, 'random_state', RANDOM_SEED)

def get_config() -> Config:
    try:
        config_dict = load_config()
        return Config(config_dict)
    except:
        return Config()