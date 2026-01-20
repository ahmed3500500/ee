import asyncio
from market_data import fetch_ohlcv, close_exchange
from analysis import calculate_indicators, analyze_market_structure

async def test_run():
    symbol = 'BTC/USDT'
    print(f"🔍 Analyzing {symbol}...")
    
    # 1. Fetch Data
    df = await fetch_ohlcv(symbol, '1h', limit=300)
    
    if df.empty:
        print("❌ Failed to fetch data.")
        return

    # 2. Calculate Indicators
    df = calculate_indicators(df)
    
    # 3. Analyze
    result = analyze_market_structure(df)
    
    if result:
        print("\n📊 ANALYSIS RESULT:")
        print(f"Time: {result['timestamp']}")
        print(f"Price: {result['price']}")
        print(f"RSI: {result['rsi']:.2f}")
        print(f"Score: {result['score']}/100")
        print(f"Status: {result['status']}")
        print("Reasons:")
        for r in result['reasons']:
            print(f" - {r}")
    else:
        print("Not enough data to analyze.")

    await close_exchange()

if __name__ == "__main__":
    asyncio.run(test_run())
