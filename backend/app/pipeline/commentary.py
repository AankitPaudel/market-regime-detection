import os
from openai import OpenAI


def generate_commentary(ticker, label, confidence, horizon, ai_regime, rsi, top_feature) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return ""
    client = OpenAI(api_key=api_key)
    regime_str = "high AI-intensity regime" if ai_regime == 1 else "low AI-intensity regime"
    prompt = f"""
You are a quantitative analyst. In exactly 2 sentences, explain this prediction to a non-expert.

Ticker: {ticker}
Prediction: {label} over the next {horizon} trading day(s)
Confidence: {confidence:.0%}
Market regime: {regime_str}
RSI: {rsi:.1f}
Top SHAP feature: {top_feature}

Be concise and professional. Mention the regime and top feature.
"""
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120
    )
    return res.choices[0].message.content.strip()
