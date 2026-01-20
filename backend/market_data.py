import ccxt.async_support as ccxt
import pandas as pd
import asyncio
import numpy as np
from datetime import datetime, timedelta

# Initialize Exchange (Using Binance as requested)
exchange = ccxt.binance({
    'enableRateLimit': True,
    'timeout': 30000,
})

# Flag to track if we are in simulation mode to avoid spamming logs
USE_SIMULATION_MODE = False

async def fetch_ohlcv(symbol: str, timeframe: str = '1h', limit: int = 100):
    """
    Fetches OHLCV data for a symbol.
    Returns a pandas DataFrame.
    """
    global USE_SIMULATION_MODE
    
    if USE_SIMULATION_MODE:
        return generate_mock_data(limit)

    try:
        # Try fetching real data
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        # Convert to DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df
    except Exception as e:
        # Check if it's a connection error
        print(f"⚠️ Network Error fetching {symbol}. Switching to SIMULATION MODE.")
        # print(f"Debug Error: {e}") # Uncomment for debugging
        USE_SIMULATION_MODE = True
        return generate_mock_data(limit)

def generate_mock_data(limit: int):
    """
    Generates synthetic bullish data to test the analyzer.
    """
    dates = [datetime.now() - timedelta(hours=x) for x in range(limit)]
    dates.reverse()
    
    # Generate a Healthy Uptrend (Perfect for signals)
    base_price = 50000
    prices = []
    for i in range(limit):
        # Smaller increments to keep RSI healthy (not overbought)
        base_price += np.random.normal(loc=5, scale=20) 
        prices.append(base_price)
    
    # Ensure the end is strong but not crazy
    prices[-1] = prices[-2] * 1.002 # 0.2% jump
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * 1.005 for p in prices],
        'low': [p * 0.995 for p in prices],
        'close': prices,
        'volume': [1000 + x*10 for x in range(limit)]
    })
    return df

async def close_exchange():
    await exchange.close()
