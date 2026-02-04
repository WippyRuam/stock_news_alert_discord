# src/analytics.py
import yfinance as yf
import pandas as pd
import numpy as np
from arch import arch_model

def get_historical_data(symbol):
    # ดึงข้อมูลย้อนหลัง 6 เดือน
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="6mo")
    if df.empty:
        raise Exception(f"No data found for {symbol}")
    return df['Close']

def calculate_statistical_metrics(symbol):
    try:
        prices = get_historical_data(symbol)
        returns = 100 * np.log(prices / prices.shift(1)).dropna()
        
        model = arch_model(returns, vol='Garch', p=1, q=1, dist='Normal')
        model_fit = model.fit(disp='off')
        
        forecast = model_fit.forecast(horizon=1)
        forecasted_vol = np.sqrt(forecast.variance.values[-1, :][0])
        z_score = (returns.iloc[-1] - returns.mean()) / returns.std()
        var_95 = returns.mean() - (1.645 * forecasted_vol)
        
        return {
            "forecasted_vol": round(forecasted_vol, 4),
            "z_score": round(z_score, 4),
            "var_95": round(var_95, 4),
            "is_outlier": abs(z_score) > 2.0
        }
    except Exception as e:
        print(f"Stats Error: {e}")
        return {"forecasted_vol": 0, "z_score": 0, "var_95": 0, "is_outlier": False}