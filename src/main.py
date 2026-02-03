import os
import time
from dotenv import load_dotenv

from scraper import (
    get_alpha_vantage_news, 
    get_finnhub_data, 
    get_atr_value, 
    get_company_factsheet, 
    get_daily_momentum
)
from analytics import calculate_statistical_metrics
from summarizer import generate_alpha_signal
from notifier import send_to_discord

def main():
    # 1. Initialization
    load_dotenv()
    watchlist_str = os.getenv("WATCHLIST", "AAPL,TSLA,NVDA")
    watchlist = [ticker.strip().upper() for ticker in watchlist_str.split(",")]
    
    print(f"Starting Bayesian Alpha Engine for: {watchlist}")
    print("-" * 50)
    
    reports = []

    for symbol in watchlist:
        try:
            print(f"Processing {symbol}...")
            
            # 2. Data Sourcing
            news = get_alpha_vantage_news(symbol)
            time.sleep(1) 
            
            recs, current_price = get_finnhub_data(symbol)
            atr = get_atr_value(symbol)
            time.sleep(1)
            
            factsheet = get_company_factsheet(symbol)
            momentum = get_daily_momentum(symbol)
            
            # 3. Statistical Analysis
            print(f"Running Econometric Models (GARCH/VaR)...")
            stats = calculate_statistical_metrics(symbol)
            
            # 4. AI Synthesis
            print(f"Synthesizing Alpha Signal for {symbol}...")
            analysis_result = generate_alpha_signal(
                symbol, news, recs, current_price, atr, factsheet, momentum, stats
            )
            
            reports.append(analysis_result)
            print(f"Analysis for {symbol} Completed.")

            # 5. API Rate Limit Management
            if symbol != watchlist[-1]:
                print(f"Cooling down for 60s to maintain API integrity...")
                time.sleep(60)

        except Exception as e:
            error_msg = f"Error analyzing {symbol}: {str(e)}"
            print(error_msg)
            reports.append(error_msg)
            continue

    # 6. Final Delivery
    if reports:
        print("\nDispatching Quant Reports to Discord...")
        final_payload = "\n\n" + "="*30 + "\n"
        final_payload += "\n\n".join(reports)
        
        if len(final_payload) > 2000:
            for i in range(0, len(final_payload), 2000):
                send_to_discord(final_payload[i:i+2000])
        else:
            send_to_discord(final_payload)
            
        print("All Alpha Signals delivered. Trading session ready.")
    else:
        print("No reports generated. Check API keys and logs.")

if __name__ == "__main__":
    main()