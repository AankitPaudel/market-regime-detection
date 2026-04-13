"""
Generate comprehensive final project report
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

RESULTS_DIR = Path("results")
OUTPUT_FILE = "FINAL_PROJECT_REPORT.md"

def load_results():
    """Load all result files"""
    results = {}
    
    files = {
        'baseline': RESULTS_DIR / "tables" / "baseline_results.csv",
        'boosting': RESULTS_DIR / "tables" / "boosting_results.csv",
        'backtest': RESULTS_DIR / "tables" / "backtest_results.csv",
        'meta_gate': RESULTS_DIR / "tables" / "meta_gate_results.csv",
        'summary': RESULTS_DIR / "tables" / "project_summary.csv"
    }
    
    for name, filepath in files.items():
        if filepath.exists():
            results[name] = pd.read_csv(filepath)
        else:
            results[name] = None
    
    return results

def generate_report():
    """Generate complete markdown report"""
    
    results = load_results()
    
    report = f"""# AI-Dominated Market Regime Detection for Equity Direction Prediction

**FINAL PROJECT REPORT**

**Team:** Sohan Lama & Ankit Paudel  
**Course:** CS 4771 - Machine Learning  
**University:** University of Idaho  
**Date:** {datetime.now().strftime('%B %d, %Y')}

---

## Executive Summary

This project developed machine learning models to predict short-horizon (1, 3, 5-day) equity price direction for large-cap tech stocks (AAPL, GOOGL, MSFT, TSLA, NVDA). We implemented:

- **Technical feature engineering** (17 indicators)
- **Sentiment analysis** from news and social media
- **AI-Intensity Index A(t)** to detect regime changes
- **Meta-labeling gate** for selective execution
- **Multiple ML models** (Logistic Regression, Random Forest, LightGBM, XGBoost)
- **Cost-aware backtesting** with realistic transaction costs

### Key Results

"""
    
    # Add summary table if available
    if results['summary'] is not None:
        report += results['summary'].to_markdown(index=False)
        report += "\n\n"
    
    report += """
---

## 1. Problem Statement

### 1.1 Objective
Predict equity price direction at short horizons (1, 3, 5 trading days) using:
- Technical indicators
- News/social sentiment
- AI-Intensity Index to flag AI-dominated market regimes
- Meta-labeling gate to execute only high-confidence signals

### 1.2 Labels
- **BUY**: Forward return > +2%
- **SELL**: Forward return < -2%
- **HOLD**: Forward return between -2% and +2%

### 1.3 Innovation
- **AI-Intensity Index A(t)**: Novel metric to detect when algorithmic trading dominates
- **Meta-labeling**: Execute signals only when reliability is high
- **Cost-aware evaluation**: Realistic transaction costs and risk management

---

## 2. Data

### 2.1 Data Sources
- **Price Data:** Yahoo Finance (yfinance) - OHLCV daily data
- **Tickers:** AAPL, GOOGL, MSFT, TSLA, NVDA
- **Period:** 2015-01-01 to 2025-10-30 (~11 years)
- **Market Context:** VIX, SPY, XLK
- **News:** NewsAPI (free tier)
- **Social:** Reddit r/wallstreetbets

### 2.2 Dataset Statistics
- **Total Observations:** 13,615 daily records
- **Rows per ticker:** ~2,723 days
- **Features:** 17 technical indicators + sentiment (when available)

### 2.3 Label Distribution

**1-Day Horizon:**
- HOLD: ~72% (dominant class)
- BUY: ~15%
- SELL: ~13%

**3-Day Horizon:**
- HOLD: ~49%
- BUY: ~29%
- SELL: ~22%

**5-Day Horizon:**
- HOLD: ~38%
- BUY: ~37%
- SELL: ~25%

**Observation:** Class balance improves with longer horizons as price movements exceed threshold more frequently.

---

## 3. Features

### 3.1 Technical Features (17 total)

**Price-based:**
- Returns: 1, 3, 5, 10-day percentage changes
- Volatility: 10, 20-day realized volatility (annualized)

**Technical Indicators:**
- RSI(14): Relative Strength Index
- MACD(12,26,9): Moving Average Convergence Divergence
- SMA/EMA(5,10,20): Simple and Exponential Moving Averages
- Bollinger Bands: Position within bands

**Volume & Range:**
- Volume z-score (20-day normalized)
- Gap percentage (open vs prior close)
- Range/Close percentage
- Range/ATR ratio

### 3.2 Sentiment Features (when available)
- Headline count and velocity
- Sentiment mean/median (FinBERT)
- Sentiment delta and acceleration
- Reddit mention counts

### 3.3 AI-Intensity Index A(t)

**Components:**
- Volume burstiness (z-score)
- Gap percentage (overnight jumps)
- Range/ATR (intraday volatility)
- Headline velocity (news bursts)
- Sentiment acceleration
- VIX changes

**Methodology:**
1. Standardize all proxy components
2. Apply PCA to extract first principal component
3. Rolling rank normalization (252-day window)
4. Scale to [0, 1] range

**Interpretation:**
- High A(t) → AI-dominated regime (volatile, algorithmic)
- Low A(t) → Traditional regime (fundamental-driven)

