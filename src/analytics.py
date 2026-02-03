import numpy as np
import pandas as pd
from arch import arch_model
import os
import requests

def get_historical_data(symbol):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
    
    response = requests.get(url)
    data = response.json()

    # เช็คว่าโดนบล็อก API Limit หรือไม่
    if "Note" in data:
        raise Exception("Alpha Vantage API Limit reached (5 calls/min). Please wait a minute.")
    
    if "Time Series (Daily)" not in data:
        raise Exception(f"Unexpected API response: {data.get('Error Message', 'Unknown Error')}")

    df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    # ใช้ราคา close (4. close) สำหรับ TIME_SERIES_DAILY
    return df['4. close']

def calculate_statistical_metrics(symbol):
    """คำนวณสถิติโดยมีการดักจับ Error ภายใน"""
    try:
        prices = get_historical_data(symbol)
        
        # คำนวณ Log Returns
        returns = 100 * np.log(prices / prices.shift(1)).dropna()
        
        if len(returns) < 30:
            raise Exception("Insufficient data points for GARCH model (need at least 30 days).")

        # GARCH (1,1) Model
        model = arch_model(returns, vol='Garch', p=1, q=1, dist='Normal')
        model_fit = model.fit(disp='off')
        
        forecast = model_fit.forecast(horizon=1)
        forecasted_vol = np.sqrt(forecast.variance.values[-1, :][0])
        
        current_return = returns.iloc[-1]
        z_score = (current_return - returns.mean()) / returns.std()
        var_95 = returns.mean() - (1.645 * forecasted_vol)
        
        return {
            "forecasted_vol": round(forecasted_vol, 4),
            "z_score": round(z_score, 4),
            "var_95": round(var_95, 4),
            "is_outlier": abs(z_score) > 2.0
        }
    except Exception as e:
        # ส่งค่า Default หากเกิด Error เพื่อให้บอททำงานต่อได้
        print(f"Statistics Error for {symbol}: {str(e)}")
        return {
            "forecasted_vol": 0, "z_score": 0, "var_95": 0, "is_outlier": False, "error": str(e)
        }