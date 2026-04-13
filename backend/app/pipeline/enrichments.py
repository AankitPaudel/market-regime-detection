"""
Optional enrichment features for AI Market Regime Detection V2.
Author: Ankit Paudel | CS 4771 Machine Learning — University of Idaho

Each function checks for its required API key first.
Returns None if the key is missing — NEVER raises an error.
The base prediction works perfectly with zero API keys configured.

Keys are loaded from .env:
    NEWSAPI_KEY         -> enables news sentiment
    REDDIT_CLIENT_ID    -> enables Reddit mention tracking
    REDDIT_CLIENT_SECRET
    REDDIT_USER_AGENT
    ALPHA_VANTAGE_KEY   -> enables analyst data / earnings

All HTTP requests use a 3-second timeout.
All functions are wrapped in try/except — enrichment failures
are logged as warnings, not errors.
"""

import os
import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 3  # seconds

# ── Positive / negative word lists for lightweight sentiment ────────────────
_POS_WORDS = {
    'beat', 'beats', 'surge', 'surges', 'surged', 'gain', 'gains', 'gained',
    'rises', 'rose', 'rally', 'rallies', 'rallied', 'upgrade', 'upgraded',
    'strong', 'growth', 'record', 'profit', 'profits', 'bullish', 'buy',
    'outperform', 'revenue', 'above', 'positive', 'boost', 'boosted',
    'higher', 'high', 'optimistic', 'upbeat', 'success', 'win', 'winning',
}
_NEG_WORDS = {
    'miss', 'misses', 'missed', 'fall', 'falls', 'fell', 'drop', 'drops',
    'dropped', 'decline', 'declines', 'declined', 'loss', 'losses', 'weak',
    'downgrade', 'downgraded', 'bearish', 'sell', 'underperform', 'cut',
    'cuts', 'below', 'negative', 'concern', 'concerns', 'warning', 'risk',
    'lower', 'low', 'pessimistic', 'crash', 'trouble', 'lawsuit', 'fine',
}


def _simple_sentiment(text: str) -> float:
    """
    Lightweight word-count sentiment. No transformers dependency.
    Returns float in [-1, 1]: -1=very negative, 0=neutral, +1=very positive.
    """
    words = text.lower().split()
    pos = sum(1 for w in words if w.strip('.,!?()') in _POS_WORDS)
    neg = sum(1 for w in words if w.strip('.,!?()') in _NEG_WORDS)
    total = pos + neg
    if total == 0:
        return 0.0
    return round((pos - neg) / total, 3)


# ── 1. News Sentiment ───────────────────────────────────────────────────────

