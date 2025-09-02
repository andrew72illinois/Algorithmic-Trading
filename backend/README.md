# Alpaca Trading Backend

A FastAPI-based backend server that provides real-time stock data via WebSockets and REST API endpoints using Alpaca's data services.

## Features

- 🔄 **Real-time WebSocket streaming** of stock data from Alpaca
- 📊 **Historical data API** with technical indicators
- 🏥 **Health monitoring** and connection management
- 🔐 **Environment variable** configuration for API keys
- 📈 **Multiple timeframes** support (1Min, 5Min, 1Hour, 1Day)

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Make sure your `environment.env` file (in the parent directory) contains:

```env
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
ALPACA_ENDPOINT=https://paper-api.alpaca.markets/v2
```

### 3. Start the Server

```bash
python start_server.py
```

Or using uvicorn directly:

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### WebSocket Endpoints

#### Real-time Data Stream
```
ws://localhost:8000/ws/candles/{symbol}
```

**Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/candles/AAPL');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'historical') {
        console.log('Historical data:', data.data);
    } else if (data.type === 'bar') {
        console.log('Real-time bar:', data);
    }
};
```

### REST API Endpoints

#### Health Check
```
GET /api/health
```

#### Historical Data
```
GET /api/symbols/{symbol}/historical?timeframe=1Min&limit=100
```

**Parameters:**
- `symbol`: Stock symbol (e.g., AAPL, GOOGL, MSFT)
- `timeframe`: 1Min, 5Min, 1Hour, 1Day (default: 1Min)
- `limit`: Number of bars to return (default: 100)

#### Latest Price
```
GET /api/symbols/{symbol}/latest
```

## Data Format

### WebSocket Messages

#### Historical Data
```json
{
    "type": "historical",
    "symbol": "AAPL",
    "data": [
        {
            "timestamp": "2024-01-15T09:30:00-05:00",
            "open": 150.0,
            "high": 151.0,
            "low": 149.5,
            "close": 150.5,
            "volume": 1000000,
            "market_status": "regular",
            "ATR": 1.2,
            "RSI": 45.5,
            "MA40": 149.8,
            "MA80": 148.5,
            "MA160": 147.2
        }
    ]
}
```

#### Real-time Bar Updates
```json
{
    "type": "bar",
    "symbol": "AAPL",
    "timestamp": "2024-01-15T09:31:00-05:00",
    "open": 150.5,
    "high": 150.8,
    "low": 150.2,
    "close": 150.6,
    "volume": 50000
}
```

## Testing

Run the test script to verify everything is working:

```bash
python test_websocket.py
```

This will test both REST API endpoints and WebSocket connections.

## Architecture

```
┌─────────────────┐    WebSocket    ┌──────────────────┐
│   Frontend      │◄──────────────►│   FastAPI        │
│   (React/Vue)   │                 │   Backend        │
└─────────────────┘                 └──────────────────┘
                                             │
                                             │ WebSocket
                                             ▼
                                    ┌──────────────────┐
                                    │   Alpaca Data    │
                                    │   Stream         │
                                    └──────────────────┘
```

## Key Components

1. **AlpacaWebSocketManager**: Manages the connection to Alpaca's real-time data stream
2. **WebSocket Endpoint**: Handles client connections and data forwarding
3. **REST API**: Provides historical data and latest prices
4. **Connection Management**: Automatically subscribes/unsubscribes from symbols

## Error Handling

The server includes comprehensive error handling for:
- WebSocket connection failures
- Alpaca API authentication issues
- Client disconnections
- Data parsing errors

## Security Notes

- API keys are loaded from environment variables
- CORS is configured (restrict origins in production)
- WebSocket connections are properly cleaned up on disconnect

## Troubleshooting

### Common Issues

1. **Connection Refused**: Make sure the server is running on port 8000
2. **Authentication Failed**: Check your Alpaca API credentials in `environment.env`
3. **No Data**: Verify the symbol exists and markets are open
4. **WebSocket Disconnects**: Check network stability and Alpaca service status

### Logs

The server provides detailed logging for debugging:
- WebSocket connection status
- Subscription/unsubscription events
- Data flow and errors
- Client connection management
