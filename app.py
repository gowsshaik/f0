import yfinance as yf
import pandas as pd
from flask import Flask, jsonify, render_template, request
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
    "UNIONBANK.NS", "UNIONBANK.NS", "UPL.NS", "VEDL.NS", "VOLTAS.NS", "WHIRLPOOL.NS", "WIPRO.NS", "ZEEL.NS"
]
# TICKERS=['PVRINOX.NS']
IST = pytz.timezone('Asia/Kolkata')
IN_HOLIDAYS = holidays.India()

# Helper functions
def get_last_two_working_days():
    today = datetime.now(IST).date()
    days = []
    while len(days) < 2:
        if today.weekday() < 5 and today not in IN_HOLIDAYS:
            days.insert(0, today)
        today -= timedelta(days=1)
    return days

def is_market_day(date_obj):
    """Check if given date is a valid market day"""
    return date_obj.weekday() < 5 and date_obj not in IN_HOLIDAYS

def get_previous_market_day(date_obj):
    """Get the previous market day from given date"""
    prev_date = date_obj - timedelta(days=1)
    while not is_market_day(prev_date):
        prev_date -= timedelta(days=1)
    return prev_date

def get_data_for_date(ticker, target_date):
    """Get stock data for a specific date - OPTIMIZED VERSION"""
    try:
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # Check if target date is a market day
        if not is_market_day(target_date_obj):
            return {
                "ticker": ticker,
                "error": f"Market closed on {target_date} (weekend/holiday)"
            }
        
        # Get previous market day
        previous_day = get_previous_market_day(target_date_obj)
        
        # Fetch historical data for only the 2 required days
        # Start from previous day, end day after target date
        start_date = previous_day
        end_date = target_date_obj + timedelta(days=1)
        print(f"Fetching data from {start_date} to {end_date}")
        
        hist = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="1m")
        
        if hist.empty:
            return {
                "ticker": ticker,
                "error": f"No data available for {target_date}"
            }
        
        def extract_open_price(date, time_str):
            dt = f"{date} {time_str}"
            return round(hist.loc[dt]['Open'], 2) if dt in hist.index else None
        
        def extract_close_price(date, time_str):
            dt = f"{date} {time_str}"
            return round(hist.loc[dt]['Close'], 2) if dt in hist.index else None
        
        def extract_day_open(date):
            day_data = hist[hist.index.date == date]
            if not day_data.empty:
                opens = day_data.between_time('09:15', '09:45')
                return round(opens.iloc[0]['Open'], 2) if not opens.empty else None
            return None

        def extract_day_close(date):
            day_data = hist[hist.index.date == date]
            if not day_data.empty:
                closes = day_data.between_time('15:25', '15:30')
                return round(closes.iloc[-1]['Close'], 2) if not closes.empty else None
            return None

        # Extract prices for target date (morning session)
        p915 = extract_open_price(target_date_obj, '09:15:00')
        p919 = extract_close_price(target_date_obj, '09:19:00')

        # Extract prices for previous market day (closing session)
        p315 = extract_open_price(previous_day, '15:15:00')
        p329 = extract_close_price(previous_day, '15:29:00')

        # Additional values
        open_price = extract_day_open(target_date_obj)
        prev_close = extract_day_close(previous_day)
        current_price = extract_close_price(target_date_obj, '09:18:00')

        # Calculate changes
        morning_change = round(((p919 - p915)/p915)*100, 2) if p915 and p919 else None
        closing_change = round(((p329 - p315)/p315)*100, 2) if p315 and p329 else None

        return {
            "ticker": ticker,
            "morning_date": str(target_date_obj),
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

def execute_mock_trade_analysis(ticker, date, time, investment_amount):
    """Execute mock trade analysis with minute-by-minute tracking"""
    try:
        target_date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Check if target date is a market day
        if not is_market_day(target_date_obj):
            return {
                "error": f"Market closed on {date} (weekend/holiday)"
            }
        
        # Parse entry time
        entry_hour, entry_minute = map(int, time.split(':'))
        entry_time_obj = datetime.combine(target_date_obj, datetime.min.time().replace(hour=entry_hour, minute=entry_minute))
        
        # Fetch minute-level data for the trading day
        start_date = target_date_obj
        end_date = target_date_obj + timedelta(days=1)
        
        hist = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="1m")
        
        if hist.empty:
            return {
                "error": f"No trading data available for {ticker} on {date}"
            }
        
        # Filter data for market hours (9:15 AM to 3:30 PM)
        market_data = hist.between_time('09:15', '15:30')
        market_data = market_data[market_data.index.date == target_date_obj]
        
        if market_data.empty:
            return {
                "error": f"No market data available for {ticker} on {date}"
            }
        
        # Find entry price at specified time
        entry_time_str = f"{target_date_obj} {time}:00"
        entry_price = None
        
        # Find the closest available time to entry time
        for idx in market_data.index:
            if idx.strftime('%H:%M') >= time:
                entry_price = round(market_data.loc[idx]['Open'], 2)
                actual_entry_time = idx.strftime('%H:%M')
                break
        
        if entry_price is None:
            return {
                "error": f"No price data available at {time} on {date}"
            }
        
        # Calculate shares that can be bought
        shares_bought = int(investment_amount / entry_price)
        
        if shares_bought == 0:
            return {
                "error": f"Investment amount too small. Cannot buy even 1 share at ₹{entry_price}"
            }
        
        # Track minute-by-minute prices after entry
        minute_prices = []
        max_profit = 0
        best_exit_price = entry_price
        best_exit_time = actual_entry_time
        
        # Only consider prices after entry time
        post_entry_data = market_data[market_data.index.strftime('%H:%M') >= time]
        
        for idx in post_entry_data.index:
            current_price = round(market_data.loc[idx]['Close'], 2)
            current_time = idx.strftime('%H:%M')
            
            # Calculate profit for this minute
            profit_per_share = current_price - entry_price
            total_profit = profit_per_share * shares_bought
            
            minute_prices.append({
                "time": current_time,
                "price": current_price,
                "profit": round(total_profit, 2)
            })
            
            # Track maximum profit
            if total_profit > max_profit:
                max_profit = total_profit
                best_exit_price = current_price
                best_exit_time = current_time
        
        return {
            "ticker": ticker,
            "date": date,
            "entry_time": actual_entry_time,
            "entry_price": entry_price,
            "exit_price": best_exit_price,
            "best_exit_time": best_exit_time,
            "max_profit": round(max_profit, 2),
            "investment_amount": investment_amount,
            "shares_bought": shares_bought,
            "return_percentage": round((max_profit / investment_amount) * 100, 2),
            "minute_prices": minute_prices
        }
        
    except Exception as e:
        return {
            "error": str(e)
        }

