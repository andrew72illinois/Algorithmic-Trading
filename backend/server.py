from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
import websockets
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime, timedelta
import pytz
import pandas as pd

# Import your alpaca_data module
import alpaca_data as ad

load_dotenv('environment.env')
alpaca_api_key = os.getenv('ALPACA_API_KEY')
alpaca_secret = os.getenv('ALPACA_SECRET')
alpaca_base_url = os.getenv('ALPACA_BASE_URL')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active websocket connections
connections = {}

# Alpaca WebSocket URL for real-time data
ALPACA_WS_URL = "wss://stream.data.alpaca.markets/v2/iex"

class AlpacaWebSocketManager:
    def __init__(self):
        self.connections = {}
        self.alpaca_ws = None
        self.subscribed_symbols = set()
        
    async def connect_to_alpaca(self):
        """Connect to Alpaca's websocket for real-time data"""
        try:
            # Alpaca websocket authentication
            auth_message = {
                "action": "auth",
                "key": alpaca_api_key,
                "secret": alpaca_secret
            }
            
            self.alpaca_ws = await websockets.connect(ALPACA_WS_URL)
            await self.alpaca_ws.send(json.dumps(auth_message))
            
            # Listen for authentication response
            response = await self.alpaca_ws.recv()
            auth_response = json.loads(response)
            
            if auth_response.get("T") == "success" and auth_response.get("msg") == "authenticated":
                print("Successfully connected to Alpaca WebSocket")
                return True
            else:
                print(f"Authentication failed: {auth_response}")
                return False
                
        except Exception as e:
            print(f"Error connecting to Alpaca WebSocket: {e}")
            return False
    
    async def subscribe_to_symbol(self, symbol: str):
        """Subscribe to real-time data for a symbol"""
        if symbol not in self.subscribed_symbols:
            subscribe_message = {
                "action": "subscribe",
                "bars": [symbol]
            }
            await self.alpaca_ws.send(json.dumps(subscribe_message))
            self.subscribed_symbols.add(symbol)
            print(f"Subscribed to {symbol}")
    
    async def unsubscribe_from_symbol(self, symbol: str):
        """Unsubscribe from real-time data for a symbol"""
        if symbol in self.subscribed_symbols:
            unsubscribe_message = {
                "action": "unsubscribe",
                "bars": [symbol]
            }
            await self.alpaca_ws.send(json.dumps(unsubscribe_message))
            self.subscribed_symbols.remove(symbol)
            print(f"Unsubscribed from {symbol}")
    
    async def listen_for_data(self):
        """Listen for incoming data from Alpaca and forward to connected clients"""
        try:
            while True:
                data = await self.alpaca_ws.recv()
                message = json.loads(data)
                
                # Forward bar data to connected clients
                if message.get("T") == "b" and "data" in message:
                    symbol = message["data"]["S"]
                    if symbol in self.connections:
                        # Format the data for frontend
                        formatted_data = {
                            "type": "bar",
                            "symbol": symbol,
                            "timestamp": message["data"]["t"],
                            "open": message["data"]["o"],
                            "high": message["data"]["h"],
                            "low": message["data"]["l"],
                            "close": message["data"]["c"],
                            "volume": message["data"]["v"]
                        }
                        
                        # Send to all connected clients for this symbol
                        for websocket in self.connections[symbol]:
                            try:
                                await websocket.send_text(json.dumps(formatted_data))
                            except:
                                # Remove disconnected clients
                                self.connections[symbol].remove(websocket)
                                
        except websockets.exceptions.ConnectionClosed:
            print("Alpaca WebSocket connection closed")
        except Exception as e:
            print(f"Error in listen_for_data: {e}")

# Global WebSocket manager
ws_manager = AlpacaWebSocketManager()

@app.on_event("startup")
async def startup_event():
    """Initialize Alpaca WebSocket connection on startup"""
    await ws_manager.connect_to_alpaca()
    # Start listening for data in background
    asyncio.create_task(ws_manager.listen_for_data())

