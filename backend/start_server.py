#!/usr/bin/env python3
"""
Startup script for the Alpaca Trading Backend
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import alpaca_data
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

if __name__ == "__main__":
    print("🚀 Starting Alpaca Trading Backend Server...")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws/candles/{symbol}")
    print("🌐 REST API: http://localhost:8000")
    print("📊 Health check: http://localhost:8000/api/health")
    print("=" * 60)
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