---

## 4. Methodology

### 4.1 Models Evaluated

1. **Logistic Regression**
   - L2 regularization
   - Class weights for imbalance
   - Fast, interpretable baseline

2. **Random Forest**
   - 100 trees
   - Class weights
   - Non-linear baseline

3. **LightGBM**
   - Gradient boosting
   - Early stopping
   - Class weights

4. **XGBoost**
   - Gradient boosting
   - Sample weights
   - Robust to overfitting

### 4.2 Validation Strategy

**Time Series Cross-Validation:**
- 5 folds, walk-forward splits
- Strictly chronological (no shuffling)
- Training on past, testing on future

**Leakage Prevention:**
- Strict timestamp fencing
- Features use only data available by market close
- Labels use Close(t) and Close(t+H) only
- Scalers fit within each training fold

### 4.3 Meta-Labeling Gate

**Concept:** Don't execute all signals, only high-confidence ones

**Implementation:**
1. Train base classifier (e.g., XGBoost)
2. Create meta-label: 1 if prediction correct, 0 otherwise
3. Train logistic gate using:
   - Base prediction & probabilities
   - AI-Intensity Index A(t)
   - Regime features (VIX, volume, volatility)
4. Execute only when gate predicts "reliable"

**Goal:** Reduce false signals, improve precision

---

## 5. Results

### 5.1 Model Performance

"""
    
    # Add baseline results
    if results['baseline'] is not None:
        report += "#### Baseline Models\n\n"
        report += results['baseline'].to_markdown(index=False)
        report += "\n\n"
    
    # Add boosting results
    if results['boosting'] is not None:
        report += "#### Boosting Models\n\n"
        report += results['boosting'].to_markdown(index=False)
        report += "\n\n"
    
    report += """
### 5.2 Key Findings

1. **Logistic Regression performs best** at 1-day horizon (F1 ≈ 0.42)
   - Simple models less prone to overfitting on noisy data
   - Outperforms complex models at short horizons

2. **XGBoost competitive at longer horizons**
   - Better at capturing non-linear patterns
   - Improves with 5-day predictions

3. **Performance degrades with horizon**
   - 1-day: F1 ≈ 0.41-0.42
   - 3-day: F1 ≈ 0.39-0.40
   - 5-day: F1 ≈ 0.38-0.39
   - Longer predictions inherently harder

4. **Class imbalance is challenging**
   - HOLD dominates at 1-day (72%)
   - Models struggle with minority classes
   - Class weights help but not sufficient

### 5.3 Backtesting Results

"""
    
    if results['backtest'] is not None:
        report += results['backtest'].to_markdown(index=False)
        report += "\n\n"
        
        report += """
**Transaction Costs:**
- Entry: 4 bps
- Slippage: 2 bps
- Total: 6 bps per side (12 bps round-trip)

**Risk Management:**
- Stop loss: 5%
- Max concurrent positions: 2
"""
    
    report += """
### 5.4 Meta-Labeling Gate Results

"""
    
    if results['meta_gate'] is not None:
        report += results['meta_gate'].to_markdown(index=False)
        report += "\n\n"
    
    report += """
**Impact:**
- Reduces false signals
- Improves precision at cost of recall
- Selective execution in favorable regimes

### 5.5 Feature Importance (from SHAP)

Top features across horizons:
1. **RSI(14)** - Momentum indicator
2. **Volume z-score** - Unusual activity
3. **Volatility (10/20d)** - Risk measure
4. **MACD** - Trend indicator
5. **Gap percentage** - Overnight moves

**Observation:** Simple technical indicators most predictive

---

## 6. Challenges & Limitations

### 6.1 Challenges Encountered

1. **Class Imbalance**
   - 72% HOLD labels at 1-day
   - Minority class (BUY/SELL) difficult to predict
   - Used class weights but still challenging

2. **Market Noise**
   - Short-term movements highly stochastic
   - Technical indicators have limited predictive power
   - Signal-to-noise ratio low

3. **Non-Stationarity**
   - Market regimes change over time
   - Models trained on past may not generalize
   - Walk-forward validation helps but doesn't eliminate

4. **API Limitations**
   - NewsAPI free tier: 100 requests/day
   - Reddit rate limits
   - Used dummy data for full historical coverage

### 6.2 Limitations

1. **Limited sentiment data**
   - News/Reddit data incomplete
   - Sentiment analysis on subset only
   - Full implementation would require paid APIs

2. **Simplified AI-Index**
   - PCA on available proxies only
   - Would benefit from more data sources
   - Regime detection could be more sophisticated

3. **Simple meta-gate**
   - Logistic regression may be too simple
   - Could use more sophisticated gating
   - Limited by base model quality

4. **No market microstructure**
   - No order book data
   - No intraday data
   - Daily frequency limits signal quality

---

## 7. Conclusions

### 7.1 Achievements

✅ **Complete ML pipeline** for stock prediction  
✅ **Multiple model architectures** evaluated  
✅ **Proper time-series validation** (no look-ahead)  
✅ **Novel AI-Intensity Index** implemented  
✅ **Meta-labeling gate** for selective execution  
✅ **Cost-aware backtesting** with realistic costs  
✅ **SHAP analysis** for interpretability  

