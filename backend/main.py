from fastapi import FastAPI, BackgroundTasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from market_data import fetch_ohlcv
from analysis import calculate_indicators, analyze_market_structure
import asyncio
import os
import firebase_admin
from firebase_admin import credentials, messaging

app = FastAPI(title="Crypto Signals API")

# --- FIREBASE SETUP ---
FCM_ENABLED = False
try:
    if os.path.exists("serviceAccountKey.json"):
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        FCM_ENABLED = True
        print("✅ Firebase Admin Initialized")
    else:
        print("⚠️ serviceAccountKey.json not found. FCM Notifications will be SKIPPED.")
except Exception as e:
    print(f"⚠️ Firebase Initialization Error: {e}")

def send_fcm_notification(topic, title, body):
    """
    Sends a push notification to a specific topic.
    """
    if not FCM_ENABLED:
        return
    
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            topic=topic,
        )
        response = messaging.send(message)
        print(f"🚀 FCM Sent to {topic}: {response}")
    except Exception as e:
        print(f"❌ FCM Error ({topic}): {e}")


# Store signals in memory for MVP
latest_signals = []
signal_history = []
# NEW: Store active signals to track profits
active_signals = {} # format: {symbol: {entry_price, max_gain, stop_loss, target_1, target_2}}

# List of Top 50 Coins (Verified for Binance)
WATCHLIST = [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT', 
    'DOT/USDT', 'TRX/USDT', 'LINK/USDT', 'POL/USDT', 'SHIB/USDT', 'LTC/USDT', 'BCH/USDT', 'ATOM/USDT', 
    'UNI/USDT', 'XLM/USDT', 'ETC/USDT', 'FIL/USDT', 'HBAR/USDT', 'APT/USDT', 'NEAR/USDT', 'VET/USDT', 
    'QNT/USDT', 'AAVE/USDT', 'GRT/USDT', 'ALGO/USDT', 'STX/USDT', 'EOS/USDT', 'SAND/USDT', 'THETA/USDT',
    'EGLD/USDT', 'MANA/USDT', 'AXS/USDT', 'FTM/USDT', 'FLOW/USDT', 'XTZ/USDT', 'CHZ/USDT', 'SUI/USDT',
    'ICP/USDT', 'ARB/USDT', 'OP/USDT', 'LDO/USDT', 'RENDER/USDT', 'INJ/USDT', 'IMX/USDT', 'GALA/USDT', 
    'SNX/USDT', 'CRV/USDT'
]

scheduler = AsyncIOScheduler()

def format_notification(signal, lang='en'):
    """
    Formats the notification message based on language.
    """
    symbol = signal['symbol']
    score = signal['score']
    status = signal['status']
    entry = signal['trade_setup']['entry_zone']
    tp1 = signal['trade_setup']['target_1']
    tp2 = signal['trade_setup']['target_2']
    # User requested to remove Stop Loss
    
    if lang == 'ar':
        # Arabic Translation - Recommendation Style
        title = f"� توصية شراء: {symbol}"
        body = (
            f"نرى فرصة ممتازة لشراء {symbol} 🚀\n"
            f"💰 منطقة الدخول: {entry}\n\n"
            f"🎯 الأهداف المتوقعة:\n"
            f"1️⃣ {tp1:.4f}\n"
            f"2️⃣ {tp2:.4f}\n\n"
            f"📊 قوة التوصية: {score}/100"
        )
    else:
        # English Default - Recommendation Style
        title = f"� Buy Recommendation: {symbol}"
        body = (
            f"Great opportunity to buy {symbol} 🚀\n"
            f"💰 Entry Zone: {entry}\n\n"
            f"🎯 Targets:\n"
            f"1️⃣ {tp1:.4f}\n"
            f"2️⃣ {tp2:.4f}\n\n"
            f"📊 Confidence: {score}/100"
        )
    
    return title, body

