from personal import alpaca_api_key, alpaca_secret, alpaca_base_url
from alpaca_data import setup_historical_client
from alpaca_data import retrieve_stock_bars
from alpaca_data import data_frame_from_stock_bars
from alpaca_data import retrieve_latest
from alpaca_data import filter_regular_hours
from alpaca_data import add_technical_indicators
from alpaca_paper_trading import setup_client


from alpaca.data.timeframe import TimeFrameUnit

def main() -> None:
    # alpaca_client = setup_client(key_=alpaca_api_key, secret_=alpaca_secret, paper_=True, base_url_=alpaca_base_url)
    alpaca_historical_client = setup_historical_client(key_=alpaca_api_key, secret_=alpaca_secret, base_url_=alpaca_base_url, raw_data_= True)

    stock_bars = retrieve_stock_bars(client_=alpaca_historical_client, symbol_= "TSLA", time_interval_=1, time_unit_=TimeFrameUnit.Minute, limit_= 180)
    stock_data_frame = data_frame_from_stock_bars(data_ = stock_bars)
    filtered_data_frame = filter_regular_hours(data_= stock_data_frame)
    technical_data_frame = add_technical_indicators(filtered_data_frame.copy())
    # technical_data_frame.to_csv('see_all.txt', sep='\t', index=False)
    print(technical_data_frame)


    

if __name__ == "__main__":
    main()