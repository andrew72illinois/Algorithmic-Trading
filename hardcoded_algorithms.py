import pandas as pd

def RSI_MA_Crossover(data_: pd.DataFrame) -> str:
    # Get indicators 
    rsi_prev, rsi_curr = data_["RSI"].tail(2)
    close = data_["close"].tail(1)
    ma40 = data_["MA40"].tail(1)
    ma80 = data_["MA80"].tail(1)
    # Buy
    if(rsi_prev < 30 and 
    rsi_curr >= 30 and 
    close > ma40 and
    close > ma80):
        return "Buy"
    # Sell
    elif(rsi_prev > 70 and rsi_curr <= 70 and
            (close < ma40 or close < ma80)):
        return "Sell"
    # Hold
    else: 
        return "Hold"
    
