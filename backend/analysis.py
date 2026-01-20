import pandas as pd
import pandas_ta as ta

def calculate_indicators(df: pd.DataFrame):
    """
    Calculates EMA20, EMA50, EMA200, RSI(14), ADX(14), ATR(14).
    """
    if df.empty:
        return df
    
    # EMAs
    df['EMA_20'] = ta.ema(df['close'], length=20)
    df['EMA_50'] = ta.ema(df['close'], length=50)
    df['EMA_200'] = ta.ema(df['close'], length=200)
    
    # RSI
    df['RSI'] = ta.rsi(df['close'], length=14)
    
    # ADX (Trend Strength)
    adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
    if adx_df is not None:
        # Join ADX columns properly
        df = df.join(adx_df)
    
    # ATR (Volatility for Stop Loss)
    df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    
    return df

def analyze_market_structure(df: pd.DataFrame):
    """
    Analyzes the latest candle to determine if it's a BUY opportunity.
    Returns a dictionary with signal details and score.
    """
    if df.empty or len(df) < 200:
        return None

    last_row = df.iloc[-1]
    
    close = last_row['close']
    ema20 = last_row['EMA_20']
    ema50 = last_row['EMA_50']
    ema200 = last_row['EMA_200']
    rsi = last_row['RSI']
    # Use ADX_14 if available, else default to 25 (neutral)
    adx = last_row.get('ADX_14', 25) 
    atr = last_row.get('ATR', close * 0.02)
    
    score = 0
    reasons = []
    
    # 1. Trend Filter (0-40 points)
    if close > ema20 > ema50 > ema200:
        score += 40
        reasons.append("Strong Uptrend (Price > EMA20 > EMA50 > EMA200)")
    elif close > ema200 and ema20 > ema50:
        score += 30
        reasons.append("Moderate Uptrend (Above EMA200, Golden Cross)")
    elif close > ema200:
        score += 10
        reasons.append("Above EMA200 (Long term bullish)")
        
    # 2. RSI Filter (0-20 points)
    if 45 <= rsi <= 65:
        score += 20
        reasons.append(f"Healthy Momentum (RSI: {rsi:.1f})")
    elif 30 <= rsi < 45:
        score += 10
        reasons.append(f"Oversold/Recovery (RSI: {rsi:.1f})")
    elif rsi > 70:
        score -= 10
        reasons.append(f"Overbought (RSI: {rsi:.1f}) - Risk of pullback")
        
    # 3. Volume/Breakout (Simplified logic for now)
    avg_vol = df['volume'].rolling(20).mean().iloc[-1]
    if last_row['volume'] > avg_vol * 1.5:
        score += 10
        reasons.append("High Volume Spike")
        
    # 4. ADX Filter (Trend Strength) - NEW
    if adx > 25:
        score += 10
        reasons.append(f"Strong Trend Strength (ADX: {adx:.1f})")
    elif adx < 20:
        score -= 10
        reasons.append(f"Weak Trend/Choppy Market (ADX: {adx:.1f})")

    # Determine Status
    status = "WEAK"
    if score >= 80:
        status = "STRONG"
    elif score >= 50:
        status = "MEDIUM"
        
    # Dynamic Risk Management (ATR Based) - NEW
    # Stop Loss: 2 ATR below close (more room to breathe)
    # TP1: 1.5 ATR
    # TP2: 3 ATR
    stop_loss = close - (atr * 2.0)
    target1 = close + (atr * 1.5)
    target2 = close + (atr * 3.0)
    
    # Calculate Risk/Reward Ratio for display
    risk = close - stop_loss
    reward = target2 - close
    rr_ratio = f"1:{reward/risk:.1f}" if risk > 0 else "N/A"
    
    return {
        "price": close,
        "score": score,
        "status": status,
        "rsi": rsi,
        "adx": adx,
        "reasons": reasons,
        "timestamp": last_row['timestamp'],
        "trade_setup": {
            "entry_zone": f"{close:.4f} - {close + (atr*0.2):.4f}",
            "stop_loss": stop_loss,
            "target_1": target1,
            "target_2": target2,
            "risk_reward_ratio": rr_ratio
        }
    }
