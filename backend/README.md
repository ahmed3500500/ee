# Crypto Signals Backend (MVP)

## Requirements
- Python 3.8+
- Virtual Environment (Recommended)

## Installation
1. Create venv: `python -m venv venv`
2. Activate: `.\venv\Scripts\activate` (Windows)
3. Install deps: `pip install -r requirements.txt`

## Running
1. Start Server: `uvicorn main:app --reload`
2. API Docs: `http://127.0.0.1:8000/docs`
3. Check Signals: `http://127.0.0.1:8000/signals`

## Features
- Fetches OHLCV data (KuCoin/OKX or Mock if blocked).
- Analyzes Trend (EMA) and Momentum (RSI).
- Scores opportunities (0-100).
- Hourly Scheduler.
