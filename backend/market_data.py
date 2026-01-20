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
        return generate_mock_data(symbol, limit)

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
        return generate_mock_data(symbol, limit)

# Base prices for simulation (approximate)
MOCK_PRICES = {
    'BTC/USDT': 52000, 'ETH/USDT': 2800, 'BNB/USDT': 350, 'SOL/USDT': 110, 'XRP/USDT': 0.55,
    'ADA/USDT': 0.60, 'AVAX/USDT': 40, 'DOGE/USDT': 0.085, 'DOT/USDT': 7.5, 'TRX/USDT': 0.13,
    'LINK/USDT': 19, 'POL/USDT': 0.80, 'SHIB/USDT': 0.000009, 'LTC/USDT': 70, 'BCH/USDT': 270,
    'ATOM/USDT': 10, 'UNI/USDT': 7, 'XLM/USDT': 0.11, 'ETC/USDT': 25, 'FIL/USDT': 7.5,
    'HBAR/USDT': 0.10, 'APT/USDT': 9, 'NEAR/USDT': 3.5, 'VET/USDT': 0.04, 'QNT/USDT': 110,
    'AAVE/USDT': 90, 'GRT/USDT': 0.25, 'ALGO/USDT': 0.18, 'STX/USDT': 2.5, 'EOS/USDT': 0.75,
    'SAND/USDT': 0.50, 'THETA/USDT': 1.2, 'EGLD/USDT': 55, 'MANA/USDT': 0.50, 'AXS/USDT': 7.5,
    'FTM/USDT': 0.40, 'FLOW/USDT': 0.90, 'XTZ/USDT': 1.0, 'CHZ/USDT': 0.10, 'SUI/USDT': 1.8,
    'ICP/USDT': 13, 'ARB/USDT': 1.9, 'OP/USDT': 3.8, 'LDO/USDT': 3.0, 'RENDER/USDT': 5.0,
    'INJ/USDT': 35, 'IMX/USDT': 3.0, 'GALA/USDT': 0.03, 'SNX/USDT': 3.5, 'CRV/USDT': 0.55
}

def generate_mock_data(symbol: str, limit: int):
    """
    Generates synthetic bullish data to test the analyzer.
    """
    dates = [datetime.now() - timedelta(hours=x) for x in range(limit)]
    dates.reverse()
    
    # Get base price for the specific coin
    base_price = MOCK_PRICES.get(symbol, 100) # Default 100 if unknown
    
    prices = []
    for i in range(limit):
        # Smaller increments relative to price
        change = np.random.normal(loc=0.0001 * base_price, scale=0.005 * base_price)
        base_price += change
        # Ensure price doesn't go negative
        base_price = max(0.000001, base_price)
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
