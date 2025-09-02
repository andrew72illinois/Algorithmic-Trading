#!/usr/bin/env python3
"""
Test script for the Alpaca WebSocket backend
Run this to test the websocket connection and data flow
"""

import asyncio
import websockets
import json
import sys

async def test_websocket_connection():
    """Test the websocket connection to the backend"""
    uri = "ws://localhost:8000/ws/candles/AAPL"
    
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to backend websocket!")
            
            # Listen for messages
            message_count = 0
            async for message in websocket:
                data = json.loads(message)
                message_count += 1
                
                if data.get("type") == "historical":
                    print(f"📊 Received historical data: {len(data['data'])} bars")
                    print(f"   Sample data: {data['data'][0] if data['data'] else 'No data'}")
                    
                elif data.get("type") == "bar":
                    print(f"📈 Real-time bar update: {data['symbol']} - ${data['close']}")
                    
                elif data.get("type") == "pong":
                    print("🏓 Pong received")
                
                # Stop after receiving some messages for testing
                if message_count >= 10:
                    print("✅ Test completed successfully!")
                    break
                    
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused. Make sure the backend server is running on localhost:8000")
        print("   Run: uvicorn backend.server:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_rest_api():
    """Test the REST API endpoints"""
    import aiohttp
    
    base_url = "http://localhost:8000"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            async with session.get(f"{base_url}/api/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check: {data}")
                else:
                    print(f"❌ Health check failed: {response.status}")
            
            # Test historical data endpoint
            async with session.get(f"{base_url}/api/symbols/AAPL/historical?limit=5") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Historical data: {len(data['data'])} bars received")
                else:
                    print(f"❌ Historical data failed: {response.status}")
                    
            # Test latest price endpoint
            async with session.get(f"{base_url}/api/symbols/AAPL/latest") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Latest price: {data}")
                else:
                    print(f"❌ Latest price failed: {response.status}")
                    
    except Exception as e:
        print(f"❌ REST API test error: {e}")

async def main():
    """Run all tests"""
    print("🚀 Testing Alpaca WebSocket Backend")
    print("=" * 50)
    
    print("\n1. Testing REST API endpoints...")
    await test_rest_api()
    
    print("\n2. Testing WebSocket connection...")
    await test_websocket_connection()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
