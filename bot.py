import requests
import time
from datetime import datetime

TOKEN = "8563282168:AAEYircnD2OpqGBRZxrrbMtUiA1K9tz1XQo"
CHAT_ID = "7015685218"

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        print("Alert sent")
    except Exception as e:
        print(f"Error: {e}")

def get_spurt_stocks():
    try:
        s = requests.Session()
        s.get("https://www.nseindia.com",
              headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r = s.get("https://www.nseindia.com/api/live-analysis-volume-gainers",
                  headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = r.json()
        stocks = []
        for item in data.get("data", [])[:4]:
            stocks.append(item["symbol"])
        return stocks
    except Exception as e:
        print(f"Spurt error: {e}")
        return []

def check_signal(symbol):
    try:
        s = requests.Session()
        s.get("https://www.nseindia.com",
              headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r = s.get(f"https://www.nseindia.com/api/quote-derivative?symbol={symbol}",
                  headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = r.json()
        fut = None
        for item in data.get("stocks", []):
            if item.get("metadata", {}).get("instrumentType") == "Stock Futures":
                fut = item
                break
        if not fut:
            return
        price_chg = fut["metadata"].get("change", 0)
        oi_chg = fut["marketDeptOrderBook"]["tradeInfo"].get("changeinOpenInterest", 0)
        if price_chg > 0 and oi_chg > 0:
            signal = "BUY CALL"
            reason = "Long Buildup"
        elif price_chg < 0 and oi_chg > 0:
            signal = "BUY PUT"
            reason = "Short Buildup"
        elif price_chg < 0 and oi_chg < 0:
            signal = "BUY PUT"
            reason = "Long Unwinding"
        else:
            return
        msg = f"TRADE ALERT\nStock: {symbol}\nSignal: {signal}\nReason: {reason}\nWait for 15 min ORB breakout!"
        send_alert(msg)
    except Exception as e:
        print(f"{symbol} error: {e}")

def run_scan(session):
    send_alert(f"{session} Scan Starting...")
    stocks = get_spurt_stocks()
    if not stocks:
        send_alert("NSE data not available.")
        return
    send_alert(f"Top 4 Stocks: {', '.join(stocks)}")
    for s in stocks:
        check_signal(s)
        time.sleep(3)

run_scan("Manual Test")
