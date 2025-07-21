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

# Constants
INDIA_TZ = pytz.timezone("Asia/Kolkata")
INDIAN_HOLIDAYS = holidays.country_holidays("IN")

def is_trading_day(date):
    return date.weekday() < 5 and date not in INDIAN_HOLIDAYS

def get_last_trading_day(start_date=None):
    date = start_date or datetime.now(INDIA_TZ).date()
    while not is_trading_day(date):
        date -= timedelta(days=1)
    return date

def get_session_data(ticker):
    today = get_last_trading_day()
    prev_day = get_last_trading_day(today - timedelta(days=1))
    results = {}

    try:
        df = yf.Ticker(ticker).history(start=str(today), interval="1m")
        p915 = df.loc[f"{today} 09:15:00"]['Close']
        p919 = df.loc[f"{today} 09:19:00"]['Close']
        results.update({
            "morning_date": str(today),
            "p915": round(p915, 2),
            "p919": round(p919, 2),
            "morning_change": round((p919 - p915) / p915 * 100, 2)
        })
    except:
        results.update({"p915": None, "p919": None, "morning_change": None, "morning_date": str(today)})

    try:
        df = yf.Ticker(ticker).history(start=str(prev_day), end=str(prev_day + timedelta(days=1)), interval="1m")
        p315 = df.loc[f"{prev_day} 15:15:00"]['Close']
        p329 = df.loc[f"{prev_day} 15:29:00"]['Close']
        results.update({
            "closing_date": str(prev_day),
            "p315": round(p315, 2),
            "p329": round(p329, 2),
            "closing_change": round((p329 - p315) / p315 * 100, 2)
        })
    except:
        results.update({"p315": None, "p329": None, "closing_change": None, "closing_date": str(prev_day)})

    results["ticker"] = ticker
    return results

# Flask App
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

from concurrent.futures import ThreadPoolExecutor, as_completed

@app.route('/analyze')
def analyze():
    results = []

    # Use a thread pool with 20 workers (can adjust based on system/network)
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ticker = {executor.submit(get_session_data, ticker): ticker for ticker in TICKERS}
        for future in as_completed(future_to_ticker):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Error with {future_to_ticker[future]}: {e}")
                
    results.sort(key=lambda x: x['morning_change'] if x['morning_change'] is not None else -999, reverse=True)
    return jsonify(results)

@app.route('/gainers')
def gainers():
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(get_session_data, t) for t in TICKERS]
        results = [f.result() for f in futures]

    # ✅ Filter: morning ≥ 2% and abs(closing) < 2%
    filtered = [
        r for r in results
        if r["morning_change"] is not None and r["morning_change"] >= 2
        and (r["closing_change"] is None or abs(r["closing_change"]) < 2)
    ]

    return jsonify(filtered)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

