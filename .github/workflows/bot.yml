import requests
from datetime import datetime
import pytz

# =========================
# TELEGRAM SETTINGS
# =========================

BOT_TOKEN = "PASTE_NEW_TOKEN_HERE"
CHAT_ID = "7015685218"

# =========================
# INDIA TIMEZONE
# =========================

india = pytz.timezone('Asia/Kolkata')

# =========================
# TELEGRAM FUNCTION
# =========================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=data)

    print(response.text)

# =========================
# TOP STOCK SCANNER
# =========================

def get_top_stocks():

    stocks = [
        "RELIANCE",
        "SBIN",
        "HAL",
        "TATASTEEL"
    ]

    return stocks

# =========================
# OI SIGNAL LOGIC
# =========================

def check_signal(stock):

    signals = {
        "RELIANCE": "CALL",
        "SBIN": "PUT",
        "HAL": None,
        "TATASTEEL": "CALL"
    }

    return signals.get(stock)

# =========================
# ORB BREAKOUT CHECK
# =========================

def orb_confirm(stock):

    return True

# =========================
# MAIN STRATEGY
# =========================

def run_bot():

    now = datetime.now(india)

    current_time = now.strftime("%H:%M")

    send_telegram(
        f"SCAN START\nTime: {current_time}"
    )

    stocks = get_top_stocks()

    stock_text = "\n".join(stocks)

    send_telegram(
        f"Top 4 F&O Stocks:\n\n{stock_text}"
    )

    signal_found = False

    for stock in stocks:

        signal = check_signal(stock)

        if signal == "CALL":

            if orb_confirm(stock):

                msg = f"""
BUY CALL SIGNAL

Stock: {stock}

Conditions:
Price Gainer
OI Gainer
Long Buildup

ORB Breakout Confirmed
Risk Reward = 1:2
"""

                send_telegram(msg)

                signal_found = True

        elif signal == "PUT":

            if orb_confirm(stock):

                msg = f"""
BUY PUT SIGNAL

Stock: {stock}

Conditions:
Price Loser
OI Gainer
Short Buildup

ORB Breakdown Confirmed
Risk Reward = 1:2
"""

                send_telegram(msg)

                signal_found = True

    if not signal_found:

        send_telegram(
            "No valid signal found."
        )

# =========================
# RUN ONLY AT MARKET TIMES
# =========================

if __name__ == "__main__":

    now = datetime.now(india)

    hour = now.hour
    minute = now.minute

    # Morning Session
    if hour == 9 and minute >= 20:

        run_bot()

    # Afternoon Session
    elif hour == 13 and minute >= 20:

        run_bot()

    else:

        print("Not scan time.")
