import pandas as pd
import pandas_ta as ta
import pytz
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.requests import StockLatestBarRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.timeframe import TimeFrameUnit
from datetime import time
from datetime import datetime
from datetime import timedelta


# Function to start up the main client for retrieving data
def setup_historical_client(key_: str,secret_: str, base_url_: str, raw_data_: bool):
    return StockHistoricalDataClient(
        api_key=key_, 
        secret_key=secret_, 
        raw_data=raw_data_
    )

# Function to retrieve the latest bars 
def retrieve_stock_bars(client_: StockHistoricalDataClient, symbol_: str, time_interval_: int, time_unit_: TimeFrameUnit, limit_: int):
    # Get ET and UTC time zones
    eastern = pytz.timezone("America/New_York")
    utc = pytz.UTC
    # Get current time and calculate start and end time for StockBarsRequest by calculating ET then converting to UTC
    now_et = datetime.now(eastern) 
    start_et = (now_et - timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_et = (now_et + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    start_utc = start_et.astimezone(utc)
    end_utc = end_et.astimezone(utc)
    prev_stock_bar_params = StockBarsRequest(
        symbol_or_symbols=symbol_,
        start=start_utc,
        end=end_utc,
        timeframe=TimeFrame(
            amount=time_interval_,
            unit=time_unit_),
        limit=limit_,
        feed="iex",
        sort="desc"
    )
    return client_.get_stock_bars(request_params=prev_stock_bar_params)

# Function to retrieve the single latest bar 
def retrieve_latest(client_: StockHistoricalDataClient, symbol_: str):
    latest_params = StockLatestBarRequest(symbol_or_symbols=symbol_)
    return client_.get_stock_latest_bar(request_params=latest_params)

# Function to convert raw bar data to an easy to parse dataframe
def data_frame_from_stock_bars(data_: dict):
    ticker, bars = next(iter(data_.items()))

    if not bars:
        raise ValueError(f"No data retrieved for ticker: {ticker}")
    
    df = pd.DataFrame(bars) # Create data frame from raw data
    df.rename(columns={'o':'open', 'h':'high','l':'low','c':'close','v':'volume','t':'timestamp'}, inplace=True) # Rename columns
    df['timestamp'] = pd.to_datetime(df['timestamp']) # Set time stamp to type datetime
    df.set_index('timestamp', inplace=True) # Index using time stamp
    eastern_time_zone = pytz.timezone("America/New_York") # Create ET timezone 
    df.index = df.index.tz_convert(eastern_time_zone) # Convert data frame times from UTC to ET 

    df['market_status'] = df.index.map(classify_market_status) # Use helper function to get market status

    return df[['close','high','low','open','volume', 'market_status']]

# Helper function used to classify market status in dataframe
def classify_market_status(dt: pd.Timestamp) -> str:
    t = dt.time()
    if time(4, 0) <= t < time(9, 30):
        return "pre-market"
    elif time(9, 30) <= t < time(16, 0):
        return "regular"
    elif time(16, 0) <= t < time(20, 0):
        return "after-hours"
    else:
        return "closed"

def filter_regular_hours(data_: pd.DataFrame) -> pd.DataFrame: 
    return data_[data_["market_status"] == "regular"]

def add_technical_indicators(data_: pd.DataFrame) -> pd.DataFrame:
    data_ = data_.sort_index()
    data_['ATR'] = data_.ta.atr(length=20) # Average True Range for 20 candlesticks
    data_['RSI'] = data_.ta.rsi() # Relative Strength Index
    data_['MA40'] = data_.ta.sma(length=40) # Moving Average for 40 candlesticks
    data_['MA80'] = data_.ta.sma(length=80) # Moving Average for 80 candlesticks
    data_['MA160'] = data_.ta.sma(length=160) # Moving Average for 160 candlesticks
    return data_

# Creates target variable for ML prediction
# New column "Higher/Lower" indicates whether the NEXT candlestick's open price
# will be higher (1), lower (-1), or same (0) than the CURRENT close price
# Note: Data is sorted chronologically (oldest first) to ensure proper time sequence
def classify_price_gap(data_: pd.DataFrame) -> pd.DataFrame:
    data_ = data_.copy()
    # Sort by timestamp to ensure chronological order (oldest first)
    data_ = data_.sort_index()
    
    # Calculate whether the NEXT candlestick's open is higher/lower than CURRENT close
    # This creates a target variable for ML prediction
    data_['next_open_vs_current_close'] = data_['open'].shift(-1) - data_['close']
    data_['Higher/Lower'] = data_['next_open_vs_current_close'].apply(
        lambda x: -1 if x < 0 else (1 if x > 0 else 0)
    )
    # Drop the last row since we can't predict the next candlestick for it
    # data_ = data_.dropna()
    return data_