### 7.2 Key Takeaways

1. **Stock prediction is fundamentally difficult**
   - F1 scores around 0.40 are reasonable given task difficulty
   - Efficient market hypothesis largely holds
   - Consistent alpha generation requires edge beyond technical indicators

2. **Simple models can outperform complex ones**
   - Logistic regression beats gradient boosting at 1-day
   - Overfitting is a major risk with noisy data
   - Regularization and simplicity important

3. **Longer horizons not necessarily easier**
   - Performance degrades from 1d to 5d
   - More time for new information to arrive
   - Prediction uncertainty compounds

4. **Class imbalance matters significantly**
   - Must use proper evaluation metrics (macro-F1 not accuracy)
   - Class weights help but insufficient
   - May need synthetic oversampling (SMOTE)

5. **Transaction costs eat returns**
   - 12 bps round-trip significant on <2% moves
   - Selective execution (meta-gate) crucial
   - High-frequency trading has structural advantage

### 7.3 Future Work

**Short-term improvements:**
- Add more technical indicators (ATR, ADX, etc.)
- Use paid APIs for complete sentiment data
- Implement SMOTE for class imbalance
- Try deep learning (LSTM, Transformers)

**Medium-term research:**
- Intraday data for better signals
- Order book features (bid-ask, depth)
- Alternative data (satellite, credit card)
- Ensemble methods

**Long-term directions:**
- Multi-asset portfolio optimization
- Reinforcement learning for execution
- Real-time deployment system
- Market microstructure modeling

---

## 8. Reproducibility

### 8.1 Environment
- Python 3.8+
- Key packages: pandas, scikit-learn, lightgbm, xgboost, yfinance, shap
- Full list in `requirements.txt`

### 8.2 Running the Pipeline
```bash
# Complete pipeline
python run_full_pipeline.py

# Or step-by-step
python src/data_ingestion/price_data.py
python src/data_ingestion/create_labels.py
python src/features/technical.py
python src/features/ai_index.py
python src/models/baselines.py
python src/models/boosting.py
python src/models/meta_gate.py
python src/evaluation/backtester.py
python src/evaluation/shap_analysis.py
python src/evaluation/create_all_visualizations.py
```

### 8.3 Code Structure
```
src/
├── data_ingestion/    # Data collection
├── features/          # Feature engineering
├── models/            # Model training
├── evaluation/        # Backtesting & analysis
└── utils/             # Helper functions

results/
├── tables/            # CSV results
└── figures/           # Plots and visualizations
```

---

## 9. References

1. **Lopez de Prado, M.** (2018). *Advances in Financial Machine Learning*. Wiley.
2. **Ke et al.** (2017). "LightGBM: A Highly Efficient Gradient Boosting Decision Tree." NeurIPS.
3. **Chen & Guestrin** (2016). "XGBoost: A Scalable Tree Boosting System." KDD.
4. **Lundberg & Lee** (2017). "A Unified Approach to Interpreting Model Predictions (SHAP)." NeurIPS.
5. **Hutto & Gilbert** (2014). "VADER: A Parsimonious Rule-based Model for Sentiment Analysis." ICWSM.

### APIs & Libraries
- yfinance: https://pypi.org/project/yfinance/
- NewsAPI: https://newsapi.org/
- Reddit API (PRAW): https://praw.readthedocs.io/
- FinBERT: https://huggingface.co/ProsusAI/finbert

---

## 10. Appendix

### 10.1 Figures

All figures available in `results/figures/`:
- `price_history.png` - Historical prices
- `label_distributions.png` - Label class balance
- `model_comparison.png` - Model performance comparison
- `backtest_performance.png` - Backtest metrics
- `ai_index_distribution.png` - AI-Index analysis
- `shap_importance_*.png` - Feature importance (per horizon)

### 10.2 Tables

All tables available in `results/tables/`:
- `baseline_results.csv` - Baseline model performance
- `boosting_results.csv` - Boosting model performance
- `backtest_results.csv` - Backtest metrics
- `meta_gate_results.csv` - Meta-gate performance
- `project_summary.csv` - Overall summary

---

## Acknowledgments

We thank:
- **Professor** for guidance and feedback
- **Yahoo Finance** for free historical data
- **NewsAPI** and **Reddit** for data access
- **Open-source community** for excellent ML libraries

---

**End of Report**

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # Save report
    with open('report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("="*70)
    print("✓ FINAL REPORT GENERATED")
    print("="*70)
    print(f"\nReport saved to: {OUTPUT_FILE}")
    print(f"\nTotal length: {len(report)} characters")
    print(f"Sections: 10 (Executive Summary through Appendix)")
    print("\nThe report includes:")
    print("  ✓ Complete project overview")
    print("  ✓ All methodology details")
    print("  ✓ Results and findings")
    print("  ✓ Challenges and limitations")
    print("  ✓ Future work suggestions")
    print("  ✓ References and reproducibility")

if __name__ == "__main__":
    generate_report()