async def run_market_scan():
    """
    Runs analysis on all coins in WATCHLIST.
    """
    print("🔄 Running Market Scan...")
    global latest_signals
    global active_signals
    new_signals = []
    
    # 1. CHECK BITCOIN TREND FIRST (Market Correlation)
    btc_trend = "NEUTRAL"
    try:
        btc_df = await fetch_ohlcv('BTC/USDT', '1h', limit=100)
        if not btc_df.empty:
            btc_df = calculate_indicators(btc_df)
            btc_last = btc_df.iloc[-1]
            if btc_last['close'] > btc_last['EMA_200']:
                btc_trend = "BULLISH"
            elif btc_last['close'] < btc_last['EMA_200']:
                btc_trend = "BEARISH"
        print(f"📉 Market Sentiment (BTC): {btc_trend}")
    except Exception as e:
        print(f"⚠️ Failed to fetch BTC trend: {e}")

    for symbol in WATCHLIST:
        # Fetch Data (Fetch more to ensure EMA200 is valid)
        df = await fetch_ohlcv(symbol, '1h', limit=500)
        if df.empty:
            continue
        
        # Get Current Price for Tracking
        current_price = df.iloc[-1]['close']
        
        # --- TRACK ACTIVE SIGNALS ---
        if symbol in active_signals:
            signal = active_signals[symbol]
            entry_price = signal['entry_price']
            
            # Calculate Gain/Loss
            gain_pct = ((current_price - entry_price) / entry_price) * 100
            
            # Update Max Gain
            if gain_pct > signal['max_gain']:
                signal['max_gain'] = gain_pct
            
            # Check for Take Profit / Stop Loss Events
            if current_price >= signal['target_1'] and not signal.get('tp1_hit'):
                title_en = f"🚀 TP1 HIT: {symbol}"
                body_en = f"{symbol} hit Target 1! Gain: +{gain_pct:.2f}%"
                
                title_ar = f"🚀 تم تحقيق الهدف الأول: {symbol}"
                body_ar = f"عملة {symbol} حققت الهدف الأول! الربح: +{gain_pct:.2f}%"

                print(title_en)
                print(title_ar)
                
                send_fcm_notification('signals_en', title_en, body_en)
                send_fcm_notification('signals_ar', title_ar, body_ar)
                
                signal['tp1_hit'] = True
                
            elif current_price >= signal['target_2'] and not signal.get('tp2_hit'):
                title_en = f"🚀🚀 TP2 HIT: {symbol}"
                body_en = f"{symbol} hit Target 2! Gain: +{gain_pct:.2f}%"
                
                title_ar = f"🚀🚀 تم تحقيق الهدف الثاني: {symbol}"
                body_ar = f"عملة {symbol} حققت الهدف الثاني! الربح: +{gain_pct:.2f}%"

                print(title_en)
                print(title_ar)
                
                send_fcm_notification('signals_en', title_en, body_en)
                send_fcm_notification('signals_ar', title_ar, body_ar)
                
                signal['tp2_hit'] = True
                
            elif current_price <= signal['stop_loss']:
                title_en = f"🛑 EXIT ALERT: {symbol}"
                body_en = f"{symbol} reached exit zone. Gain: {gain_pct:.2f}%"
                
                title_ar = f"🛑 تنبيه خروج: {symbol}"
                body_ar = f"عملة {symbol} وصلت لمنطقة الخروج. الربح: {gain_pct:.2f}%"

                print(title_en)
                print(title_ar)
                
                send_fcm_notification('signals_en', title_en, body_en)
                send_fcm_notification('signals_ar', title_ar, body_ar)
                
                del active_signals[symbol] # Remove from active
                continue # Skip analysis for this coin
                
            # Periodic Profit Update (e.g. every +2%)
            if gain_pct >= 2.0 and int(gain_pct) > int(signal.get('last_reported_gain', 0)):
                title_en = f"📈 UPDATE: {symbol}"
                body_en = f"{symbol} is up +{gain_pct:.2f}%"
                
                title_ar = f"📈 تحديث: {symbol}"
                body_ar = f"عملة {symbol} ارتفعت بنسبة +{gain_pct:.2f}%"

                print(title_en)
                print(title_ar)
                
                send_fcm_notification('signals_en', title_en, body_en)
                send_fcm_notification('signals_ar', title_ar, body_ar)
                
                signal['last_reported_gain'] = gain_pct

        # --- ANALYZE FOR NEW SIGNALS ---
        # Skip analysis if we already have an active trade for this symbol
        if symbol in active_signals:
            continue

        df = calculate_indicators(df)
        result = analyze_market_structure(df)
        
        if result:
            # BTC Correlation Filter
            # Don't buy if BTC is Bearish (unless the signal is exceptionally strong > 90)
            if btc_trend == "BEARISH" and result['score'] < 90:
                # print(f"⚠️ Filtered {symbol} due to Bearish BTC Market")
                continue

            signal_data = {
                "symbol": symbol,
                **result
            }
            # Only keep Strong or Medium signals
            if result['score'] >= 30:
                new_signals.append(signal_data)
                
                # Check if this is a NEW signal to notify (Mock notification)
                # Generate Bilingual Content
                title_en, body_en = format_notification(signal_data, 'en')
                title_ar, body_ar = format_notification(signal_data, 'ar')
                
                print(f"🔔 [EN] {title_en}")
                print(body_en)
                print("-" * 20)
                print(f"🔔 [AR] {title_ar}")
                print(body_ar)
                print("=" * 40)
                
                send_fcm_notification('signals_en', title_en, body_en)
                send_fcm_notification('signals_ar', title_ar, body_ar)
                
                # Add to history for tracking
                signal_history.append(signal_data)
                
                # Add to Active Signals for Tracking
                active_signals[symbol] = {
                    "entry_price": result['price'],
                    "stop_loss": result['trade_setup']['stop_loss'],
                    "target_1": result['trade_setup']['target_1'],
                    "target_2": result['trade_setup']['target_2'],
                    "max_gain": 0.0,
                    "tp1_hit": False,
                    "tp2_hit": False
                }
    
    # Update latest signals list
    latest_signals = sorted(new_signals, key=lambda x: x['score'], reverse=True)
    print("✅ Scan Complete.")

