# src/scraper.py
import requests
import os

def get_alpha_vantage_news(symbol):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={api_key}'
    try:
        r = requests.get(url)
        return r.json().get("feed", [])[:20] # เอา 5 ข่าวเน้นๆ
    except: return []

def get_finnhub_data(symbol):
    api_key = os.getenv("FINNHUB_API_KEY")
    # ดึง Recommendation Trends
    rec_url = f'https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={api_key}'
    # ดึง Current Price
    quote_url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}'
    
    try:
        rec = requests.get(rec_url).json()
        quote = requests.get(quote_url).json()
        return rec[0] if rec else {}, quote.get('c', 0)
    except: return {}, 0

def get_atr_value(symbol):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f'https://www.alphavantage.co/query?function=ATR&symbol={symbol}&interval=daily&time_period=14&apikey={api_key}'
    try:
        r = requests.get(url).json()
        latest_date = list(r["Technical Analysis: ATR"].keys())[0]
        return r["Technical Analysis: ATR"][latest_date]["ATR"]
    except: return "N/A"

def get_company_factsheet(symbol):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    # ดึงค่าทางสถิติสำคัญ: P/E, PEG, Dividend, Next Earnings Date
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
    try:
        data = requests.get(url).json()
        return {
            "PERatio": data.get("PERatio"),
            "PEGRatio": data.get("PEGRatio"),
            "BookValue": data.get("BookValue"),
            "DividendYield": data.get("DividendYield"),
            "NextEarnings": data.get("LatestQuarter") # หรือดึงจาก Earnings Calendar
        }
    except: return {}

def get_daily_momentum(symbol):
    api_key = os.getenv("FINNHUB_API_KEY")
    url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}'
    try:
        d = requests.get(url).json()
        # c=Current, d=Change, dp=Percent Change, h=High, l=Low
        return f"Change: {d['d']} ({d['dp']}%), Range: {d['l']} - {d['h']}"
    except: return "N/A"