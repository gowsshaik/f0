import yfinance as yf
import pandas as pd
from flask import Flask, jsonify, render_template, request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import pytz
import holidays

app = Flask(__name__)

# Ticker List with Company Names and Sectors
TICKER_INFO = {
    "360ONE.NS": {"company": "360 ONE WAM Ltd", "sector": "Financial Services"},
    "ABB.NS": {"company": "ABB India Ltd", "sector": "Capital Goods"},
    "ACC.NS": {"company": "ACC Ltd", "sector": "Cement & Cement Products"},
    "APLAPOLLO.NS": {"company": "APL Apollo Tubes Ltd", "sector": "Metal Products"},
    "ADANIENT.NS": {"company": "Adani Enterprises Ltd", "sector": "Trading"},
    "ADANIPORTS.NS": {"company": "Adani Ports & Special Economic Zone Ltd", "sector": "Services"},
    "AMBUJACEM.NS": {"company": "Ambuja Cements Ltd", "sector": "Cement & Cement Products"},
    "AMBER.NS": {"company": "Amber Enterprises India Ltd", "sector": "Consumer Durables"},
    "APOLLOHOSP.NS": {"company": "Apollo Hospitals Enterprise Ltd", "sector": "Healthcare Services"},
    "ASIANPAINT.NS": {"company": "Asian Paints Ltd", "sector": "Consumer Goods"},
    "ASTRAL.NS": {"company": "Astral Ltd", "sector": "Capital Goods"},
    "AUBANK.NS": {"company": "AU Small Finance Bank Ltd", "sector": "Financial Services"},
    "AUROPHARMA.NS": {"company": "Aurobindo Pharma Ltd", "sector": "Pharmaceuticals"},
    "AXISBANK.NS": {"company": "Axis Bank Ltd", "sector": "Financial Services"},
    "BAJAJ-AUTO.NS": {"company": "Bajaj Auto Ltd", "sector": "Automobile and Auto Components"},
    "BAJFINANCE.NS": {"company": "Bajaj Finance Ltd", "sector": "Financial Services"},
    "BAJAJFINSV.NS": {"company": "Bajaj Finserv Ltd", "sector": "Financial Services"},
    "BALKRISIND.NS": {"company": "Balkrishna Industries Ltd", "sector": "Automobile and Auto Components"},
    "BANDHANBNK.NS": {"company": "Bandhan Bank Ltd", "sector": "Financial Services"},
    "BANKBARODA.NS": {"company": "Bank of Baroda", "sector": "Financial Services"},
    "BATAINDIA.NS": {"company": "Bata India Ltd", "sector": "Consumer Goods"},
    "BEL.NS": {"company": "Bharat Electronics Ltd", "sector": "Capital Goods"},
    "BHARATFORG.NS": {"company": "Bharat Forge Ltd", "sector": "Automobile and Auto Components"},
    "BHARTIARTL.NS": {"company": "Bharti Airtel Ltd", "sector": "Telecommunication"},
    "BIOCON.NS": {"company": "Biocon Ltd", "sector": "Pharmaceuticals"},
    "BOSCHLTD.NS": {"company": "Bosch Ltd", "sector": "Automobile and Auto Components"},
    "BRITANNIA.NS": {"company": "Britannia Industries Ltd", "sector": "FMCG"},
    "CADILAHC.NS": {"company": "Cadila Healthcare Ltd", "sector": "Pharmaceuticals"},
    "CANBK.NS": {"company": "Canara Bank", "sector": "Financial Services"},
    "CASTROLIND.NS": {"company": "Castrol India Ltd", "sector": "Oil Gas & Consumable Fuels"},
    "CHAMBLFERT.NS": {"company": "Chambal Fertilisers & Chemicals Ltd", "sector": "Fertilizers & Agrochemicals"},
    "CHOLAFIN.NS": {"company": "Cholamandalam Investment and Finance Company Ltd", "sector": "Financial Services"},
    "CIPLA.NS": {"company": "Cipla Ltd", "sector": "Pharmaceuticals"},
    "CUB.NS": {"company": "City Union Bank Ltd", "sector": "Financial Services"},
    "COALINDIA.NS": {"company": "Coal India Ltd", "sector": "Oil Gas & Consumable Fuels"},
    "COFORGE.NS": {"company": "Coforge Ltd", "sector": "Information Technology"},
    "COLPAL.NS": {"company": "Colgate Palmolive (India) Ltd", "sector": "FMCG"},
    "CONCOR.NS": {"company": "Container Corporation of India Ltd", "sector": "Services"},
    "COROMANDEL.NS": {"company": "Coromandel International Ltd", "sector": "Fertilizers & Agrochemicals"},
    "CROMPTON.NS": {"company": "Crompton Greaves Consumer Electricals Ltd", "sector": "Consumer Durables"},
    "CUMMINSIND.NS": {"company": "Cummins India Ltd", "sector": "Capital Goods"},
    "DALBHARAT.NS": {"company": "Dalmia Bharat Ltd", "sector": "Cement & Cement Products"},
    "DLF.NS": {"company": "DLF Ltd", "sector": "Realty"},
    "DIXON.NS": {"company": "Dixon Technologies (India) Ltd", "sector": "Consumer Durables"},
    "DIVISLAB.NS": {"company": "Divi's Laboratories Ltd", "sector": "Pharmaceuticals"},
    "LALPATHLAB.NS": {"company": "Dr. Lal PathLabs Ltd", "sector": "Healthcare Services"},
    "DRREDDY.NS": {"company": "Dr. Reddy's Laboratories Ltd", "sector": "Pharmaceuticals"},
    "EICHERMOT.NS": {"company": "Eicher Motors Ltd", "sector": "Automobile and Auto Components"},
    "ESCORTS.NS": {"company": "Escorts Kubota Ltd", "sector": "Capital Goods"},
    "FEDERALBNK.NS": {"company": "Federal Bank Ltd", "sector": "Financial Services"},
    "FORTIS.NS": {"company": "Fortis Healthcare Ltd", "sector": "Healthcare Services"},
    "GAIL.NS": {"company": "GAIL (India) Ltd", "sector": "Oil Gas & Consumable Fuels"},
    "GLAND.NS": {"company": "Gland Pharma Ltd", "sector": "Pharmaceuticals"},
    "GLENMARK.NS": {"company": "Glenmark Pharmaceuticals Ltd", "sector": "Pharmaceuticals"},
    "GODREJCP.NS": {"company": "Godrej Consumer Products Ltd", "sector": "FMCG"},
    "GODREJPROP.NS": {"company": "Godrej Properties Ltd", "sector": "Realty"},
    "GRANULES.NS": {"company": "Granules India Ltd", "sector": "Pharmaceuticals"},
    "GRASIM.NS": {"company": "Grasim Industries Ltd", "sector": "Cement & Cement Products"},
    "GUJGASLTD.NS": {"company": "Gujarat Gas Ltd", "sector": "Oil Gas & Consumable Fuels"},
    "GSPL.NS": {"company": "Gujarat State Petronet Ltd", "sector": "Oil Gas & Consumable Fuels"},
    "HCLTECH.NS": {"company": "HCL Technologies Ltd", "sector": "Information Technology"},
    "HDFCAMC.NS": {"company": "HDFC Asset Management Company Ltd", "sector": "Financial Services"},
    "HDFCBANK.NS": {"company": "HDFC Bank Ltd", "sector": "Financial Services"},
    "HDFCLIFE.NS": {"company": "HDFC Life Insurance Company Ltd", "sector": "Financial Services"},
    "HEROMOTOCO.NS": {"company": "Hero MotoCorp Ltd", "sector": "Automobile and Auto Components"},
    "HINDALCO.NS": {"company": "Hindalco Industries Ltd", "sector": "Metals & Mining"},
    "HAL.NS": {"company": "Hindustan Aeronautics Ltd", "sector": "Capital Goods"},
    "HINDCOPPER.NS": {"company": "Hindustan Copper Ltd", "sector": "Metals & Mining"},
    "HINDPETRO.NS": {"company": "Hindustan Petroleum Corporation Ltd", "sector": "Oil Gas & Consumable Fuels"},
    "HINDUNILVR.NS": {"company": "Hindustan Unilever Ltd", "sector": "FMCG"},
    "HINDZINC.NS": {"company": "Hindustan Zinc Ltd", "sector": "Metals & Mining"},
    "ICICIBANK.NS": {"company": "ICICI Bank Ltd", "sector": "Financial Services"},
    "ICICIGI.NS": {"company": "ICICI Lombard General Insurance Company Ltd", "sector": "Financial Services"},
    "ICICIPRULI.NS": {"company": "ICICI Prudential Life Insurance Company Ltd", "sector": "Financial Services"},
    "IDFCFIRSTB.NS": {"company": "IDFC First Bank Ltd", "sector": "Financial Services"},
    "IEX.NS": {"company": "Indian Energy Exchange Ltd", "sector": "Financial Services"},
    "IGL.NS": {"company": "Indraprastha Gas Ltd", "sector": "Oil Gas & Consumable Fuels"},
    "INDIACEM.NS": {"company": "The India Cements Ltd", "sector": "Cement & Cement Products"},
    "INDIAMART.NS": {"company": "IndiaMART InterMESH Ltd", "sector": "Consumer Services"},
    "INDHOTEL.NS": {"company": "The Indian Hotels Company Ltd", "sector": "Consumer Services"},
    "IOC.NS": {"company": "Indian Oil Corporation Ltd", "sector": "Oil Gas & Consumable Fuels"},
    "INDUSINDBK.NS": {"company": "IndusInd Bank Ltd", "sector": "Financial Services"},
    "NAUKRI.NS": {"company": "Info Edge (India) Ltd", "sector": "Consumer Services"},
    "INFY.NS": {"company": "Infosys Ltd", "sector": "Information Technology"},
    "INTELLECT.NS": {"company": "Intellect Design Arena Ltd", "sector": "Information Technology"},
    "INDIGO.NS": {"company": "InterGlobe Aviation Ltd", "sector": "Services"},
    "IPCALAB.NS": {"company": "IPCA Laboratories Ltd", "sector": "Pharmaceuticals"},
    "IRCTC.NS": {"company": "Indian Railway Catering And Tourism Corporation Ltd", "sector": "Consumer Services"},
    "ITC.NS": {"company": "ITC Ltd", "sector": "FMCG"},
    "JKCEMENT.NS": {"company": "JK Cement Ltd", "sector": "Cement & Cement Products"},
    "JINDALSTEL.NS": {"company": "Jindal Steel & Power Ltd", "sector": "Metals & Mining"},
    "JSWSTEEL.NS": {"company": "JSW Steel Ltd", "sector": "Metals & Mining"},
    "JUBLFOOD.NS": {"company": "Jubilant Foodworks Ltd", "sector": "Consumer Services"},
    "KAJARIACER.NS": {"company": "Kajaria Ceramics Ltd", "sector": "Consumer Durables"},
    "KANSAINER.NS": {"company": "Kansai Nerolac Paints Ltd", "sector": "Consumer Goods"},
    "KEC.NS": {"company": "KEC International Ltd", "sector": "Capital Goods"},
    "KOTAKBANK.NS": {"company": "Kotak Mahindra Bank Ltd", "sector": "Financial Services"},
    "L&TFH.NS": {"company": "L&T Finance Holdings Ltd", "sector": "Financial Services"},
    "LTTS.NS": {"company": "L&T Technology Services Ltd", "sector": "Information Technology"},
    "LICHSGFIN.NS": {"company": "LIC Housing Finance Ltd", "sector": "Financial Services"},
    "LT.NS": {"company": "Larsen & Toubro Ltd", "sector": "Capital Goods"},
    "LUPIN.NS": {"company": "Lupin Ltd", "sector": "Pharmaceuticals"},
    "MANAPPURAM.NS": {"company": "Manappuram Finance Ltd", "sector": "Financial Services"},
    "MARICO.NS": {"company": "Marico Ltd", "sector": "FMCG"},
    "MARUTI.NS": {"company": "Maruti Suzuki India Ltd", "sector": "Automobile and Auto Components"},
    "MCDOWELL-N.NS": {"company": "United Spirits Ltd", "sector": "FMCG"},
    "MCX.NS": {"company": "Multi Commodity Exchange of India Ltd", "sector": "Financial Services"},
    "METROPOLIS.NS": {"company": "Metropolis Healthcare Ltd", "sector": "Healthcare Services"},
    "MFSL.NS": {"company": "Max Financial Services Ltd", "sector": "Financial Services"},
    "MGL.NS": {"company": "Mahanagar Gas Ltd", "sector": "Oil Gas & Consumable Fuels"},
    "M&M.NS": {"company": "Mahindra & Mahindra Ltd", "sector": "Automobile and Auto Components"},
    "M&MFIN.NS": {"company": "Mahindra & Mahindra Financial Services Ltd", "sector": "Financial Services"},
    "MNGL.NS": {"company": "MNGL Ltd", "sector": "Oil Gas & Consumable Fuels"},
    "MPHASIS.NS": {"company": "Mphasis Ltd", "sector": "Information Technology"},
    "MRF.NS": {"company": "MRF Ltd", "sector": "Automobile and Auto Components"},
    "MUTHOOTFIN.NS": {"company": "Muthoot Finance Ltd", "sector": "Financial Services"},
    "NAM-INDIA.NS": {"company": "Nippon Life India Asset Management Ltd", "sector": "Financial Services"},
    "NATIONALUM.NS": {"company": "National Aluminium Company Ltd", "sector": "Metals & Mining"},
    "NAVINFLUOR.NS": {"company": "Navin Fluorine International Ltd", "sector": "Chemicals"},
    "NCC.NS": {"company": "NCC Ltd", "sector": "Construction"},
    "NESTLEIND.NS": {"company": "Nestle India Ltd", "sector": "FMCG"},
    "NMDC.NS": {"company": "NMDC Ltd", "sector": "Metals & Mining"},
    "NTPC.NS": {"company": "NTPC Ltd", "sector": "Power"},
    "OBEROIRLTY.NS": {"company": "Oberoi Realty Ltd", "sector": "Realty"},
    "OFSS.NS": {"company": "Oracle Financial Services Software Ltd", "sector": "Information Technology"},
    "ONGC.NS": {"company": "Oil & Natural Gas Corporation Ltd", "sector": "Oil Gas & Consumable Fuels"},
    "PAGEIND.NS": {"company": "Page Industries Ltd", "sector": "Textiles"},
    "PEL.NS": {"company": "Piramal Enterprises Ltd", "sector": "Pharmaceuticals"},
    "PERSISTENT.NS": {"company": "Persistent Systems Ltd", "sector": "Information Technology"},
    "PETRONET.NS": {"company": "Petronet LNG Ltd", "sector": "Oil Gas & Consumable Fuels"},
    "PFC.NS": {"company": "Power Finance Corporation Ltd", "sector": "Financial Services"},
    "PIDILITIND.NS": {"company": "Pidilite Industries Ltd", "sector": "Chemicals"},
    "PIIND.NS": {"company": "PI Industries Ltd", "sector": "Fertilizers & Agrochemicals"},
    "PNB.NS": {"company": "Punjab National Bank", "sector": "Financial Services"},
    "POLYCAB.NS": {"company": "Polycab India Ltd", "sector": "Capital Goods"},
    "POWERGRID.NS": {"company": "Power Grid Corporation of India Ltd", "sector": "Power"},
    "PRAJIND.NS": {"company": "Praj Industries Ltd", "sector": "Capital Goods"},
    "PRESTIGE.NS": {"company": "Prestige Estates Projects Ltd", "sector": "Realty"},
    "PVRINOX.NS": {"company": "PVR INOX Ltd", "sector": "Media & Entertainment"},
    "RAMCOCEM.NS": {"company": "The Ramco Cements Ltd", "sector": "Cement & Cement Products"},
    "RBLBANK.NS": {"company": "RBL Bank Ltd", "sector": "Financial Services"},
    "RECLTD.NS": {"company": "REC Ltd", "sector": "Financial Services"},
    "RELIANCE.NS": {"company": "Reliance Industries Ltd", "sector": "Oil Gas & Consumable Fuels"},
    "SAIL.NS": {"company": "Steel Authority of India Ltd", "sector": "Metals & Mining"},
    "SBICARD.NS": {"company": "SBI Cards and Payment Services Ltd", "sector": "Financial Services"},
    "SBILIFE.NS": {"company": "SBI Life Insurance Company Ltd", "sector": "Financial Services"},
    "SBIN.NS": {"company": "State Bank of India", "sector": "Financial Services"},
    "SCHAEFFLER.NS": {"company": "Schaeffler India Ltd", "sector": "Automobile and Auto Components"},
    "SHREECEM.NS": {"company": "Shree Cement Ltd", "sector": "Cement & Cement Products"},
    "SHRIRAMFIN.NS": {"company": "Shriram Finance Ltd", "sector": "Financial Services"},
    "SIEMENS.NS": {"company": "Siemens Ltd", "sector": "Capital Goods"},
    "SRF.NS": {"company": "SRF Ltd", "sector": "Chemicals"},
    "SRTRANSFIN.NS": {"company": "Shriram Transport Finance Company Ltd", "sector": "Financial Services"},
    "SUNPHARMA.NS": {"company": "Sun Pharmaceutical Industries Ltd", "sector": "Pharmaceuticals"},
    "SUNTV.NS": {"company": "Sun TV Network Ltd", "sector": "Media & Entertainment"},
    "SUPRAJIT.NS": {"company": "Suprajit Engineering Ltd", "sector": "Automobile and Auto Components"},
    "SYNGENE.NS": {"company": "Syngene International Ltd", "sector": "Pharmaceuticals"},
    "TATACHEM.NS": {"company": "Tata Chemicals Ltd", "sector": "Chemicals"},
    "TATACOMM.NS": {"company": "Tata Communications Ltd", "sector": "Telecommunication"},
    "TATACONSUM.NS": {"company": "Tata Consumer Products Ltd", "sector": "FMCG"},
    "TATAMOTORS.NS": {"company": "Tata Motors Ltd", "sector": "Automobile and Auto Components"},
    "TATAPOWER.NS": {"company": "Tata Power Company Ltd", "sector": "Power"},
    "TATASTEEL.NS": {"company": "Tata Steel Ltd", "sector": "Metals & Mining"},
    "TCS.NS": {"company": "Tata Consultancy Services Ltd", "sector": "Information Technology"},
    "TECHM.NS": {"company": "Tech Mahindra Ltd", "sector": "Information Technology"},
    "TITAN.NS": {"company": "Titan Company Ltd", "sector": "Consumer Goods"},
    "TORNTPHARM.NS": {"company": "Torrent Pharmaceuticals Ltd", "sector": "Pharmaceuticals"},
    "TORNTPOWER.NS": {"company": "Torrent Power Ltd", "sector": "Power"},
    "TRENT.NS": {"company": "Trent Ltd", "sector": "Consumer Services"},
    "TVSMOTOR.NS": {"company": "TVS Motor Company Ltd", "sector": "Automobile and Auto Components"},
    "UBL.NS": {"company": "United Breweries Ltd", "sector": "FMCG"},
    "ULTRACEMCO.NS": {"company": "UltraTech Cement Ltd", "sector": "Cement & Cement Products"},
    "UNIONBANK.NS": {"company": "Union Bank of India", "sector": "Financial Services"},
    "UPL.NS": {"company": "UPL Ltd", "sector": "Fertilizers & Agrochemicals"},
    "VEDL.NS": {"company": "Vedanta Ltd", "sector": "Metals & Mining"},
    "VOLTAS.NS": {"company": "Voltas Ltd", "sector": "Consumer Durables"},
    "WHIRLPOOL.NS": {"company": "Whirlpool of India Ltd", "sector": "Consumer Durables"},
    "WIPRO.NS": {"company": "Wipro Ltd", "sector": "Information Technology"},
    "ZEEL.NS": {"company": "Zee Entertainment Enterprises Ltd", "sector": "Media & Entertainment"}
}

