import yfinance as yf
import pandas as pd
from flask import Flask, jsonify, render_template, request
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask_cors import CORS
from datetime import datetime, timedelta, time as dt_time
import pytz
import holidays
import os
from threading import Lock
import time

app = Flask(__name__)
CORS(app)

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

# Use all tickers for production
TICKERS = list(TICKER_INFO.keys())
IST = pytz.timezone('Asia/Kolkata')
IN_HOLIDAYS = holidays.India()

# Global cache for data
class DataCache:
    def __init__(self):
        self.current_data = {}
        self.historical_cache = {}
        self.time_filtered_cache = {}
        self.last_update = None
        self.cache_duration = 300  # 5 minutes cache
        self.lock = Lock()
    
    def is_cache_valid(self):
        if self.last_update is None:
            return False
        return (datetime.now() - self.last_update).seconds < self.cache_duration
    
    def get_current_data(self, force_last_working_day=False):
        """Get current data, with option to force last working day data"""
        with self.lock:
            if not self.is_cache_valid():
                self._fetch_current_data(force_last_working_day)
            return self.current_data.copy()
    
    def get_historical_data(self, date):
        with self.lock:
            if date not in self.historical_cache:
                self._fetch_historical_data(date)
            return self.historical_cache.get(date, {})
    
    def get_time_filtered_data(self, target_date, current_time):
        """Get data filtered by current time (9:15 AM to current_time)"""
        cache_key = f"{target_date}_{current_time}"
        
        with self.lock:
            if cache_key not in self.time_filtered_cache:
                self._fetch_time_filtered_data(target_date, current_time)
            return self.time_filtered_cache.get(cache_key, {})
    
    def _fetch_current_data(self, force_last_working_day=False):
        """Fetch current data for all tickers in parallel"""
        print("Fetching current data for all tickers...")
        start_time = time.time()
        
        # Determine which dates to use
        if force_last_working_day or not is_market_day(datetime.now(IST).date()):
            # Use last working day data
            previous_day, latest_day = get_last_two_working_days()
            print(f"Using last working day data: {latest_day} (previous: {previous_day})")
        else:
            # Use regular current data logic
            previous_day, latest_day = get_last_two_working_days()
        
        # Fetch data for all tickers in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all ticker fetch jobs
            future_to_ticker = {
                executor.submit(self._fetch_single_ticker_current, ticker, previous_day, latest_day): ticker 
                for ticker in TICKERS
            }
            
            results = {}
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    results[ticker] = future.result()
                except Exception as e:
                    results[ticker] = {"ticker": ticker, "error": str(e)}
        
        self.current_data = results
        self.last_update = datetime.now()
        
        print(f"Current data fetch completed in {time.time() - start_time:.2f} seconds")
    
    def _fetch_historical_data(self, target_date):
        """Fetch historical data for all tickers for a specific date"""
        print(f"Fetching historical data for {target_date}...")
        start_time = time.time()
        
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # If target date is not a market day, use the last working day
        if not is_market_day(target_date_obj):
            actual_target_date = get_previous_market_day(target_date_obj)
            print(f"Target date {target_date} is not a market day. Using {actual_target_date} instead.")
        else:
            actual_target_date = target_date_obj
        
        # Get previous market day
        previous_day = get_previous_market_day(actual_target_date)
        
        # Fetch data for all tickers in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_ticker = {
                executor.submit(self._fetch_single_ticker_historical, ticker, actual_target_date, previous_day): ticker 
                for ticker in TICKERS
            }
            
            results = {}
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    result = future.result()
                    # Add metadata about date adjustment
                    if actual_target_date != target_date_obj:
                        result['date_adjusted'] = True
                        result['requested_date'] = target_date
                        result['actual_date'] = str(actual_target_date)
                        result['adjustment_reason'] = f"Requested date {target_date} was not a market day"
                    results[ticker] = result
                except Exception as e:
                    results[ticker] = {"ticker": ticker, "error": str(e)}
        
        self.historical_cache[target_date] = results
        print(f"Historical data fetch for {target_date} completed in {time.time() - start_time:.2f} seconds")
    
    def _fetch_time_filtered_data(self, target_date, current_time):
        """Fetch time-filtered data for all tickers"""
        print(f"Fetching time-filtered data for {target_date} up to {current_time}...")
        start_time = time.time()
        
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # If target date is not a market day, use the last working day
        if not is_market_day(target_date_obj):
            actual_target_date = get_previous_market_day(target_date_obj)
            print(f"Target date {target_date} is not a market day. Using {actual_target_date} instead.")
        else:
            actual_target_date = target_date_obj
        
        # Get previous market day
        previous_day = get_previous_market_day(actual_target_date)
        
        # Fetch data for all tickers in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_ticker = {
                executor.submit(self._fetch_single_ticker_time_filtered, ticker, actual_target_date, previous_day, current_time): ticker 
                for ticker in TICKERS
            }
            
            results = {}
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    result = future.result()
                    # Add metadata about date adjustment
                    if actual_target_date != target_date_obj:
                        result['date_adjusted'] = True
                        result['requested_date'] = target_date
                        result['actual_date'] = str(actual_target_date)
                        result['adjustment_reason'] = f"Requested date {target_date} was not a market day"
                    results[ticker] = result
                except Exception as e:
                    results[ticker] = {"ticker": ticker, "error": str(e)}
        
        cache_key = f"{target_date}_{current_time}"
        self.time_filtered_cache[cache_key] = results
        print(f"Time-filtered data fetch for {target_date} up to {current_time} completed in {time.time() - start_time:.2f} seconds")
    
    def _fetch_single_ticker_current(self, ticker, previous_day, latest_day):
        """Fetch current data for a single ticker"""
        return process_ticker_data(ticker, latest_day, previous_day, is_current=True)
    
    def _fetch_single_ticker_historical(self, ticker, target_date_obj, previous_day):
        """Fetch historical data for a single ticker"""
        return process_ticker_data(ticker, target_date_obj, previous_day, is_current=False)
    
    def _fetch_single_ticker_time_filtered(self, ticker, target_date_obj, previous_day, current_time):
        """Fetch time-filtered data for a single ticker"""
        return process_ticker_data_time_filtered(ticker, target_date_obj, previous_day, current_time)