def get_data(ticker):
    """Original get_data function for current analysis"""
    try:
        now = datetime.now(IST)
        previous_day, latest_day = get_last_two_working_days()
        hist = yf.Ticker(ticker).history(period="7d", interval="1m")
        
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
        current_price = extract_close_price(latest_day, '09:18:00')

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

# Multithread wrapper for current analysis
def get_all_tickers_data():
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(get_data, TICKERS))
    return results

# Multithread wrapper for date-specific analysis
def get_all_tickers_data_for_date(target_date):
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(lambda ticker: get_data_for_date(ticker, target_date), TICKERS))
    return results

# Routes
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

# NEW ENDPOINTS FOR TEST TAB

@app.route("/analyze-date")
def analyze_date():
    """Analyze all tickers for a specific date"""
    target_date = request.args.get('date')
    
    if not target_date:
        return jsonify({"error": "Date parameter is required"}), 400
    
    try:
        # Validate date format
        datetime.strptime(target_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    try:
        data = get_all_tickers_data_for_date(target_date)
        # Sort by morning change (highest first)
        sorted_data = sorted(data, key=lambda x: x.get("morning_change") or -999, reverse=True)
        return jsonify(sorted_data)
    except Exception as e:
        return jsonify({"error": f"Failed to analyze data for {target_date}: {str(e)}"}), 500

@app.route("/mock-trade", methods=['POST'])
def mock_trade():
    """Execute mock trade analysis"""
    try:
        data = request.get_json()
        
        # Validate required parameters
        required_fields = ['ticker', 'date', 'time', 'investment_amount']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        ticker = data['ticker']
        date = data['date']
        time = data['time']
        investment_amount = float(data['investment_amount'])
        
        # Validate inputs
        if investment_amount <= 0:
            return jsonify({"error": "Investment amount must be positive"}), 400
        
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        try:
            datetime.strptime(time, '%H:%M')
        except ValueError:
            return jsonify({"error": "Invalid time format. Use HH:MM"}), 400
        
        # Validate time is within market hours
        hour, minute = map(int, time.split(':'))
        if hour < 9 or (hour == 9 and minute < 15) or hour > 15 or (hour == 15 and minute > 30):
            return jsonify({"error": "Time must be within market hours (09:15 - 15:30)"}), 400
        
        # Execute mock trade
        result = execute_mock_trade_analysis(ticker, date, time, investment_amount)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({"error": f"Invalid investment amount: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Mock trade failed: {str(e)}"}), 500

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
