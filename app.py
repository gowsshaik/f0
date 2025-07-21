import yfinance as yf
import pandas as pd
from flask import Flask, jsonify, render_template
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import pytz
import holidays
app = Flask(__name__)
# Ticker List
TICKERS = [
    "360ONE.NS", "ABB.NS", "ACC.NS", "APLAPOLLO.NS", "ADANIENT.NS", "ADANIPORTS.NS", "AMBUJACEM.NS",
    "AMBER.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "ASTRAL.NS", "AUBANK.NS", "AUROPHARMA.NS",
    "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BALKRISIND.NS", "BANDHANBNK.NS",
    "BANKBARODA.NS", "BATAINDIA.NS", "BEL.NS", "BHARATFORG.NS", "BHARTIARTL.NS", "BIOCON.NS",
    "BOSCHLTD.NS", "BRITANNIA.NS", "CADILAHC.NS", "CANBK.NS", "CASTROLIND.NS", "CHAMBLFERT.NS",
    "CHOLAFIN.NS", "CIPLA.NS", "CUB.NS", "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", "CONCOR.NS",
    "COROMANDEL.NS", "CROMPTON.NS", "CUMMINSIND.NS", "DALBHARAT.NS", "DLF.NS", "DIXON.NS",
    "DIVISLAB.NS", "LALPATHLAB.NS", "DRREDDY.NS", "EICHERMOT.NS", "ESCORTS.NS", "FEDERALBNK.NS",
    "FORTIS.NS", "GAIL.NS", "GLAND.NS", "GLENMARK.NS", "GODREJCP.NS", "GODREJPROP.NS", "GRANULES.NS",
    "GRASIM.NS", "GUJGASLTD.NS", "GSPL.NS", "HCLTECH.NS", "HDFCAMC.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HAL.NS", "HINDCOPPER.NS", "HINDPETRO.NS", "HINDUNILVR.NS",
    "HINDZINC.NS", "ICICIBANK.NS", "ICICIGI.NS", "ICICIPRULI.NS", "IDFCFIRSTB.NS", "IEX.NS", "IGL.NS",
    "INDIACEM.NS", "INDIAMART.NS", "INDHOTEL.NS", "IOC.NS", "INDUSINDBK.NS", "NAUKRI.NS", "INFY.NS",
    "INTELLECT.NS", "INDIGO.NS", "IPCALAB.NS", "IRCTC.NS", "ITC.NS", "JKCEMENT.NS", "JINDALSTEL.NS",
    "JSWSTEEL.NS", "JUBLFOOD.NS", "KAJARIACER.NS", "KANSAINER.NS", "KEC.NS", "KOTAKBANK.NS", "L&TFH.NS",
    "LTTS.NS", "LICHSGFIN.NS", "LT.NS", "LUPIN.NS", "MANAPPURAM.NS", "MARICO.NS", "MARUTI.NS",
    "MCDOWELL-N.NS", "MCX.NS", "METROPOLIS.NS", "MFSL.NS", "MGL.NS", "M&M.NS", "M&MFIN.NS",
    "MNGL.NS", "MPHASIS.NS", "MRF.NS", "MUTHOOTFIN.NS", "NAM-INDIA.NS", "NATIONALUM.NS",
    "NAVINFLUOR.NS", "NCC.NS", "NESTLEIND.NS", "NMDC.NS", "NTPC.NS", "OBEROIRLTY.NS", "OFSS.NS",
    "ONGC.NS", "PAGEIND.NS", "PEL.NS", "PERSISTENT.NS", "PETRONET.NS", "PFC.NS", "PIDILITIND.NS",
    "PIIND.NS", "PNB.NS", "POLYCAB.NS", "POWERGRID.NS", "PRAJIND.NS", "PRESTIGE.NS", "PVRINOX.NS",
    "RAMCOCEM.NS", "RBLBANK.NS", "RECLTD.NS", "RELIANCE.NS", "SAIL.NS", "SBICARD.NS", "SBILIFE.NS",
    "SBIN.NS", "SCHAEFFLER.NS", "SHREECEM.NS", "SHRIRAMFIN.NS", "SIEMENS.NS", "SRF.NS", "SRTRANSFIN.NS",
    "SUNPHARMA.NS", "SUNTV.NS", "SUPRAJIT.NS", "SYNGENE.NS", "TATACHEM.NS", "TATACOMM.NS",
    "TATACONSUM.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS",
    "TITAN.NS", "TORNTPHARM.NS", "TORNTPOWER.NS", "TRENT.NS", "TVSMOTOR.NS", "UBL.NS", "ULTRACEMCO.NS",
    "UNIONBANK.NS", "UPL.NS", "VEDL.NS", "VOLTAS.NS", "WHIRLPOOL.NS", "WIPRO.NS", "ZEEL.NS"
]
# TICKERS = ["PVRINOX.NS"]
IST = pytz.timezone('Asia/Kolkata')
IN_HOLIDAYS = holidays.India()