# Initialize global cache
data_cache = DataCache()

# Helper functions
def get_last_two_working_days():
    """Get the last two working days, regardless of today being a working day or not"""
    today = datetime.now(IST).date()
    days = []
    check_date = today
    
    # If today is not a working day, start from yesterday
    if not is_market_day(today):
        check_date = today - timedelta(days=1)
    
    while len(days) < 2:
        if is_market_day(check_date):
            days.insert(0, check_date)
        check_date -= timedelta(days=1)
    
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

def get_next_market_day(date_obj):
    """Get the next market day from given date"""
    next_date = date_obj + timedelta(days=1)
    while not is_market_day(next_date):
        next_date += timedelta(days=1)
    return next_date

def search_tickers(query):
    """Search for tickers based on company name, ticker symbol, or sector"""
    if not query:
        return TICKER_INFO
    
    query = query.lower()
    results = {}
    
    for ticker, info in TICKER_INFO.items():
        # Search in ticker symbol
        if query in ticker.lower():
            results[ticker] = info
            continue
        
        # Search in company name
        if query in info['company'].lower():
            results[ticker] = info
            continue
        
        # Search in sector
        if query in info['sector'].lower():
            results[ticker] = info
            continue
    
    return results

def process_ticker_data(ticker, target_date, previous_date, is_current=True):
    """Process data for a single ticker - unified logic for current and historical"""
    try:
        # Determine the date range for fetching data
        if is_current:
            # For current data, fetch last 7 days
            hist = yf.Ticker(ticker).history(period="7d", interval="1m")
        else:
            # For historical data, fetch specific date range
            start_date = previous_date
            end_date = target_date + timedelta(days=1)
            hist = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="1m")
        
        if hist.empty:
            return {
                "ticker": ticker,
                "error": f"No data available"
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
        p915, v915 = extract_price_and_volume(target_date, '09:15:00', 'Open')
        p919, v919 = extract_price_and_volume(target_date, '09:19:00', 'Close')

        # Extract prices and volumes for previous day (closing session)
        p315, v315 = extract_price_and_volume(previous_date, '15:15:00', 'Open')
        p329, v329 = extract_price_and_volume(previous_date, '15:29:00', 'Close')

        # Additional values
        open_price = extract_day_open(target_date)
        prev_close = extract_day_close(previous_date)
        current_price, _ = extract_price_and_volume(target_date, '09:18:00', 'Close')

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
            "morning_date": str(target_date),
            "p915": p915,
            "p919": p919,
            "v915": v915,
            "v919": v919,
            "morning_change": morning_change,
            "morning_volume_change": morning_volume_change,
            "closing_date": str(previous_date),
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

def process_ticker_data_time_filtered(ticker, target_date, previous_date, current_time):
    """Process time-filtered data for a single ticker (9:15 AM to current_time)"""
    try:
        # Parse current_time
        current_hour, current_minute = map(int, current_time.split(':'))
        current_time_obj = dt_time(current_hour, current_minute)
        
        # Validate time range (must be between 9:15 and 15:30)
        market_start = dt_time(9, 15)
        market_end = dt_time(15, 30)
        
        if current_time_obj < market_start:
            return {
                "ticker": ticker,
                "error": f"Market opens at 9:15 AM. Current time {current_time} is before market hours."
            }
        
        if current_time_obj > market_end:
            current_time_obj = market_end
            current_time = "15:30"
        
        # Fetch data for the specific date range
        start_date = previous_date
        end_date = target_date + timedelta(days=1)
        hist = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="1m")
        
        if hist.empty:
            return {
                "ticker": ticker,
                "error": f"No data available"
            }
        
        # Filter data for target date and time range (9:15 to current_time)
        day_data = hist[hist.index.date == target_date]
        if day_data.empty:
            return {
                "ticker": ticker,
                "error": f"No data available for {target_date}"
            }
        
        # Filter by time range
        filtered_data = day_data.between_time('09:15', current_time)
        
        if filtered_data.empty:
            return {
                "ticker": ticker,
                "error": f"No data available between 09:15 and {current_time}"
            }
        
        def extract_price_and_volume_filtered(date, time_str, price_type='Open'):
            dt = f"{date} {time_str}"
            if dt in hist.index:
                price = round(hist.loc[dt][price_type], 2)
                volume = int(hist.loc[dt]['Volume'])
                return price, volume
            return None, None
        
        def extract_day_close_prev(date):
            day_data = hist[hist.index.date == date]
            if not day_data.empty:
                closes = day_data.between_time('15:25', '15:30')
                return round(closes.iloc[-1]['Close'], 2) if not closes.empty else None
            return None
        
        # Get opening price at 9:15
        opening_price = round(filtered_data.iloc[0]['Open'], 2) if not filtered_data.empty else None
        opening_volume = int(filtered_data.iloc[0]['Volume']) if not filtered_data.empty else None
        
        # Get current price (last available price in the filtered range)
        current_price_filtered = round(filtered_data.iloc[-1]['Close'], 2) if not filtered_data.empty else None
        current_volume = int(filtered_data.iloc[-1]['Volume']) if not filtered_data.empty else None
        
        # Get highest and lowest prices in the time range
        high_price = round(filtered_data['High'].max(), 2) if not filtered_data.empty else None
        low_price = round(filtered_data['Low'].min(), 2) if not filtered_data.empty else None
        
        # Get previous day's closing price
        prev_close = extract_day_close_prev(previous_date)
        
        # Extract prices and volumes for previous day (closing session)
        p315, v315 = extract_price_and_volume_filtered(previous_date, '15:15:00', 'Open')
        p329, v329 = extract_price_and_volume_filtered(previous_date, '15:29:00', 'Close')
        
        # Calculate changes
        intraday_change = round(((current_price_filtered - opening_price)/opening_price)*100, 2) if opening_price and current_price_filtered else None
        overnight_change = round(((opening_price - prev_close)/prev_close)*100, 2) if opening_price and prev_close else None
        overall_change = round(((current_price_filtered - prev_close)/prev_close)*100, 2) if current_price_filtered and prev_close else None
        
        # Volume analysis
        total_volume = int(filtered_data['Volume'].sum()) if not filtered_data.empty else 0
        avg_volume = int(filtered_data['Volume'].mean()) if not filtered_data.empty else 0
        volume_change = round(((current_volume - opening_volume)/opening_volume)*100, 2) if opening_volume and current_volume and opening_volume > 0 else None
        
        # Previous day closing change
        closing_change = round(((p329 - p315)/p315)*100, 2) if p315 and p329 else None
        
        # Get company info
        company_info = TICKER_INFO.get(ticker, {"company": "Unknown", "sector": "Unknown"})
        
        # Generate minute-by-minute data for visualization
        minute_data = []
        for idx in filtered_data.index:
            minute_data.append({
                "time": idx.strftime('%H:%M'),
                "price": round(filtered_data.loc[idx]['Close'], 2),
                "volume": int(filtered_data.loc[idx]['Volume']),
                "high": round(filtered_data.loc[idx]['High'], 2),
                "low": round(filtered_data.loc[idx]['Low'], 2)
            })
        
        return {
            "ticker": ticker,
            "company_name": company_info["company"],
            "sector": company_info["sector"],
            "date": str(target_date),
            "time_range": f"09:15 - {current_time}",
            "opening_price": opening_price,
            "current_price": current_price_filtered,
            "high_price": high_price,
            "low_price": low_price,
            "prev_day_close": prev_close,
            "intraday_change": intraday_change,
            "overnight_change": overnight_change,
            "overall_change": overall_change,
            "opening_volume": opening_volume,
            "current_volume": current_volume,
            "total_volume": total_volume,
            "avg_volume": avg_volume,
            "volume_change": volume_change,
            "previous_day_closing_change": closing_change,
            "minute_data": minute_data,
            "data_points": len(minute_data)
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
        
        # If target date is not a market day, use the last working day
        if not is_market_day(target_date_obj):
            actual_target_date = get_previous_market_day(target_date_obj)
            print(f"Target date {date} is not a market day. Using {actual_target_date} instead.")
        else:
            actual_target_date = target_date_obj
        
        # Parse entry time
        entry_hour, entry_minute = map(int, time.split(':'))
        entry_time_obj = datetime.combine(actual_target_date, datetime.min.time().replace(hour=entry_hour, minute=entry_minute))
        
        # Fetch minute-level data for the trading day
        start_date = actual_target_date
        end_date = actual_target_date + timedelta(days=1)
        
        hist = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="1m")
        
        if hist.empty:
            return {
                "error": f"No trading data available for {ticker} on {actual_target_date}"
            }
        
        # Filter data for market hours (9:15 AM to 3:30 PM)
        market_data = hist.between_time('09:15', '15:30')
        market_data = market_data[market_data.index.date == actual_target_date]
        
        if market_data.empty:
            return {
                "error": f"No market data available for {ticker} on {actual_target_date}"
            }
        
        # Find entry price at specified time
        entry_time_str = f"{actual_target_date} {time}:00"
        entry_price = None
        
        # Find the closest available time to entry time
        for idx in market_data.index:
            if idx.strftime('%H:%M') >= time:
                entry_price = round(market_data.loc[idx]['Open'], 2)
                actual_entry_time = idx.strftime('%H:%M')
                break
        
        if entry_price is None:
            return {
                "error": f"No price data available at {time} on {actual_target_date}"
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
        
        result = {
            "ticker": ticker,
            "company_name": company_info["company"],
            "sector": company_info["sector"],
            "date": str(actual_target_date),
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
        
        # Add metadata if date was adjusted
        if actual_target_date != target_date_obj:
            result['date_adjusted'] = True
            result['requested_date'] = date
            result['adjustment_reason'] = f"Requested date {date} was not a market day"
        
        return result
        
    except Exception as e:
        return {
            "error": str(e)
        }

def calculate_sector_performance(all_data):
    """Calculate gains/losses dashboard for sectors"""
    sector_stats = {}
    
    # Handle both list and dict formats
    data_list = list(all_data.values()) if isinstance(all_data, dict) else all_data
    
    for data in data_list:
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
        
        # Handle different data formats (current vs time-filtered)
        change_field = data.get('morning_change') or data.get('intraday_change') or data.get('overall_change')
        if change_field is not None:
            sector_stats[sector]['total_morning_change'] += change_field
            if change_field > 0:
                sector_stats[sector]['morning_gainers'] += 1
            elif change_field < 0:
                sector_stats[sector]['morning_losers'] += 1
        
        # Closing change analysis
        closing_change = data.get('closing_change') or data.get('previous_day_closing_change')
        if closing_change is not None:
            sector_stats[sector]['total_closing_change'] += closing_change
            if closing_change > 0:
                sector_stats[sector]['closing_gainers'] += 1
            elif closing_change < 0:
                sector_stats[sector]['closing_losers'] += 1
        
        # Overall performance
        current_price = data.get('current_price')
        prev_close = data.get('prev_day_close')
        if current_price and prev_close:
            overall_change = ((current_price - prev_close) / prev_close) * 100
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
            'change': change_field,
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

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    """Get current data for all tickers - uses cached data, falls back to last working day if weekend/holiday"""
    # Check if today is a market day
    today = datetime.now(IST).date()
    is_today_market_day = is_market_day(today)
    
    # Force last working day data if today is not a market day
    current_data = data_cache.get_current_data(force_last_working_day=not is_today_market_day)
    
    # Convert dict to list format for compatibility
    results = list(current_data.values())
    
    # Calculate sector performance
    sector_performance = calculate_sector_performance(current_data)
    
    # Get the actual dates being used
    last_two_days = get_last_two_working_days()
    
    response_data = {
        'stocks': results,
        'sectors': sector_performance,
        'timestamp': datetime.now(IST).isoformat(),
        'is_market_day': is_today_market_day,
        'data_date': str(last_two_days[1]),  # Latest working day
        'previous_date': str(last_two_days[0])  # Previous working day
    }
    
    # Add weekend/holiday message if applicable
    if not is_today_market_day:
        if today.weekday() >= 5:  # Weekend
            response_data['message'] = f"Market closed (Weekend). Showing data from last trading day: {last_two_days[1]}"
        else:  # Holiday
            response_data['message'] = f"Market closed (Holiday). Showing data from last trading day: {last_two_days[1]}"
    
    return jsonify(response_data)

@app.route('/api/data/time-filtered')
def api_data_time_filtered():
    """Get time-filtered data (9:15 AM to current time) for all tickers"""
    # Get query parameters
    target_date = request.args.get('date')
    current_time = request.args.get('time')
    
    # Use today's date if not provided
    if not target_date:
        today = datetime.now(IST).date()
        if not is_market_day(today):
            # Use last working day if today is not a market day
            target_date = str(get_last_two_working_days()[1])
        else:
            target_date = str(today)
    
    # Use current time if not provided
    if not current_time:
        current_time = datetime.now(IST).strftime('%H:%M')
    
    try:
        # Validate date format
        datetime.strptime(target_date, '%Y-%m-%d')
        # Validate time format
        datetime.strptime(current_time, '%H:%M')
    except ValueError:
        return jsonify({"error": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time"}), 400
    
    time_filtered_data = data_cache.get_time_filtered_data(target_date, current_time)
    
    # Convert dict to list format for compatibility
    results = list(time_filtered_data.values())
    
    # Calculate sector performance for time-filtered data
    sector_performance = calculate_sector_performance(time_filtered_data)
    
    # Check if any date adjustment was made
    date_adjusted = any(result.get('date_adjusted', False) for result in results if 'error' not in result)
    actual_date = None
    adjustment_reason = None
    
    if date_adjusted:
        for result in results:
            if result.get('date_adjusted', False):
                actual_date = result.get('actual_date')
                adjustment_reason = result.get('adjustment_reason')
                break
    
    response_data = {
        'date': target_date,
        'time_range': f"09:15 - {current_time}",
        'stocks': results,
        'sectors': sector_performance,
        'timestamp': datetime.now(IST).isoformat()
    }
    
    if date_adjusted:
        response_data['date_adjusted'] = True
        response_data['actual_date'] = actual_date
        response_data['adjustment_reason'] = adjustment_reason
    
    return jsonify(response_data)

@app.route('/api/search')
def api_search():
    """Search for tickers based on query"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    
    # Search for matching tickers
    matching_tickers = search_tickers(query)
    
    if not matching_tickers:
        return jsonify({
            "query": query,
            "results": [],
            "message": "No tickers found matching your search"
        })
    
    # Check if today is a market day
    today = datetime.now(IST).date()
    is_today_market_day = is_market_day(today)
    
    # Get current data for matching tickers only (force last working day if needed)
    current_data = data_cache.get_current_data(force_last_working_day=not is_today_market_day)
    
    # Filter results to only include matching tickers
    search_results = []
    for ticker in matching_tickers:
        if ticker in current_data:
            search_results.append(current_data[ticker])
        else:
            # If not in cache, add basic info
            search_results.append({
                "ticker": ticker,
                "company_name": matching_tickers[ticker]["company"],
                "sector": matching_tickers[ticker]["sector"],
                "message": "Data not available in cache"
            })
    
    # Get the actual dates being used
    last_two_days = get_last_two_working_days()
    
    response_data = {
        "query": query,
        "results": search_results,
        "total_found": len(matching_tickers),
        "timestamp": datetime.now(IST).isoformat(),
        "is_market_day": is_today_market_day,
        "data_date": str(last_two_days[1])
    }
    
    # Add weekend/holiday message if applicable
    if not is_today_market_day:
        if today.weekday() >= 5:  # Weekend
            response_data['message'] = f"Market closed (Weekend). Showing data from last trading day: {last_two_days[1]}"
        else:  # Holiday
            response_data['message'] = f"Market closed (Holiday). Showing data from last trading day: {last_two_days[1]}"
    
    return jsonify(response_data)

@app.route('/api/search/time-filtered')
def api_search_time_filtered():
    """Search for tickers and get time-filtered data"""
    query = request.args.get('q', '').strip()
    target_date = request.args.get('date')
    current_time = request.args.get('time')
    
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    
    # Use appropriate date if not provided
    if not target_date:
        today = datetime.now(IST).date()
        if not is_market_day(today):
            # Use last working day if today is not a market day
            target_date = str(get_last_two_working_days()[1])
        else:
            target_date = str(today)
    
    # Use current time if not provided
    if not current_time:
        current_time = datetime.now(IST).strftime('%H:%M')
    
    try:
        # Validate date format
        datetime.strptime(target_date, '%Y-%m-%d')
        # Validate time format
        datetime.strptime(current_time, '%H:%M')
    except ValueError:
        return jsonify({"error": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time"}), 400
    
    # Search for matching tickers
    matching_tickers = search_tickers(query)
    
    if not matching_tickers:
        return jsonify({
            "query": query,
            "results": [],
            "message": "No tickers found matching your search"
        })
    
    # Get time-filtered data for matching tickers
    time_filtered_data = data_cache.get_time_filtered_data(target_date, current_time)
    
    # Filter results to only include matching tickers
    search_results = []
    for ticker in matching_tickers:
        if ticker in time_filtered_data:
            search_results.append(time_filtered_data[ticker])
        else:
            # If not in cache, add basic info
            search_results.append({
                "ticker": ticker,
                "company_name": matching_tickers[ticker]["company"],
                "sector": matching_tickers[ticker]["sector"],
                "message": "Time-filtered data not available"
            })
    
    # Check if any date adjustment was made
    date_adjusted = any(result.get('date_adjusted', False) for result in search_results if 'error' not in result)
    actual_date = None
    adjustment_reason = None
    
    if date_adjusted:
        for result in search_results:
            if result.get('date_adjusted', False):
                actual_date = result.get('actual_date')
                adjustment_reason = result.get('adjustment_reason')
                break
    
    response_data = {
        "query": query,
        "date": target_date,
        "time_range": f"09:15 - {current_time}",
        "results": search_results,
        "total_found": len(matching_tickers),
        "timestamp": datetime.now(IST).isoformat()
    }
    
    if date_adjusted:
        response_data['date_adjusted'] = True
        response_data['actual_date'] = actual_date
        response_data['adjustment_reason'] = adjustment_reason
    
    return jsonify(response_data)

@app.route('/api/ticker/<ticker>')
def api_single_ticker(ticker):
    """Get detailed data for a single ticker"""
    if ticker not in TICKER_INFO:
        return jsonify({"error": f"Invalid ticker: {ticker}"}), 400
    
    # Check if today is a market day
    today = datetime.now(IST).date()
    is_today_market_day = is_market_day(today)
    
    # Get current data (force last working day if needed)
    current_data = data_cache.get_current_data(force_last_working_day=not is_today_market_day)
    
    if ticker in current_data:
        result = current_data[ticker]
        
        # Add market status information
        last_two_days = get_last_two_working_days()
        result['is_market_day'] = is_today_market_day
        result['data_date'] = str(last_two_days[1])
        
        if not is_today_market_day:
            if today.weekday() >= 5:  # Weekend
                result['message'] = f"Market closed (Weekend). Showing data from last trading day: {last_two_days[1]}"
            else:  # Holiday
                result['message'] = f"Market closed (Holiday). Showing data from last trading day: {last_two_days[1]}"
        
        return jsonify(result)
    else:
        return jsonify({"error": "Data not available for this ticker"}), 404

@app.route('/api/ticker/<ticker>/time-filtered')
def api_single_ticker_time_filtered(ticker):
    """Get time-filtered data for a single ticker"""
    if ticker not in TICKER_INFO:
        return jsonify({"error": f"Invalid ticker: {ticker}"}), 400
    
    target_date = request.args.get('date')
    current_time = request.args.get('time')
    
    # Use appropriate date if not provided
    if not target_date:
        today = datetime.now(IST).date()
        if not is_market_day(today):
            # Use last working day if today is not a market day
            target_date = str(get_last_two_working_days()[1])
        else:
            target_date = str(today)
    
    # Use current time if not provided
    if not current_time:
        current_time = datetime.now(IST).strftime('%H:%M')
    
    try:
        # Validate date format
        datetime.strptime(target_date, '%Y-%m-%d')
        # Validate time format
        datetime.strptime(current_time, '%H:%M')
    except ValueError:
        return jsonify({"error": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time"}), 400
    
    # Get time-filtered data
    time_filtered_data = data_cache.get_time_filtered_data(target_date, current_time)
    
    if ticker in time_filtered_data:
        return jsonify(time_filtered_data[ticker])
    else:
        return jsonify({"error": "Time-filtered data not available for this ticker"}), 404

@app.route('/api/historical/<date>')
def api_historical_all(date):
    """Get historical data for ALL tickers for a specific date"""
    try:
        # Validate date format
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    historical_data = data_cache.get_historical_data(date)
    
    # Convert dict to list format for compatibility
    results = list(historical_data.values())
    
    # Calculate sector performance for historical data
    sector_performance = calculate_sector_performance(historical_data)
    
    # Check if any date adjustment was made
    date_adjusted = any(result.get('date_adjusted', False) for result in results if 'error' not in result)
    actual_date = None
    adjustment_reason = None
    
    if date_adjusted:
        for result in results:
            if result.get('date_adjusted', False):
                actual_date = result.get('actual_date')
                adjustment_reason = result.get('adjustment_reason')
                break
    
    response_data = {
        'date': date,
        'stocks': results,
        'sectors': sector_performance,
        'timestamp': datetime.now(IST).isoformat()
    }
    
    if date_adjusted:
        response_data['date_adjusted'] = True
        response_data['actual_date'] = actual_date
        response_data['adjustment_reason'] = adjustment_reason
    
    return jsonify(response_data)

@app.route('/api/historical/<ticker>/<date>')
def api_historical_single(ticker, date):
    """Get historical data for a single ticker (backward compatibility)"""
    if ticker not in TICKER_INFO:
        return jsonify({"error": "Invalid ticker"}), 400
    
    try:
        # Validate date format
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    historical_data = data_cache.get_historical_data(date)
    
    if ticker in historical_data:
        return jsonify(historical_data[ticker])
    else:
        return jsonify({"error": "No data available for this ticker"}), 404

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
    """Get sector-wise performance data - uses cached data"""
    # Check if today is a market day
    today = datetime.now(IST).date()
    is_today_market_day = is_market_day(today)
    
    # Get current data (force last working day if needed)
    current_data = data_cache.get_current_data(force_last_working_day=not is_today_market_day)
    sector_performance = calculate_sector_performance(current_data)
    
    # Get the actual dates being used
    last_two_days = get_last_two_working_days()
    
    response_data = {
        'sectors': sector_performance,
        'timestamp': datetime.now(IST).isoformat(),
        'is_market_day': is_today_market_day,
        'data_date': str(last_two_days[1])
    }
    
    # Add weekend/holiday message if applicable
    if not is_today_market_day:
        if today.weekday() >= 5:  # Weekend
            response_data['message'] = f"Market closed (Weekend). Showing data from last trading day: {last_two_days[1]}"
        else:  # Holiday
            response_data['message'] = f"Market closed (Holiday). Showing data from last trading day: {last_two_days[1]}"
    
    return jsonify(response_data)

@app.route('/api/sector/<sector_name>')
def api_sector_details(sector_name):
    """Get detailed information for a specific sector - uses cached data"""
    # Check if today is a market day
    today = datetime.now(IST).date()
    is_today_market_day = is_market_day(today)
    
    # Get current data (force last working day if needed)
    current_data = data_cache.get_current_data(force_last_working_day=not is_today_market_day)
    
    # Filter stocks by sector
    sector_stocks = {}
    for ticker, data in current_data.items():
        if data.get('sector') == sector_name:
            sector_stocks[ticker] = data
    
    if not sector_stocks:
        return jsonify({"error": "Invalid sector name or no stocks found"}), 400
    
    # Get the actual dates being used
    last_two_days = get_last_two_working_days()
    
    response_data = {
        'sector': sector_name,
        'stocks': list(sector_stocks.values()),
        'timestamp': datetime.now(IST).isoformat(),
        'is_market_day': is_today_market_day,
        'data_date': str(last_two_days[1])
    }
    
    # Add weekend/holiday message if applicable
    if not is_today_market_day:
        if today.weekday() >= 5:  # Weekend
            response_data['message'] = f"Market closed (Weekend). Showing data from last trading day: {last_two_days[1]}"
        else:  # Holiday
            response_data['message'] = f"Market closed (Holiday). Showing data from last trading day: {last_two_days[1]}"
    
    return jsonify(response_data)

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """Manually refresh current data cache"""
    data_cache.last_update = None  # Force refresh
    
    # Check if today is a market day
    today = datetime.now(IST).date()
    is_today_market_day = is_market_day(today)
    
    # Get current data (force last working day if needed)
    current_data = data_cache.get_current_data(force_last_working_day=not is_today_market_day)
    
    # Get the actual dates being used
    last_two_days = get_last_two_working_days()
    
    response_data = {
        'message': 'Data refreshed successfully',
        'stocks_count': len(current_data),
        'timestamp': datetime.now(IST).isoformat(),
        'is_market_day': is_today_market_day,
        'data_date': str(last_two_days[1])
    }
    
    # Add weekend/holiday message if applicable
    if not is_today_market_day:
        if today.weekday() >= 5:  # Weekend
            response_data['refresh_message'] = f"Market closed (Weekend). Refreshed with data from last trading day: {last_two_days[1]}"
        else:  # Holiday
            response_data['refresh_message'] = f"Market closed (Holiday). Refreshed with data from last trading day: {last_two_days[1]}"
    
    return jsonify(response_data)

@app.route('/api/tickers')
def api_list_tickers():
    """Get list of all available tickers with company info"""
    return jsonify({
        'tickers': TICKER_INFO,
        'total_count': len(TICKER_INFO),
        'timestamp': datetime.now(IST).isoformat()
    })

@app.route('/api/market-status')
def api_market_status():
    """Get current market status"""
    now = datetime.now(IST)
    current_date = now.date()
    current_time = now.time()
    
    is_market_open = False
    market_session = "Closed"
    
    if is_market_day(current_date):
        market_start = dt_time(9, 15)
        market_end = dt_time(15, 30)
        
        if market_start <= current_time <= market_end:
            is_market_open = True
            if dt_time(9, 15) <= current_time <= dt_time(11, 30):
                market_session = "Morning Session"
            elif dt_time(11, 30) < current_time <= dt_time(13, 0):
                market_session = "Break"
            else:
                market_session = "Afternoon Session"
        elif current_time < market_start:
            market_session = "Pre-Market"
        else:
            market_session = "Post-Market"
    else:
        if current_date.weekday() >= 5:  # Weekend
            market_session = "Weekend"
        else:  # Holiday
            market_session = "Market Holiday"
    
    # Get last working day info
    last_two_days = get_last_two_working_days()
    
    return jsonify({
        'is_market_open': is_market_open,
        'market_session': market_session,
        'is_market_day': is_market_day(current_date),
        'current_time': now.strftime('%Y-%m-%d %H:%M:%S'),
        'current_date': str(current_date),
        'last_trading_day': str(last_two_days[1]),
        'previous_trading_day': str(last_two_days[0]),
        'next_trading_day': str(get_next_market_day(current_date)),
        'timestamp': now.isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)