def get_news_sentiment(ticker: str) -> dict | None:
    """
    Requires: NEWSAPI_KEY in .env
    Fetches last 10 headlines for ticker using NewsAPI free tier.
    Scores sentiment using positive/negative word count (no heavy deps).

    Returns:
        { score: float (-1 to 1), headline_count: int, sample_headline: str }
    Returns None if NEWSAPI_KEY is not set or request fails.
    """
    api_key = os.getenv('NEWSAPI_KEY', '').strip()
    if not api_key:
        logger.debug('NEWSAPI_KEY not set — skipping news sentiment')
        return None

    try:
        # Map common ticker aliases to company names for better search results
        company_names = {
            'AAPL': 'Apple', 'GOOGL': 'Google', 'MSFT': 'Microsoft',
            'TSLA': 'Tesla', 'NVDA': 'NVIDIA',
        }
        query = company_names.get(ticker.upper(), ticker)
        from_date = (datetime.today() - timedelta(days=3)).strftime('%Y-%m-%d')

        resp = requests.get(
            'https://newsapi.org/v2/everything',
            params={
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 10,
                'from': from_date,
                'apiKey': api_key,
            },
            timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()

        articles = data.get('articles', [])
        if not articles:
            return {'score': 0.0, 'headline_count': 0, 'sample_headline': 'No recent headlines found'}

        headlines = [a.get('title', '') or '' for a in articles]
        scores = [_simple_sentiment(h) for h in headlines if h]
        avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0

        sample = headlines[0][:120] if headlines else ''

        return {
            'score': avg_score,
            'headline_count': len(headlines),
            'sample_headline': sample,
        }

    except Exception as e:
        logger.warning(f'News sentiment failed for {ticker}: {e}')
        return None


# ── 2. Reddit Mentions ──────────────────────────────────────────────────────

def get_reddit_mentions(ticker: str) -> dict | None:
    """
    Requires: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT in .env
    Searches r/wallstreetbets and r/investing for ticker mentions in last 24h.

    Returns:
        { mention_count: int, sentiment_score: float, top_post_title: str }
    Returns None if PRAW credentials not set or request fails.
    """
    client_id     = os.getenv('REDDIT_CLIENT_ID', '').strip()
    client_secret = os.getenv('REDDIT_CLIENT_SECRET', '').strip()
    user_agent    = os.getenv('REDDIT_USER_AGENT', 'MarketRegimeV2/1.0').strip()

    if not client_id or not client_secret:
        logger.debug('REDDIT_CLIENT_ID/SECRET not set — skipping Reddit mentions')
        return None

    try:
        import praw

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

        mention_count = 0
        sentiment_scores = []
        top_post_title = ''
        top_score = -1

        subreddits = ['wallstreetbets', 'investing']
        cutoff = datetime.utcnow().timestamp() - 86400  # 24h ago

        for sub_name in subreddits:
            try:
                subreddit = reddit.subreddit(sub_name)
                for post in subreddit.search(ticker, sort='new', time_filter='day', limit=25):
                    if post.created_utc < cutoff:
                        continue
                    title = post.title or ''
                    if ticker.upper() in title.upper():
                        mention_count += 1
                        sentiment_scores.append(_simple_sentiment(title))
                        if post.score > top_score:
                            top_score = post.score
                            top_post_title = title[:80]
            except Exception:
                continue

        avg_sentiment = round(sum(sentiment_scores) / len(sentiment_scores), 3) if sentiment_scores else 0.0

        return {
            'mention_count': mention_count,
            'sentiment_score': avg_sentiment,
            'top_post_title': top_post_title or f'No recent {ticker} posts found',
        }

    except ImportError:
        logger.warning('praw not installed — run: pip install praw')
        return None
    except Exception as e:
        logger.warning(f'Reddit mentions failed for {ticker}: {e}')
        return None


# ── 3. Alpha Vantage Analyst Data ───────────────────────────────────────────

def get_alpha_vantage_data(ticker: str) -> dict | None:
    """
    Requires: ALPHA_VANTAGE_KEY in .env (free key at alphavantage.co)
    Fetches company overview: analyst target price, rating, and next earnings.

    Returns:
        { next_earnings: str, analyst_target: float, analyst_rating: str }
    Returns None if ALPHA_VANTAGE_KEY is not set or request fails.
    """
    api_key = os.getenv('ALPHA_VANTAGE_KEY', '').strip()
    if not api_key:
        logger.debug('ALPHA_VANTAGE_KEY not set — skipping analyst data')
        return None

    try:
        resp = requests.get(
            'https://www.alphavantage.co/query',
            params={
                'function': 'OVERVIEW',
                'symbol': ticker.upper(),
                'apikey': api_key,
            },
            timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()

        if 'Note' in data:
            # API rate limit hit
            logger.warning(f'Alpha Vantage rate limit hit for {ticker}')
            return None

        analyst_target_raw = data.get('AnalystTargetPrice', '')
        try:
            analyst_target = float(analyst_target_raw) if analyst_target_raw else None
        except ValueError:
            analyst_target = None

        # Map numeric rating to string
        rating_raw = data.get('AnalystRatingBuy', '')
        hold_raw   = data.get('AnalystRatingHold', '')
        sell_raw   = data.get('AnalystRatingSell', '')
        try:
            buy_count  = int(rating_raw) if rating_raw else 0
            hold_count = int(hold_raw)   if hold_raw   else 0
            sell_count = int(sell_raw)   if sell_raw   else 0
            total = buy_count + hold_count + sell_count
            if total > 0:
                if buy_count / total >= 0.5:
                    analyst_rating = 'Buy'
                elif sell_count / total >= 0.5:
                    analyst_rating = 'Sell'
                else:
                    analyst_rating = 'Hold'
            else:
                analyst_rating = data.get('RecommendationKey', 'N/A').capitalize()
        except Exception:
            analyst_rating = 'N/A'

        next_earnings = data.get('NextEarningsDate', 'N/A')

        return {
            'next_earnings': next_earnings,
            'analyst_target': analyst_target,
            'analyst_rating': analyst_rating,
        }

    except Exception as e:
        logger.warning(f'Alpha Vantage data failed for {ticker}: {e}')
        return None
