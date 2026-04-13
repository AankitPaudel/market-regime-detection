"""
AI Market Regime Detection V2 — Backtester
Author: Ankit Paudel | CS 4771 Machine Learning — University of Idaho

Loads each pre-trained model, fetches 3 years of yfinance data,
simulates a trading strategy, and reports performance vs buy-and-hold.

Strategy rules:
  - Start with $10,000
  - BUY signal  → invest full capital in the stock
  - SELL signal → exit position (hold cash)
  - HOLD signal → maintain current position (no change)
  - Transaction cost: 0.1% per trade (applied on each buy and sell)

Usage:
    conda run -n ml-env python run_backtest.py

Output:
    - Console table with return, Sharpe, win rate per ticker/horizon
    - results/backtest_equity_curve.png (equity curves for all tickers)
"""

import os
import sys
import warnings
import joblib
import numpy as np
import pandas as pd
import yfinance as yf
import ta

warnings.filterwarnings('ignore')

TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
HORIZONS = [1, 3, 5]
MODELS_DIR = 'backend/models'
RESULTS_DIR = 'results'
INITIAL_CAPITAL = 10_000.0
TRANSACTION_COST = 0.001  # 0.1% per trade
LABEL_MAP = {0: 'SELL', 1: 'HOLD', 2: 'BUY'}

os.makedirs(RESULTS_DIR, exist_ok=True)


# ── Feature engineering (mirrors train_local.py exactly) ───────────────────

def fetch_data(ticker: str, period: str = '3y') -> pd.DataFrame:
    df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [c.lower() for c in df.columns]
    return df.dropna()


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['return_1d'] = df['close'].pct_change(1)
    df['return_5d'] = df['close'].pct_change(5)
    df['volatility_10d'] = df['return_1d'].rolling(10).std()
    df['volatility_20d'] = df['return_1d'].rolling(20).std()
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()
    bb = ta.volatility.BollingerBands(df['close'], window=20)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['close']
    df['bb_pct'] = bb.bollinger_pband()
    df['volume_zscore'] = (
        (df['volume'] - df['volume'].rolling(20).mean()) /
        df['volume'].rolling(20).std()
    )
    df['gap'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)
    df['range'] = (df['high'] - df['low']) / df['close']
    ai_feats = ['volatility_10d', 'volume_zscore', 'bb_width', 'macd_diff']
    df['ai_index'] = df[ai_feats].rank(pct=True).mean(axis=1)
    df['ai_regime'] = (df['ai_index'] > df['ai_index'].rolling(20).mean()).astype(int)
    return df.dropna()


FEATURE_COLS = [
    'return_1d', 'return_5d', 'volatility_10d', 'volatility_20d',
    'rsi', 'macd', 'macd_signal', 'macd_diff',
    'bb_upper', 'bb_lower', 'bb_width', 'bb_pct',
    'volume_zscore', 'gap', 'range', 'ai_index', 'ai_regime'
]


# ── Backtester ──────────────────────────────────────────────────────────────

