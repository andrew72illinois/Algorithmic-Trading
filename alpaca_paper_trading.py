from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest, MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

def setup_client(key_: str, secret_: str, paper_: bool, base_url_: str):
    return TradingClient(api_key=key_, secret_key=secret_, paper=paper_)


def place_market_buy_order(client: TradingClient, symbol: str, quantity: int) -> dict:
    """
    Place a market buy order.
    
    Args:
        client: Alpaca trading client
        symbol: Stock symbol (e.g., 'TSLA')
        quantity: Number of shares to buy
        
    Returns:
        Order response dictionary
    """
    try:
        # Create market order request
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        
        # Submit the order
        order = client.submit_order(order_data=market_order_data)
        
        print(f"Market BUY order placed for {quantity} shares of {symbol}")
        print(f"Order ID: {order.id}")
        print(f"Status: {order.status}")
        
        return {
            'success': True,
            'order_id': order.id,
            'status': order.status,
            'symbol': symbol,
            'quantity': quantity,
            'side': 'BUY',
            'order_type': 'MARKET'
        }
        
    except Exception as e:
        print(f"Error placing market buy order: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def place_limit_buy_order(client: TradingClient, symbol: str, quantity: int, limit_price: float) -> dict:
    """
    Place a limit buy order.
    
    Args:
        client: Alpaca trading client
        symbol: Stock symbol (e.g., 'TSLA')
        quantity: Number of shares to buy
        limit_price: Maximum price willing to pay per share
        
    Returns:
        Order response dictionary
    """
    try:
        # Create limit order request
        limit_order_data = LimitOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
            limit_price=limit_price
        )
        
        # Submit the order
        order = client.submit_order(order_data=limit_order_data)
        
        print(f"Limit BUY order placed for {quantity} shares of {symbol} at ${limit_price}")
        print(f"Order ID: {order.id}")
        print(f"Status: {order.status}")
        
        return {
            'success': True,
            'order_id': order.id,
            'status': order.status,
            'symbol': symbol,
            'quantity': quantity,
            'limit_price': limit_price,
            'side': 'BUY',
            'order_type': 'LIMIT'
        }
        
    except Exception as e:
        print(f"Error placing limit buy order: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def get_account_info(client: TradingClient) -> dict:
    """
    Get account information including buying power.
    
    Args:
        client: Alpaca trading client
        
    Returns:
        Account information dictionary
    """
    try:
        account = client.get_account()
        
        return {
            'buying_power': float(account.buying_power),
            'cash': float(account.cash),
            'portfolio_value': float(account.portfolio_value),
            'equity': float(account.equity),
            'pattern_day_trader': account.pattern_day_trader
        }
        
    except Exception as e:
        print(f"Error getting account info: {e}")
        return {'error': str(e)}


def place_market_sell_order(client: TradingClient, symbol: str, quantity: int) -> dict:
    """
    Place a market sell order.
    
    Args:
        client: Alpaca trading client
        symbol: Stock symbol (e.g., 'TSLA')
        quantity: Number of shares to sell
        
    Returns:
        Order response dictionary
    """
    try:
        # Create market order request
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        
        # Submit the order
        order = client.submit_order(order_data=market_order_data)
        
        print(f"Market SELL order placed for {quantity} shares of {symbol}")
        print(f"Order ID: {order.id}")
        print(f"Status: {order.status}")
        
        return {
            'success': True,
            'order_id': order.id,
            'status': order.status,
            'symbol': symbol,
            'quantity': quantity,
            'side': 'SELL',
            'order_type': 'MARKET'
        }
        
    except Exception as e:
        print(f"Error placing market sell order: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def place_limit_sell_order(client: TradingClient, symbol: str, quantity: int, limit_price: float) -> dict:
    """
    Place a limit sell order.
    
    Args:
        client: Alpaca trading client
        symbol: Stock symbol (e.g., 'TSLA')
        quantity: Number of shares to sell
        limit_price: Minimum price willing to accept per share
        
    Returns:
        Order response dictionary
    """
    try:
        # Create limit order request
        limit_order_data = LimitOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
            limit_price=limit_price
        )
        
        # Submit the order
        order = client.submit_order(order_data=limit_order_data)
        
        print(f"Limit SELL order placed for {quantity} shares of {symbol} at ${limit_price}")
        print(f"Order ID: {order.id}")
        print(f"Status: {order.status}")
        
        return {
            'success': True,
            'order_id': order.id,
            'status': order.status,
            'symbol': symbol,
            'quantity': quantity,
            'limit_price': limit_price,
            'side': 'SELL',
            'order_type': 'LIMIT'
        }
        
    except Exception as e:
        print(f"Error placing limit sell order: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def get_positions(client: TradingClient) -> dict:
    """
    Get current positions (stocks you own).
    
    Args:
        client: Alpaca trading client
        
    Returns:
        Dictionary of current positions
    """
    try:
        positions = client.get_all_positions()
        
        positions_dict = {}
        for position in positions:
            positions_dict[position.symbol] = {
                'symbol': position.symbol,
                'qty': float(position.qty),
                'market_value': float(position.market_value),
                'cost_basis': float(position.cost_basis),
                'unrealized_pl': float(position.unrealized_pl),
                'unrealized_plpc': float(position.unrealized_plpc),
                'current_price': float(position.current_price)
            }
        
        return positions_dict
        
    except Exception as e:
        print(f"Error getting positions: {e}")
        return {'error': str(e)}





