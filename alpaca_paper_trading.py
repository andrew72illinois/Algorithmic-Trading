from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest

def setup_client(key_: str, secret_: str, paper_: bool, base_url_: str):
    return TradingClient(api_key=key_, secret_key=secret_, paper=paper_)
    