@app.websocket("/ws/candles/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await websocket.accept()
    
    # Add connection to manager
    if symbol not in ws_manager.connections:
        ws_manager.connections[symbol] = []
    ws_manager.connections[symbol].append(websocket)
    
    # Subscribe to symbol if not already subscribed
    await ws_manager.subscribe_to_symbol(symbol)
    
    try:
        # Send initial historical data
        hist_client = ad.setup_historical_client(
            key_=alpaca_api_key, 
            secret_=alpaca_secret, 
            base_url_=alpaca_base_url, 
            raw_data_=True
        )
        
        # Get recent historical data
        bars_data = ad.retrieve_stock_bars(
            client_=hist_client,
            symbol_=symbol,
            time_interval_=1,
            time_unit_=TimeFrameUnit.Minute,
            limit_=100
        )
        
        # Convert to DataFrame and send
        df = ad.data_frame_from_stock_bars(bars_data.data)
        df = ad.add_technical_indicators(df)
        
        # Send historical data
        historical_data = {
            "type": "historical",
            "symbol": symbol,
            "data": df.to_dict('records')
        }
        await websocket.send_text(json.dumps(historical_data))
        
        # Keep connection alive and listen for client messages
        while True:
            try:
                # Wait for messages from client (like subscription changes)
                message = await websocket.receive_text()
                data = json.loads(message)
                
                if data.get("action") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                    
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        print(f"Error in websocket endpoint: {e}")
    finally:
        # Clean up connection
        if symbol in ws_manager.connections:
            ws_manager.connections[symbol].remove(websocket)
            if not ws_manager.connections[symbol]:
                del ws_manager.connections[symbol]
                await ws_manager.unsubscribe_from_symbol(symbol)

# REST API endpoints
@app.get("/")
async def root():
    return {"message": "Alpaca Trading Backend API", "status": "running"}

@app.get("/api/symbols/{symbol}/historical")
async def get_historical_data(symbol: str, timeframe: str = "1Min", limit: int = 100):
    """Get historical data for a symbol"""
    try:
        hist_client = ad.setup_historical_client(
            key_=alpaca_api_key, 
            secret_=alpaca_secret, 
            base_url_=alpaca_base_url, 
            raw_data_=True
        )
        
        # Parse timeframe
        if timeframe == "1Min":
            time_interval = 1
            time_unit = TimeFrameUnit.Minute
        elif timeframe == "5Min":
            time_interval = 5
            time_unit = TimeFrameUnit.Minute
        elif timeframe == "1Hour":
            time_interval = 1
            time_unit = TimeFrameUnit.Hour
        elif timeframe == "1Day":
            time_interval = 1
            time_unit = TimeFrameUnit.Day
        else:
            time_interval = 1
            time_unit = TimeFrameUnit.Minute
        
        bars_data = ad.retrieve_stock_bars(
            client_=hist_client,
            symbol_=symbol,
            time_interval_=time_interval,
            time_unit_=time_unit,
            limit_=limit
        )
        
        df = ad.data_frame_from_stock_bars(bars_data.data)
        df = ad.add_technical_indicators(df)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": df.to_dict('records')
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/symbols/{symbol}/latest")
async def get_latest_price(symbol: str):
    """Get latest price for a symbol"""
    try:
        hist_client = ad.setup_historical_client(
            key_=alpaca_api_key, 
            secret_=alpaca_secret, 
            base_url_=alpaca_base_url, 
            raw_data_=True
        )
        
        latest_data = ad.retrieve_latest(hist_client, symbol)
        
        if latest_data and symbol in latest_data:
            bar = latest_data[symbol]
            return {
                "symbol": symbol,
                "timestamp": bar.t,
                "open": bar.o,
                "high": bar.h,
                "low": bar.l,
                "close": bar.c,
                "volume": bar.v
            }
        else:
            return {"error": f"No data found for {symbol}"}
            
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "alpaca_connected": ws_manager.alpaca_ws is not None,
        "active_connections": len(ws_manager.connections),
        "subscribed_symbols": list(ws_manager.subscribed_symbols)
    }
    