def run_backtest(model, df: pd.DataFrame, horizon: int) -> dict:
    """
    Walk-forward simulation on the most recent 20% of rows.
    Uses the pre-trained model to generate signals on each row,
    then simulates portfolio value day by day.
    """
    # Use last 20% for out-of-sample testing
    split = int(len(df) * 0.80)
    test_df = df.iloc[split:].copy()

    if len(test_df) < 20:
        return None

    capital = INITIAL_CAPITAL
    in_position = False
    entry_price = 0.0
    equity_curve = [capital]
    trades = []

    prices = test_df['close'].values
    features_matrix = test_df[FEATURE_COLS].values

    for i in range(len(test_df) - horizon):
        X = pd.DataFrame([test_df[FEATURE_COLS].iloc[i]])[FEATURE_COLS]
        proba = model.predict_proba(X)[0]
        pred = int(np.argmax(proba))
        signal = LABEL_MAP[pred]

        current_price = prices[i]
        next_price = prices[i + horizon]

        if signal == 'BUY' and not in_position:
            # Enter long position
            cost = capital * TRANSACTION_COST
            capital -= cost
            shares = capital / current_price
            entry_price = current_price
            in_position = True
            trades.append({'type': 'BUY', 'price': current_price, 'idx': i})

        elif signal == 'SELL' and in_position:
            # Exit position
            capital = shares * current_price
            cost = capital * TRANSACTION_COST
            capital -= cost
            in_position = False
            ret = (current_price - entry_price) / entry_price
            trades.append({'type': 'SELL', 'price': current_price, 'ret': ret, 'idx': i})

        # Mark-to-market portfolio value
        if in_position:
            mtm = shares * next_price
        else:
            mtm = capital
        equity_curve.append(mtm)

    # Close any open position at end
    if in_position:
        capital = shares * prices[-1] * (1 - TRANSACTION_COST)

    # ── Performance metrics ─────────────────────────────────────────────────
    equity = np.array(equity_curve)
    daily_returns = np.diff(equity) / equity[:-1]
    daily_returns = daily_returns[np.isfinite(daily_returns)]

    total_return = (capital - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100

    bh_return = (prices[-1] - prices[0]) / prices[0] * 100

    sharpe = (
        (np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252))
        if np.std(daily_returns) > 0 else 0.0
    )

    sell_trades = [t for t in trades if t['type'] == 'SELL']
    win_rate = (
        len([t for t in sell_trades if t.get('ret', 0) > 0]) / len(sell_trades) * 100
        if sell_trades else 0.0
    )

    return {
        'strategy_return': total_return,
        'bh_return': bh_return,
        'sharpe': sharpe,
        'win_rate': win_rate,
        'total_trades': len(sell_trades),
        'equity_curve': equity_curve,
    }


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("  AI Market Regime Detection V2 - Backtest")
    print("  Author: Ankit Paudel | CS 4771 - University of Idaho")
    print("  Strategy: $10k capital, 0.1% transaction cost, 20% OOS test set")
    print("=" * 72)

    results = []
    equity_data = {}

    for ticker in TICKERS:
        print(f"\nFetching {ticker}...")
        df_raw = fetch_data(ticker, period='3y')
        df = compute_features(df_raw)

        equity_data[ticker] = {}

        for horizon in HORIZONS:
            key = f"{ticker}_{horizon}d"
            model_path = os.path.join(MODELS_DIR, f"lgbm_{key}.pkl")
            if not os.path.exists(model_path):
                print(f"  ⚠️  Missing model: {model_path}")
                continue

            model = joblib.load(model_path)
            result = run_backtest(model, df, horizon)
            if result is None:
                continue

            equity_data[ticker][horizon] = result['equity_curve']
            results.append({
                'Ticker': ticker,
                'Horizon': f'{horizon}d',
                'Strategy Return': f"{result['strategy_return']:+.1f}%",
                'Buy & Hold':      f"{result['bh_return']:+.1f}%",
                'Sharpe Ratio':    f"{result['sharpe']:.2f}",
                'Win Rate':        f"{result['win_rate']:.0f}%",
                'Total Trades':    result['total_trades'],
            })
            print(f"  OK {key}: strategy={result['strategy_return']:+.1f}% | B&H={result['bh_return']:+.1f}% | Sharpe={result['sharpe']:.2f} | WinRate={result['win_rate']:.0f}%")

    # ── Print table ─────────────────────────────────────────────────────────
    if results:
        df_results = pd.DataFrame(results)
        print("\n" + "=" * 72)
        print(df_results.to_string(index=False))
        print("=" * 72)
        print("\nNOTE: Past performance does not indicate future results. Research only.\n")

    # ── Equity curve plot ────────────────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, len(TICKERS), figsize=(18, 4), sharey=False)
        fig.suptitle('AI Market Regime Detection V2 — Equity Curves (1d horizon, OOS test)\nAnkit Paudel · CS 4771 · University of Idaho', fontsize=11)

        colors = ['#3b82f6', '#22c55e', '#a855f7', '#f59e0b', '#ef4444']

        for ax, ticker, color in zip(axes, TICKERS, colors):
            if ticker in equity_data and 1 in equity_data[ticker]:
                curve = equity_data[ticker][1]
                ax.plot(curve, color=color, linewidth=1.5)
                ax.axhline(INITIAL_CAPITAL, color='#555', linestyle='--', linewidth=0.8, alpha=0.6)
                ax.set_title(ticker, fontweight='bold')
                ax.set_xlabel('Days (OOS)')
                ax.set_ylabel('Portfolio Value ($)')
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
                ax.grid(True, alpha=0.1)
                ax.set_facecolor('#08080f')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        fig.patch.set_facecolor('#05050f')
        for ax in axes:
            ax.tick_params(colors='#888')
            ax.xaxis.label.set_color('#888')
            ax.yaxis.label.set_color('#888')
            ax.title.set_color('#ccc')
            for spine in ax.spines.values():
                spine.set_edgecolor('#222')

        plt.tight_layout()
        out_path = os.path.join(RESULTS_DIR, 'backtest_equity_curve.png')
        plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='#05050f')
        plt.close()
        print(f"Saved equity curve to {out_path}")
    except ImportError:
        print("  (matplotlib not installed — skipping plot)")


if __name__ == '__main__':
    main()
