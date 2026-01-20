import ccxt.async_support as ccxt
import asyncio

async def test():
    exchange = ccxt.mexc({
        'timeout': 30000,
        'enableRateLimit': True,
    })
    try:
        print("Testing MEXC connectivity...")
        ticker = await exchange.fetch_ticker('BTC/USDT')
        print(f"Ticker success: {ticker['last']}")
    except Exception as e:
        print(f"Error type: {type(e)}")
        print(f"Error: {e}")
    finally:
        await exchange.close()

asyncio.run(test())