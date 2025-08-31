from personal import alpaca_api_key, alpaca_secret, alpaca_base_url
from alpaca_data import (
    setup_historical_client, 
    retrieve_stock_bars,
    data_frame_from_stock_bars,
    retrieve_latest,
    filter_regular_hours,
    add_technical_indicators,
    classify_price_gap
)
from trading_algorithms import (
    train_and_test_KNN,
    train_and_test_RF
)
from alpaca_paper_trading import setup_client


from alpaca.data.timeframe import TimeFrameUnit

def main() -> None:
    # alpaca_client = setup_client(key_=alpaca_api_key, secret_=alpaca_secret, paper_=True, base_url_=alpaca_base_url)
    alpaca_historical_client = setup_historical_client(key_=alpaca_api_key, secret_=alpaca_secret, base_url_=alpaca_base_url, raw_data_= True)

    stock_bars = retrieve_stock_bars(client_=alpaca_historical_client, symbol_= "TSLA", time_interval_=1, time_unit_=TimeFrameUnit.Minute, limit_= 1000)
    stock_data_frame = data_frame_from_stock_bars(data_ = stock_bars)
    filtered_data_frame = filter_regular_hours(data_= stock_data_frame)
    technical_data_frame = add_technical_indicators(data_=filtered_data_frame.copy())
    classified_data_frame = classify_price_gap(data_=technical_data_frame)
    # for k in range(1, 24):
    #     print(f"K={k}\n")
    #     train_and_test_KNN(data_= classified_data_frame, neighbors_=k)
    train_and_test_RF(data_=classified_data_frame)


    

if __name__ == "__main__":
    main()