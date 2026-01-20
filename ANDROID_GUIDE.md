# Crypto Signals - Android Implementation Guide

## 1. API Endpoints
Base URL: `http://YOUR_SERVER_IP:8000`

### Get Active Signals
- **GET** `/signals`
- Returns list of current opportunities.
- **Response Format:**
```json
{
  "count": 5,
  "signals": [
    {
      "symbol": "BTC/USDT",
      "price": 52000.50,
      "score": 85,
      "status": "STRONG",
      "trade_setup": {
        "entry_zone": "52000 - 52100",
        "stop_loss": 51500,
        "target_1": 53000,
        "target_2": 54500
      },
      "reasons": ["Uptrend", "RSI Healthy"],
      "timestamp": "2026-01-20T10:00:00"
    }
  ]
}
```

## 2. Kotlin Data Models
Create these data classes in your Android project:

```kotlin
data class SignalResponse(
    val count: Int,
    val signals: List<Signal>
)

data class Signal(
    val symbol: String,
    val price: Double,
    val score: Int,
    val status: String,
    val trade_setup: TradeSetup,
    val reasons: List<String>,
    val timestamp: String
)

data class TradeSetup(
    val entry_zone: String,
    val stop_loss: Double,
    val target_1: Double,
    val target_2: Double,
    val risk_reward_ratio: String
)
```

## 3. Retrofit Interface
```kotlin
interface CryptoApi {
    @GET("signals")
    suspend fun getSignals(): SignalResponse
}
```

## 4. Notifications (FCM)
To receive notifications, the app needs to subscribe to a topic (e.g., "signals").
The server will send push notifications when a new STRONG signal is detected.