@app.on_event("startup")
async def start_scheduler():
    scheduler.add_job(run_market_scan, 'interval', minutes=20) # Run every 20 minutes as requested
    scheduler.start()
    # Run one scan immediately on startup
    asyncio.create_task(run_market_scan())

@app.get("/")
def home():
    return {"message": "Crypto Signals Backend is Running"}

@app.get("/signals")
def get_signals():
    """
    Returns the current active signals.
    """
    return {
        "count": len(latest_signals),
        "signals": latest_signals
    }

@app.get("/history")
def get_history():
    """
    Returns the history of all signals generated.
    """
    return {
        "count": len(signal_history),
        "history": signal_history[-50:] # Return last 50
    }

@app.post("/scan")
async def trigger_scan(background_tasks: BackgroundTasks):
    """
    Manually trigger a scan (useful for testing).
    """
    background_tasks.add_task(run_market_scan)
    return {"message": "Scan started in background"}

from datetime import datetime, timezone

def get_time_ago(timestamp_str):
    try:
        # Parse timestamp (assuming ISO format from isoformat())
        # If timestamp is already a datetime object, use it directly
        if isinstance(timestamp_str, str):
            signal_time = datetime.fromisoformat(timestamp_str)
        else:
            signal_time = timestamp_str
            
        now = datetime.now(timezone.utc)
        # Ensure signal_time is timezone-aware
        if signal_time.tzinfo is None:
            signal_time = signal_time.replace(tzinfo=timezone.utc)
            
        diff = now - signal_time
        minutes = int(diff.total_seconds() / 60)
        
        if minutes < 1:
            return "Just now"
        elif minutes < 60:
            return f"{minutes}m ago"
        elif minutes < 1440:
            return f"{minutes // 60}h ago"
        else:
            return f"{minutes // 1440}d ago"
    except Exception as e:
        print(f"Error calculating time_ago: {e}")
        return "Just now"

@app.get("/android/signals")
def get_android_signals():
    """
    Optimized endpoint for Android App.
    Returns signals with formatted strings ready for UI display.
    """
    android_signals = []
    for s in latest_signals:
        coin = s['symbol'].split('/')[0]
        image_url = f"https://lcw.nyc3.cdn.digitaloceanspaces.com/production/currencies/64/{coin.lower()}.png"

        android_signals.append({
            "id": f"{s['symbol']}-{s['timestamp']}",
            "coin": coin,
            "pair": s['symbol'],
            "price": f"${s['price']:.2f}",
            "image_url": image_url,
            "score_value": s['score'],
            "score_color": "#00C853" if s['score'] >= 80 else "#FFAB00", # Green for Strong, Amber for Medium
            "status_text": s['status'],
            "entry": s['trade_setup']['entry_zone'],
            "targets": f"TP1: {s['trade_setup']['target_1']:.2f} | TP2: {s['trade_setup']['target_2']:.2f}",
            "stop_loss": f"Exit: {s['trade_setup']['stop_loss']:.2f}",
            "time_ago": get_time_ago(s['timestamp'])
        })
    
    return {
        "status": "success",
        "data": android_signals
    }

@app.post("/test-notification")
def test_notification():
    """
    Sends a test notification to check FCM configuration.
    """
    if not FCM_ENABLED:
        return {
            "status": "error",
            "message": "FCM is NOT enabled. Please place 'serviceAccountKey.json' in the backend folder and restart the server."
        }
        
    send_fcm_notification('signals_en', 'Test Notification', 'This is a test message from your Crypto Server (English).')
    send_fcm_notification('signals_ar', 'إشعار تجريبي', 'هذه رسالة تجريبية من سيرفر الكريبتو الخاص بك (عربي).')
    return {"status": "success", "message": "Test notifications sent to signals_en and signals_ar"}