# Helper functions

def get_last_two_working_days():
    today = datetime.now(IST).date()
    # Go back from today until we find 2 valid market days
    days = []
    while len(days) < 2:
        if today.weekday() < 5 and today not in IN_HOLIDAYS:
            days.insert(0, today)
        today -= timedelta(days=1)
    return days  # [previous_working_day, latest_working_day]


def get_data(ticker):
    try:
        now = datetime.now(IST)
        previous_day, latest_day = get_last_two_working_days()
        hist = yf.Ticker(ticker).history(period="5d", interval="1m")
        def extract_open_price(date, time_str):
            dt = f"{date} {time_str}"
            return round(hist.loc[dt]['Open'], 2) if dt in hist.index else None
        def extract_close_price(date, time_str):
            dt = f"{date} {time_str}"
            return round(hist.loc[dt]['Close'], 2) if dt in hist.index else None
        def extract_day_open(date):
            opens = hist.between_time('09:15', '09:45')
            day_data = opens[opens.index.date == date]
            return round(day_data.iloc[0]['Open'], 2) if not day_data.empty else None

        def extract_day_close(date):
            closes = hist.between_time('15:25', '15:30')
            day_data = closes[closes.index.date == date]
            return round(day_data.iloc[-1]['Close'], 2) if not day_data.empty else None

        p915 = extract_open_price(latest_day, '09:15:00')
        p919 = extract_close_price(latest_day, '09:19:00')

        p315 = extract_open_price(previous_day, '15:15:00')
        p329 = extract_close_price(previous_day, '15:29:00')

        # Additional values
        open_price = extract_day_open(latest_day)
        prev_close = extract_day_close(previous_day)
        current_price = extract_close_price(latest_day, '09:18:00')  # You can change this

        morning_change = round(((p919 - p915)/p915)*100, 2) if p915 and p919 else None
        closing_change = round(((p329 - p315)/p315)*100, 2) if p315 and p329 else None

        return {
            "ticker": ticker,
            "morning_date": str(latest_day),
            "p915": p915,
            "p919": p919,
            "morning_change": morning_change,
            "closing_date": str(previous_day),
            "p315": p315,
            "p329": p329,
            "closing_change": closing_change,
            "open_price": open_price,
            "prev_day_close": prev_close,
            "current_price": current_price
        }

    except Exception as e:
        return {
            "ticker": ticker,
            "error": str(e)
        }

# Multithread wrapper
def get_all_tickers_data():
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(get_data, TICKERS))
    return results

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze")
def analyze():
    data = get_all_tickers_data()
    sorted_data = sorted(data, key=lambda x: x.get("morning_change") or 0, reverse=True)
    return jsonify(sorted_data)

@app.route("/gainers")
def gainers():
    data = get_all_tickers_data()
    filtered = [d for d in data if d.get("morning_change") and d["morning_change"] >= 2 \
                and (d.get("closing_change") is None or abs(d["closing_change"]) < 2)]
    sorted_filtered = sorted(filtered, key=lambda x: x.get("morning_change") or 0, reverse=True)
    return jsonify(sorted_filtered)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
