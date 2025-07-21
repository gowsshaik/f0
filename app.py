import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import holidays
from flask import Flask, request, jsonify, render_template

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

IST = pytz.timezone('Asia/Kolkata')

# Helper functions

def get_previous_n_working_days(n):
    today = datetime.now(IST).date()
    days = []
    while len(days) < n:
        today -= timedelta(days=1)
        if today.weekday() < 5:
            days.append(today)
    return days

def get_data(ticker):
    try:
        now = datetime.now(IST)
        prev_days = get_previous_n_working_days(3)
        today = now.date()
        yesterday = prev_days[0]
        day_before = prev_days[1]

        hist = yf.Ticker(ticker).history(period="5d", interval="1m")

        def extract_price(date, time_str):
            dt = f"{date} {time_str}"
            return round(hist.loc[dt]['Close'], 2) if dt in hist.index else None

        p915 = extract_price(today, '09:15:00')
        p919 = extract_price(today, '09:19:00')

        p315 = extract_price(day_before, '15:15:00')
        p329 = extract_price(day_before, '15:29:00')

        morning_change = round(((p919 - p915)/p915)*100, 2) if p915 and p919 else None
        closing_change = round(((p329 - p315)/p315)*100, 2) if p315 and p329 else None

        return {
            "ticker": ticker,
            "morning_date": str(today),
            "p915": p915,
            "p919": p919,
            "morning_change": morning_change,
            "closing_date": str(day_before),
            "p315": p315,
            "p329": p329,
            "closing_change": closing_change
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "error": str(e)
        }

# Multithread wrapper
def get_all_tickers_data():
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(get_data, tickers_list))
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

