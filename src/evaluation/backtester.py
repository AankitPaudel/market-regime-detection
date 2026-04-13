"""
Cost-aware backtesting with transaction costs and risk management
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import get_config, LABELS_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR, RESULTS_DIR
from src.utils.helpers import load_dataframe, save_dataframe

class Backtester:
    """Cost-aware backtester for trading signals"""
    
    def __init__(self, 
                 transaction_cost_bps=4,
                 slippage_bps=2,
                 stop_loss_pct=0.05,
                 max_positions=2):
        """
        Initialize backtester
        
        Args:
            transaction_cost_bps: Transaction cost in basis points (per side)
            slippage_bps: Slippage in basis points
            stop_loss_pct: Stop loss percentage (e.g., 0.05 = 5%)
            max_positions: Maximum concurrent positions
        """
        self.transaction_cost_bps = transaction_cost_bps
        self.slippage_bps = slippage_bps
        self.total_cost_bps = transaction_cost_bps + slippage_bps
        self.stop_loss_pct = stop_loss_pct
        self.max_positions = max_positions
    
    def backtest(self, prices_df, signals_df, horizon=1):
        """
        Run backtest
        
        Args:
            prices_df: DataFrame with Date, Ticker, Close
            signals_df: DataFrame with Date, Ticker, signal (-1/0/1)
            horizon: Holding period in days
        
        Returns:
            DataFrame with trade results
        """
        
        print(f"\nBacktesting {horizon}-day horizon...")
        
        # Merge prices and signals
        df = prices_df[['Date', 'Ticker', 'Close']].merge(
            signals_df[['Date', 'Ticker', 'signal']],
            on=['Date', 'Ticker'],
            how='inner'
        )
        
        df = df.sort_values(['Ticker', 'Date']).reset_index(drop=True)
        
        # Calculate forward returns
        for ticker in df['Ticker'].unique():
            mask = df['Ticker'] == ticker
            df.loc[mask, 'future_close'] = df.loc[mask, 'Close'].shift(-horizon)
        
        df['forward_return'] = (df['future_close'] - df['Close']) / df['Close']
        
        # Filter to tradable signals
        df_trades = df[df['signal'] != 0].copy()
        
        print(f"  Total signals: {len(df_trades)}")
        print(f"  BUY signals: {(df_trades['signal'] == 1).sum()}")
        print(f"  SELL signals: {(df_trades['signal'] == -1).sum()}")
        
        # Calculate trade returns
        df_trades['gross_return'] = df_trades['signal'] * df_trades['forward_return']
        
        # Apply costs (entry + exit)
        total_cost = 2 * (self.total_cost_bps / 10000)  # Both sides
        df_trades['net_return'] = df_trades['gross_return'] - total_cost
        
        # Apply stop loss
        df_trades['stopped_out'] = df_trades['gross_return'] < -self.stop_loss_pct
        df_trades.loc[df_trades['stopped_out'], 'net_return'] = -self.stop_loss_pct - total_cost
        
        # Drop trades without future prices
        df_trades = df_trades.dropna(subset=['forward_return'])
        
        if len(df_trades) == 0:
            print("  No valid trades!")
            return None
        
        # Calculate metrics
        metrics = self.calculate_metrics(df_trades, horizon)
        
        return df_trades, metrics
    
    def calculate_metrics(self, trades_df, horizon):
        """Calculate performance metrics"""
        
        # Basic stats
        total_trades = len(trades_df)
        winning_trades = (trades_df['net_return'] > 0).sum()
        losing_trades = (trades_df['net_return'] < 0).sum()
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Returns
        mean_return = trades_df['net_return'].mean()
        total_return = trades_df['net_return'].sum()
        
        # Sharpe ratio (annualized)
        returns_std = trades_df['net_return'].std()
        if returns_std > 0:
            sharpe = (mean_return / returns_std) * np.sqrt(252 / horizon)
        else:
            sharpe = 0
        
        # Sortino ratio (downside deviation)
        negative_returns = trades_df['net_return'][trades_df['net_return'] < 0]
        if len(negative_returns) > 0:
            downside_std = negative_returns.std()
            if downside_std > 0:
                sortino = (mean_return / downside_std) * np.sqrt(252 / horizon)
            else:
                sortino = 0
        else:
            sortino = 0
        
        # Maximum drawdown
        cumulative = (1 + trades_df['net_return']).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # CAGR (annualized)
        years = len(trades_df) * horizon / 252
        if years > 0:
            final_value = cumulative.iloc[-1]
            cagr = (final_value ** (1/years)) - 1
        else:
            cagr = 0
        
        # Profit factor
        gross_profit = trades_df[trades_df['net_return'] > 0]['net_return'].sum()
        gross_loss = abs(trades_df[trades_df['net_return'] < 0]['net_return'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        metrics = {
            'Horizon': f'{horizon}d',
            'Total_Trades': total_trades,
            'Win_Rate': win_rate,
            'Mean_Return': mean_return,
            'Total_Return': total_return,
            'Sharpe_Ratio': sharpe,
            'Sortino_Ratio': sortino,
            'Max_Drawdown': max_drawdown,
            'CAGR': cagr,
            'Profit_Factor': profit_factor,
            'Winning_Trades': winning_trades,
            'Losing_Trades': losing_trades
        }
        
        print(f"\n  Performance Metrics:")
        print(f"    Total Trades: {total_trades}")
        print(f"    Win Rate: {win_rate:.1%}")
        print(f"    Sharpe Ratio: {sharpe:.3f}")
        print(f"    Sortino Ratio: {sortino:.3f}")
        print(f"    Max Drawdown: {max_drawdown:.1%}")
        print(f"    CAGR: {cagr:.1%}")
        print(f"    Profit Factor: {profit_factor:.2f}")
        
        return metrics

def generate_simple_signals(features_df, labels_df, horizon=1):
    """
    Generate simple trading signals using RSI
    (In practice, use actual model predictions)
    """
    
    # Merge features and labels
    df = features_df[['Date', 'Ticker', 'rsi_14', 'Close']].copy()
    
    # Simple strategy: RSI signals
    df['signal'] = 0
    
    if 'rsi_14' in df.columns:
        df.loc[df['rsi_14'] < 30, 'signal'] = 1   # BUY oversold
        df.loc[df['rsi_14'] > 70, 'signal'] = -1  # SELL overbought
    
    return df[['Date', 'Ticker', 'signal', 'Close']]

def main():
    """Main execution"""
    print("="*60)
    print("BACKTESTING")
    print("="*60)
    
    config = get_config()
    
    # Load data
    print("\nLoading data...")
    prices_df = load_dataframe(RAW_DATA_DIR / "prices" / "all_tickers.parquet")
    features_df = load_dataframe(PROCESSED_DATA_DIR / "technical_features.parquet")
    labels_df = load_dataframe(LABELS_DIR / "all_labels.parquet")
    
    print(f"Prices: {len(prices_df)} rows")
    print(f"Features: {len(features_df)} rows")
    
    # Initialize backtester
    backtester = Backtester(
        transaction_cost_bps=config.transaction_cost_bps,
        slippage_bps=config.slippage_bps,
        stop_loss_pct=config.stop_loss_pct,
        max_positions=config.max_concurrent_positions
    )
    
    # Run backtests for each horizon
    all_metrics = []
    all_trades = []
    
    for horizon in config.horizons:
        print(f"\n{'#'*60}")
        print(f"HORIZON: {horizon} days")
        print('#'*60)
        
        # Generate signals (simplified - use RSI)
        signals_df = generate_simple_signals(features_df, labels_df, horizon)
        
        print(f"Generated {len(signals_df)} signals")
        
        # Run backtest
        trades_df, metrics = backtester.backtest(prices_df, signals_df, horizon)
        
        if trades_df is not None:
            trades_df['horizon'] = horizon
            all_trades.append(trades_df)
            all_metrics.append(metrics)
    
    # Save results
    if all_metrics:
        metrics_df = pd.DataFrame(all_metrics)
        output = RESULTS_DIR / "tables" / "backtest_results.csv"
        metrics_df.to_csv(output, index=False)
        
        print("\n" + "="*60)
        print("BACKTEST COMPLETE")
        print("="*60)
        print(f"\nResults saved to: {output}")
        print("\nSummary:")
        print(metrics_df.to_string(index=False))
        
        # Save all trades
        if all_trades:
            trades_combined = pd.concat(all_trades, ignore_index=True)
            trades_output = RESULTS_DIR / "tables" / "all_trades.csv"
            trades_combined.to_csv(trades_output, index=False)
            print(f"\nTrades saved to: {trades_output}")

if __name__ == "__main__":
    main()