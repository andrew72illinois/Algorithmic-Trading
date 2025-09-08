import os
import pandas as pd
from dotenv import load_dotenv

from alpaca_data import (
    setup_historical_client, 
    retrieve_stock_bars,
    data_frame_from_stock_bars,
    retrieve_latest,
    filter_regular_hours,
    add_technical_indicators,
    classify_price_gap
)

from machine_learning import (
    train_and_save_knn_model,
    load_knn_model,
    predict_latest_candlestick
)
import numpy as np

from alpaca_paper_trading import (
    setup_client, 
    place_market_buy_order, 
    place_limit_buy_order, 
    place_market_sell_order,
    place_limit_sell_order,
    get_account_info,
    get_positions
)

import time
from alpaca.data.timeframe import TimeFrameUnit

load_dotenv("environment.env")

def main() -> None:
    # Get keys from environment
    alpaca_api_key = os.getenv("ALPACA_API_KEY")
    alpaca_secret = os.getenv("ALPACA_SECRET")
    alpaca_base_url = os.getenv("ALPACA_BASE_URL")
    
    # Setup clients
    alpaca_client = setup_client(key_=alpaca_api_key, secret_=alpaca_secret, paper_=True, base_url_=alpaca_base_url)
    alpaca_historical_client = setup_historical_client(key_=alpaca_api_key, secret_=alpaca_secret, base_url_=alpaca_base_url, raw_data_= True)
    # Load trained model
    model = load_knn_model(model_filename="knn_model1.pkl")
    # Run during stock market hours
    while True:
        start_time = time.time()
        
        stock_bars = retrieve_stock_bars(client_=alpaca_historical_client, symbol_= "TSLA", time_interval_=1, time_unit_=TimeFrameUnit.Minute, limit_= 1000)
        stock_data_frame = data_frame_from_stock_bars(data_ = stock_bars)
        filtered_data_frame = filter_regular_hours(data_= stock_data_frame)
        technical_data_frame = add_technical_indicators(data_=filtered_data_frame.copy())
        # classified_data_frame = classify_price_gap(data_=technical_data_frame)
        
        if model is not None:
             # Get prediction for the latest candlestick
            prediction = predict_latest_candlestick(model, technical_data_frame)
             
             # Get current price for limit orders
            print(technical_data_frame.iloc[-1])
            current_price = technical_data_frame['close'].iloc[-1]
             
            if prediction == 1:
                print("Prediction: Price will go HIGHER")
                 
                # Example: Place a market buy order for 1 share
                # Uncomment the line below to actually place the order
                order_result = place_market_buy_order(alpaca_client, "TSLA", 1)
                 
                # Example: Place a limit buy order slightly below current price
                # limit_price = current_price * 0.995  # 0.5% below current price
                # order_result = place_limit_buy_order(alpaca_client, "TSLA", 1, limit_price)
                 
                print(f"Would place BUY order at current price: ${current_price:.2f}")
                 
            elif prediction == -1:
                print("Prediction: Price will go LOWER")
                 
                # Check if we have any TSLA positions to sell
                positions = get_positions(alpaca_client)
                if 'TSLA' in positions and positions['TSLA']['qty'] > 0:
                    tsla_qty = int(positions['TSLA']['qty'])
                    print(f"Found {tsla_qty} shares of TSLA to sell")
                     
                    # Example: Place a market sell order for all TSLA shares
                    # Uncomment the line below to actually place the order
                    order_result = place_market_sell_order(alpaca_client, "TSLA", tsla_qty)
                     
                    # Example: Place a limit sell order slightly above current price
                    # limit_price = current_price * 1.005  # 0.5% above current price
                    # order_result = place_limit_sell_order(alpaca_client, "TSLA", tsla_qty, limit_price)
                     
                    print(f"Would place SELL order for {tsla_qty} shares at current price: ${current_price:.2f}")
                else:
                    print("No TSLA positions to sell")
                 
            else:
                print("Prediction: No significant change expected")
                print("No orders placed")
                 
            # Check account info (optional)
            account_info = get_account_info(alpaca_client)
            print(f"Buying Power: ${account_info.get('buying_power', 'N/A')}")
             
        else:
             print("Failed to load model. Please train a model first.")
         
         # Calculate how long the loop took and adjust sleep time
        elapsed_time = time.time() - start_time
        sleep_time = max(0, 60 - elapsed_time)  # Ensure sleep_time is not negative
         
        print(f"Loop completed in {elapsed_time:.2f} seconds. Sleeping for {sleep_time:.2f} seconds.")
        time.sleep(sleep_time)

    

if __name__ == "__main__":
    main()