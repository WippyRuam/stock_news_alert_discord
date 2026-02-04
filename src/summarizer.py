import os
from openai import OpenAI

def generate_alpha_signal(ticker, news, recs, price, atr, factsheet, momentum, stats):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=60.0,  # เพิ่มเวลาเป็น 60 วินาที
        max_retries=5   # ให้ลองใหม่ 5 ครั้งถ้าต่อไม่ติด
    )
    
    # Pre-processing news for the model
    news_string = ""
    if news:
        for idx, item in enumerate(news):
            news_string += f"[{idx+1}] Title: {item.get('title')} | Sentiment: {item.get('overall_sentiment_label')} | Score: {item.get('overall_sentiment_score')}\n"
    else:
        news_string = "No news data available for the period."

    prompt = f"""
    System Role: Act as a Bayesian Inference Engine for Equities Research. Your task is to synthesize raw market data into a high-conviction "Alpha Signal." You must identify correlations and divergences between news sentiment and institutional analyst trends using the data provided below.

    ---
    INPUT DATA FOR {ticker}:
    1. News Sentiment (Alpha Vantage):
    {news_string}

    2. Recommendation Trends (Finnhub Analysts):
    {recs}

    3. Market Context:
    - Current Price: {price}
    - ATR (14-Day): {atr}
    - Daily Momentum: {momentum}

    4. Fundamental Factsheet:
    {factsheet}

    5. Statistical Risk Metrics (Econometric Model - GARCH):
    - GARCH Forecasted Volatility: {stats.get('forecasted_vol')}%
    - Return Z-Score: {stats.get('z_score')}
    - Value at Risk (VaR 95%): {stats.get('var_95')}%
    - Statistical Outlier: {stats.get('is_outlier')}
    ---

    ANALYSIS PROTOCOL:
    1. Weighted Sentiment ($S$): Extract the top 3 core themes from the news data. Weight them by institutional relevance. Calculate a Sentiment Score ($S$) from -1.0 (Bearish) to 1.0 (Bullish).
    2. Trend Discrepancy: Compare the Finnhub Analyst Consensus (e.g., Strong Buy/Buy counts) against the current News Sentiment ($S$). If Analysts are "Bullish" but $S$ is "Bearish," flag this as a "Divergence."
    3. Volatility & Anomaly Filter: Use the Z-Score and ATR to determine if current price action is a statistical outlier or market noise. Cross-reference this with the GARCH Forecasted Volatility to assess if risk is expanding.
    4. Valuation Guardrail: Assess if the news catalyst justifies the current P/E or PEG ratio. Determine if the stock is "Overextended" fundamentally.
    5. Final Signal Calculation: $(Sentiment Score \times 0.6) + (Recommendation Strength \times 0.4)$.
       *Note: Recommendation Strength is normalized from 0.0 (Strong Sell) to 1.0 (Strong Buy).*

    OUTPUT REQUIREMENTS:
    - Use Markdown for structure.
    - DO NOT USE ANY EMOJIS.
    - Use professional, academic, and objective language.
    - The Execution Plan section must be in THAI.

    OUTPUT FORMAT:
    ### Bayesian Alpha Signal Report: {ticker}
    **Final Signal Score**: [Numerical Value]

    **1. Weighted Sentiment Analysis**
    - Identify top 3 themes and calculate $S$.

    **2. Trend Discrepancy & Divergence Alert**
    - Compare Consensus vs. News Sentiment. Flag anomalies.

    **3. Statistical Risk Assessment (GARCH/VaR)**
    - Analyze Z-Score and VaR to evaluate tail risk.

    **4. Factsheet & Valuation Insight**
    - P/E and PEG analysis relative to the daily catalyst.

    **5. Execution Plan (ภาษาไทย)**
    - [สรุปกลยุทธ์เชิงลึก: การวาง Position Sizing ตามค่า VaR, การตั้งจุดรับหรือจุดถอยตาม ATR และความเชื่อมั่นจาก Alpha Signal]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a world-class Quantitative Equity Researcher. You provide precise, data-driven insights without fluff or emojis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error in Summarizer: {str(e)}"