# Use only PVRINOX for testing
TICKERS = list(TICKER_INFO.keys())
# For production, use: TICKERS = list(TICKER_INFO.keys())

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
    """Get stock data for a specific date - WITH VOLUME AND COMPANY INFO"""
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
        start_date = previous_day
        end_date = target_date_obj + timedelta(days=1)
        print(f"Fetching data from {start_date} to {end_date}")
        
        hist = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="1m")
        
        if hist.empty:
            return {
                "ticker": ticker,
                "error": f"No data available for {target_date}"
            }
        
        def extract_price_and_volume(date, time_str, price_type='Open'):
            dt = f"{date} {time_str}"
            if dt in hist.index:
                price = round(hist.loc[dt][price_type], 2)
                volume = int(hist.loc[dt]['Volume'])
                return price, volume
            return None, None
        
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

        # Extract prices and volumes for target date (morning session)
        p915, v915 = extract_price_and_volume(target_date_obj, '09:15:00', 'Open')
        p919, v919 = extract_price_and_volume(target_date_obj, '09:19:00', 'Close')

        # Extract prices and volumes for previous market day (closing session)
        p315, v315 = extract_price_and_volume(previous_day, '15:15:00', 'Open')
        p329, v329 = extract_price_and_volume(previous_day, '15:29:00', 'Close')

        # Additional values
        open_price = extract_day_open(target_date_obj)
        prev_close = extract_day_close(previous_day)
        current_price, _ = extract_price_and_volume(target_date_obj, '09:18:00', 'Close')

        # Calculate changes
        morning_change = round(((p919 - p915)/p915)*100, 2) if p915 and p919 else None
        closing_change = round(((p329 - p315)/p315)*100, 2) if p315 and p329 else None

        # Calculate volume changes
        morning_volume_change = round(((v919 - v915)/v915)*100, 2) if v915 and v919 and v915 > 0 else None
        closing_volume_change = round(((v329 - v315)/v315)*100, 2) if v315 and v329 and v315 > 0 else None

        # Get company info
        company_info = TICKER_INFO.get(ticker, {"company": "Unknown", "sector": "Unknown"})

        return {
            "ticker": ticker,
            "company_name": company_info["company"],
            "sector": company_info["sector"],
            "morning_date": str(target_date_obj),
            "p915": p915,
            "p919": p919,
            "v915": v915,
            "v919": v919,
            "morning_change": morning_change,
            "morning_volume_change": morning_volume_change,
            "closing_date": str(previous_day),
            "p315": p315,
            "p329": p329,
            "v315": v315,
            "v329": v329,
            "closing_change": closing_change,
            "closing_volume_change": closing_volume_change,
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
        
        # Get company info
        company_info = TICKER_INFO.get(ticker, {"company": "Unknown", "sector": "Unknown"})
        
        return {
            "ticker": ticker,
            "company_name": company_info["company"],
            "sector": company_info["sector"],
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
    """Original get_data function for current analysis - WITH VOLUME AND COMPANY INFO"""
    try:
        now = datetime.now(IST)
        previous_day, latest_day = get_last_two_working_days()
        hist = yf.Ticker(ticker).history(period="7d", interval="1m")
        
        def extract_price_and_volume(date, time_str, price_type='Open'):
            dt = f"{date} {time_str}"
            if dt in hist.index:
                price = round(hist.loc[dt][price_type], 2)
                volume = int(hist.loc[dt]['Volume'])
                return price, volume
            return None, None
        
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

        # Extract prices and volumes for current day (morning session)
        p915, v915 = extract_price_and_volume(latest_day, '09:15:00', 'Open')
        p919, v919 = extract_price_and_volume(latest_day, '09:19:00', 'Close')

        # Extract prices and volumes for previous day (closing session)
        p315, v315 = extract_price_and_volume(previous_day, '15:15:00', 'Open')
        p329, v329 = extract_price_and_volume(previous_day, '15:29:00', 'Close')

        # Additional values
        open_price = extract_day_open(latest_day)
        prev_close = extract_day_close(previous_day)
        current_price, _ = extract_price_and_volume(latest_day, '09:18:00', 'Close')

        # Calculate changes
        morning_change = round(((p919 - p915)/p915)*100, 2) if p915 and p919 else None
        closing_change = round(((p329 - p315)/p315)*100, 2) if p315 and p329 else None

        # Calculate volume changes
        morning_volume_change = round(((v919 - v915)/v915)*100, 2) if v915 and v919 and v915 > 0 else None
        closing_volume_change = round(((v329 - v315)/v315)*100, 2) if v315 and v329 and v315 > 0 else None

        # Get company info
        company_info = TICKER_INFO.get(ticker, {"company": "Unknown", "sector": "Unknown"})

        return {
            "ticker": ticker,
            "company_name": company_info["company"],
            "sector": company_info["sector"],
            "morning_date": str(latest_day),
            "p915": p915,
            "p919": p919,
            "v915": v915,
            "v919": v919,
            "morning_change": morning_change,
            "morning_volume_change": morning_volume_change,
            "closing_date": str(previous_day),
            "p315": p315,
            "p329": p329,
            "v315": v315,
            "v329": v329,
            "closing_change": closing_change,
            "closing_volume_change": closing_volume_change,
            "open_price": open_price,
            "prev_day_close": prev_close,
            "current_price": current_price
        }

    except Exception as e:
        return {
            "ticker": ticker,
            "error": str(e)
        }
def calculate_sector_performance(all_data):
    """Calculate gains/losses dashboard for sectors"""
    sector_stats = {}
    
    for data in all_data:
        if 'error' in data:
            continue
            
        sector = data.get('sector', 'Unknown')
        if sector not in sector_stats:
            sector_stats[sector] = {
                'sector': sector,
                'total_stocks': 0,
                'gainers': 0,
                'losers': 0,
                'unchanged': 0,
                'morning_gainers': 0,
                'morning_losers': 0,
                'closing_gainers': 0,
                'closing_losers': 0,
                'avg_morning_change': 0,
                'avg_closing_change': 0,
                'total_morning_change': 0,
                'total_closing_change': 0,
                'stocks': []
            }
        
        sector_stats[sector]['total_stocks'] += 1
        
        # Morning change analysis
        morning_change = data.get('morning_change')
        if morning_change is not None:
            sector_stats[sector]['total_morning_change'] += morning_change
            if morning_change > 0:
                sector_stats[sector]['morning_gainers'] += 1
            elif morning_change < 0:
                sector_stats[sector]['morning_losers'] += 1
        
        # Closing change analysis
        closing_change = data.get('closing_change')
        if closing_change is not None:
            sector_stats[sector]['total_closing_change'] += closing_change
            if closing_change > 0:
                sector_stats[sector]['closing_gainers'] += 1
            elif closing_change < 0:
                sector_stats[sector]['closing_losers'] += 1
        
        # Overall performance (using current price vs prev close if available)
        if data.get('current_price') and data.get('prev_day_close'):
            overall_change = ((data['current_price'] - data['prev_day_close']) / data['prev_day_close']) * 100
            if overall_change > 0:
                sector_stats[sector]['gainers'] += 1
            elif overall_change < 0:
                sector_stats[sector]['losers'] += 1
            else:
                sector_stats[sector]['unchanged'] += 1
        
        # Add stock to sector
        sector_stats[sector]['stocks'].append({
            'ticker': data['ticker'],
            'company_name': data.get('company_name', 'Unknown'),
            'morning_change': morning_change,
            'closing_change': closing_change
        })
    
    # Calculate averages
    for sector in sector_stats:
        total_stocks = sector_stats[sector]['total_stocks']
        if total_stocks > 0:
            sector_stats[sector]['avg_morning_change'] = round(
                sector_stats[sector]['total_morning_change'] / total_stocks, 2
            )
            sector_stats[sector]['avg_closing_change'] = round(
                sector_stats[sector]['total_closing_change'] / total_stocks, 2
            )
    
    # Convert to list and sort by total stocks
    sector_list = list(sector_stats.values())
    sector_list.sort(key=lambda x: x['total_stocks'], reverse=True)
    
    return sector_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(get_data, ticker): ticker for ticker in TICKERS}
        results = []
        for future in futures:
            results.append(future.result())
    
    # Calculate sector performance
    sector_performance = calculate_sector_performance(results)
    
    return jsonify({
        'stocks': results,
        'sectors': sector_performance,
        'timestamp': datetime.now(IST).isoformat()
    })

@app.route('/api/historical/<ticker>/<date>')
def api_historical(ticker, date):
    if ticker not in TICKER_INFO:
        return jsonify({"error": "Invalid ticker"}), 400
    
    result = get_data_for_date(ticker, date)
    return jsonify(result)

@app.route('/api/mock-trade', methods=['POST'])
def api_mock_trade():
    data = request.get_json()
    ticker = data.get('ticker')
    date = data.get('date')
    time = data.get('time')
    investment_amount = data.get('investment_amount', 10000)
    
    if not all([ticker, date, time]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    if ticker not in TICKER_INFO:
        return jsonify({"error": "Invalid ticker"}), 400
    
    result = execute_mock_trade_analysis(ticker, date, time, investment_amount)
    return jsonify(result)

@app.route('/api/sectors')
def api_sectors():
    """Get sector-wise performance data"""
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(get_data, ticker): ticker for ticker in TICKERS}
        results = []
        for future in futures:
            results.append(future.result())
    
    sector_performance = calculate_sector_performance(results)
    return jsonify({
        'sectors': sector_performance,
        'timestamp': datetime.now(IST).isoformat()
    })

@app.route('/api/sector/<sector_name>')
def api_sector_details(sector_name):
    """Get detailed information for a specific sector"""
    sector_tickers = [ticker for ticker, info in TICKER_INFO.items() if info['sector'] == sector_name]
    
    if not sector_tickers:
        return jsonify({"error": "Invalid sector name"}), 400
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(get_data, ticker): ticker for ticker in sector_tickers}
        results = []
        for future in futures:
            results.append(future.result())
    
    return jsonify({
        'sector': sector_name,
        'stocks': results,
        'timestamp': datetime.now(IST).isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True)
