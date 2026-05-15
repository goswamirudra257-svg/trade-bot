import requests
import time
from datetime import datetime

TOKEN = "8563282168:AAEYircnD2OpqGBRZxrrbMtUiA1K9tz1XQo"
CHAT_ID = "7015685218"

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        print(f"Alert sent: {r.status_code}")
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

def get_oi_signal(symbol):
    try:
        s = requests.Session()
        s.get("https://www.nseindia.com",
              headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r = s.get(f"https://www.nseindia.com/api/quote-derivative?symbol={symbol}",
                  headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = r.json()

        # Options OI data
        call_oi = 0
        put_oi = 0
        call_oi_chg = 0
        put_oi_chg = 0
        price_chg = 0

        # Get price change
        price_chg = data.get("underlyingValue", 0)
        last_price = data.get("underlyingValue", 0)

        # Get underlying price change %
        info = data.get("info", {})
        price_chg = info.get("change", 0)

        # Sum all CE and PE OI
        for item in data.get("stocks", []):
            meta = item.get("metadata", {})
            inst = meta.get("instrumentType", "")
            oi = item.get("marketDeptOrderBook", {}).get("tradeInfo", {}).get("openInterest", 0)
            oi_chg = item.get("marketDeptOrderBook", {}).get("tradeInfo", {}).get("changeinOpenInterest", 0)

            if "Call" in inst or "CE" in str(meta.get("optionType", "")):
                call_oi += oi
                call_oi_chg += oi_chg
            elif "Put" in inst or "PE" in str(meta.get("optionType", "")):
                put_oi += oi
                put_oi_chg += oi_chg

        print(f"{symbol}: Price chg={price_chg}, Call OI chg={call_oi_chg}, Put OI chg={put_oi_chg}")

        # Strategy conditions
        if price_chg > 0 and call_oi_chg > 0:
            return ("BUY CALL", "Price Gainer + Call OI Gainer = Long Buildup")
        elif price_chg < 0 and put_oi_chg > 0:
            return ("BUY PUT", "Price Loser + Put OI Gainer = Short Buildup")
        elif price_chg < 0 and call_oi_chg < 0:
            return ("BUY PUT", "Price Loser + Call OI Loser = Long Unwinding")
        else:
            return None

    except Exception as e:
        print(f"{symbol} OI error: {e}")
        return None

def run_scan(session):
    now = datetime.now().strftime("%H:%M")

    if "Morning" in session:
        window = "Entry: 9:31 - 10:45 | 15 Min ORB"
    elif "Afternoon" in session:
        window = "Entry: 1:31 - 2:30 | 15 Min ORB"
    else:
        window = "Manual Test Mode"

    send_alert(f"SCAN START - {session}\nTime: {now}")

    stocks = get_spurt_stocks()
    if not stocks:
        send_alert("NSE data not available. Check manually.")
        return

    send_alert(f"Top 4 NSE Spurt Stocks:\n" + "\n".join(stocks))

    found = False
    for symbol in stocks:
        result = get_oi_signal(symbol)
        time.sleep(3)

        if result:
            signal, reason = result
            found = True
            msg = f"""TRADE ALERT
Stock: {symbol}
Signal: {signal}
Reason: {reason}
{window}
Target: 1:2
Trailing SL: Every 1:1"""
            send_alert(msg)

    if not found:
        send_alert("No OI signal found in top 4 stocks.")

now = datetime.now()
hour = now.hour
minute = now.minute

if hour == 9 and minute == 20:
    run_scan("Morning 9:20")
elif hour == 13 and minute == 20:
    run_scan("Afternoon 1:20")
else:
    run_scan("Manual Test")
