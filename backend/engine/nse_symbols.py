"""
NSE Symbol list fetcher - downloads the complete list of NSE-listed companies
and caches it for autocomplete search.
"""
import os
import json
import time
import pandas as pd
import requests
from io import StringIO

CACHE_FILE = os.path.join(os.path.dirname(__file__), "nse_symbols_cache.json")
CACHE_TTL = 86400  # 24 hours


def _fetch_from_nse() -> list[dict]:
    """Downloads the live EQUITY list from NSE India directly."""
    try:
        url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/",
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text))
        # Columns: SYMBOL, NAME OF COMPANY, SERIES, DATE OF LISTING, ...
        results = []
        for _, row in df.iterrows():
            sym = str(row.get("SYMBOL", "")).strip()
            name = str(row.get("NAME OF COMPANY", "")).strip()
            if sym and name and sym != "nan":
                results.append({"symbol": sym, "name": name})
        return results
    except Exception as e:
        print(f"[NSE Fetch] Failed to download from NSE: {e}")
        return []


def _load_builtin_fallback() -> list[dict]:
    """A curated fallback list of top 200 NSE stocks in case the live fetch fails."""
    return [
        {"symbol": "RELIANCE", "name": "Reliance Industries Ltd"},
        {"symbol": "TCS", "name": "Tata Consultancy Services Ltd"},
        {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd"},
        {"symbol": "INFY", "name": "Infosys Ltd"},
        {"symbol": "HINDUNILVR", "name": "Hindustan Unilever Ltd"},
        {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd"},
        {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank Ltd"},
        {"symbol": "SBIN", "name": "State Bank of India"},
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd"},
        {"symbol": "ITC", "name": "ITC Ltd"},
        {"symbol": "AXISBANK", "name": "Axis Bank Ltd"},
        {"symbol": "LT", "name": "Larsen & Toubro Ltd"},
        {"symbol": "WIPRO", "name": "Wipro Ltd"},
        {"symbol": "ASIANPAINT", "name": "Asian Paints Ltd"},
        {"symbol": "MARUTI", "name": "Maruti Suzuki India Ltd"},
        {"symbol": "ULTRACEMCO", "name": "UltraTech Cement Ltd"},
        {"symbol": "TITAN", "name": "Titan Company Ltd"},
        {"symbol": "BAJFINANCE", "name": "Bajaj Finance Ltd"},
        {"symbol": "BAJAJFINSV", "name": "Bajaj Finserv Ltd"},
        {"symbol": "HCLTECH", "name": "HCL Technologies Ltd"},
        {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical Industries Ltd"},
        {"symbol": "ONGC", "name": "Oil and Natural Gas Corporation Ltd"},
        {"symbol": "NESTLEIND", "name": "Nestle India Ltd"},
        {"symbol": "POWERGRID", "name": "Power Grid Corporation of India Ltd"},
        {"symbol": "NTPC", "name": "NTPC Ltd"},
        {"symbol": "M&M", "name": "Mahindra & Mahindra Ltd"},
        {"symbol": "TATAMOTORS", "name": "Tata Motors Ltd"},
        {"symbol": "TECHM", "name": "Tech Mahindra Ltd"},
        {"symbol": "TATASTEEL", "name": "Tata Steel Ltd"},
        {"symbol": "ADANIENT", "name": "Adani Enterprises Ltd"},
        {"symbol": "ADANIPORTS", "name": "Adani Ports and Special Economic Zone Ltd"},
        {"symbol": "COALINDIA", "name": "Coal India Ltd"},
        {"symbol": "DIVISLAB", "name": "Divi's Laboratories Ltd"},
        {"symbol": "DRREDDY", "name": "Dr. Reddy's Laboratories Ltd"},
        {"symbol": "CIPLA", "name": "Cipla Ltd"},
        {"symbol": "EICHERMOT", "name": "Eicher Motors Ltd"},
        {"symbol": "GRASIM", "name": "Grasim Industries Ltd"},
        {"symbol": "HEROMOTOCO", "name": "Hero MotoCorp Ltd"},
        {"symbol": "HINDALCO", "name": "Hindalco Industries Ltd"},
        {"symbol": "INDUSINDBK", "name": "IndusInd Bank Ltd"},
        {"symbol": "JSWSTEEL", "name": "JSW Steel Ltd"},
        {"symbol": "TATACONSUM", "name": "Tata Consumer Products Ltd"},
        {"symbol": "APOLLOHOSP", "name": "Apollo Hospitals Enterprise Ltd"},
        {"symbol": "BAJAJ-AUTO", "name": "Bajaj Auto Ltd"},
        {"symbol": "BPCL", "name": "Bharat Petroleum Corporation Ltd"},
        {"symbol": "BRITANNIA", "name": "Britannia Industries Ltd"},
        {"symbol": "SBILIFE", "name": "SBI Life Insurance Company Ltd"},
        {"symbol": "HDFCLIFE", "name": "HDFC Life Insurance Company Ltd"},
        {"symbol": "VEDL", "name": "Vedanta Ltd"},
        {"symbol": "BANKBARODA", "name": "Bank of Baroda"},
        {"symbol": "ZOMATO", "name": "Zomato Ltd"},
        {"symbol": "PAYTM", "name": "One97 Communications Ltd (Paytm)"},
        {"symbol": "NYKAA", "name": "FSN E-Commerce Ventures Ltd (Nykaa)"},
        {"symbol": "POLICYBZR", "name": "PB Fintech Ltd (Policybazaar)"},
        {"symbol": "IRCTC", "name": "Indian Railway Catering and Tourism Corporation Ltd"},
        {"symbol": "HAL", "name": "Hindustan Aeronautics Ltd"},
        {"symbol": "BEL", "name": "Bharat Electronics Ltd"},
        {"symbol": "SIEMENS", "name": "Siemens Ltd"},
        {"symbol": "ABB", "name": "ABB India Ltd"},
        {"symbol": "HAVELLS", "name": "Havells India Ltd"},
        {"symbol": "VOLTAS", "name": "Voltas Ltd"},
        {"symbol": "PIDILITIND", "name": "Pidilite Industries Ltd"},
        {"symbol": "DMART", "name": "Avenue Supermarts Ltd"},
        {"symbol": "INDUSTOWER", "name": "Indus Towers Ltd"},
        {"symbol": "GAIL", "name": "GAIL (India) Ltd"},
        {"symbol": "IOC", "name": "Indian Oil Corporation Ltd"},
        {"symbol": "HPCL", "name": "Hindustan Petroleum Corporation Ltd"},
        {"symbol": "IOCL", "name": "Indian Oil Corporation Ltd"},
        {"symbol": "AMBUJACEM", "name": "Ambuja Cements Ltd"},
        {"symbol": "ACC", "name": "ACC Ltd"},
        {"symbol": "SHREECEM", "name": "Shree Cement Ltd"},
        {"symbol": "LUPIN", "name": "Lupin Ltd"},
        {"symbol": "BIOCON", "name": "Biocon Ltd"},
        {"symbol": "TORNTPHARM", "name": "Torrent Pharmaceuticals Ltd"},
        {"symbol": "MCDOWELL-N", "name": "United Spirits Ltd"},
        {"symbol": "UBL", "name": "United Breweries Ltd"},
        {"symbol": "COLPAL", "name": "Colgate-Palmolive (India) Ltd"},
        {"symbol": "DABUR", "name": "Dabur India Ltd"},
        {"symbol": "GODREJCP", "name": "Godrej Consumer Products Ltd"},
        {"symbol": "MARICO", "name": "Marico Ltd"},
        {"symbol": "EMAMILTD", "name": "Emami Ltd"},
        {"symbol": "PGHH", "name": "Procter & Gamble Hygiene and Health Care Ltd"},
        {"symbol": "MUTHOOTFIN", "name": "Muthoot Finance Ltd"},
        {"symbol": "BAJAJHLDNG", "name": "Bajaj Holdings & Investment Ltd"},
        {"symbol": "CHOLAFIN", "name": "Cholamandalam Investment and Finance Company Ltd"},
        {"symbol": "LICHSGFIN", "name": "LIC Housing Finance Ltd"},
        {"symbol": "PFC", "name": "Power Finance Corporation Ltd"},
        {"symbol": "RECLTD", "name": "REC Ltd"},
        {"symbol": "NHPC", "name": "NHPC Ltd"},
        {"symbol": "SJVN", "name": "SJVN Ltd"},
        {"symbol": "TATAPOWER", "name": "Tata Power Company Ltd"},
        {"symbol": "TORNTPOWER", "name": "Torrent Power Ltd"},
        {"symbol": "ADANIGREEN", "name": "Adani Green Energy Ltd"},
        {"symbol": "ADANITRANS", "name": "Adani Transmission Ltd"},
        {"symbol": "GMRINFRA", "name": "GMR Infrastructure Ltd"},
        {"symbol": "IRB", "name": "IRB Infrastructure Developers Ltd"},
        {"symbol": "INDIGO", "name": "InterGlobe Aviation Ltd"},
        {"symbol": "SPICEJET", "name": "SpiceJet Ltd"},
        {"symbol": "ZEEL", "name": "Zee Entertainment Enterprises Ltd"},
        {"symbol": "SUNTV", "name": "Sun TV Network Ltd"},
        {"symbol": "PVRINOX", "name": "PVR INOX Ltd"},
        {"symbol": "MPHASIS", "name": "Mphasis Ltd"},
        {"symbol": "LTIM", "name": "LTIMindtree Ltd"},
        {"symbol": "PERSISTENT", "name": "Persistent Systems Ltd"},
        {"symbol": "COFORGE", "name": "Coforge Ltd"},
        {"symbol": "KPITTECH", "name": "KPIT Technologies Ltd"},
        {"symbol": "TANLA", "name": "Tanla Platforms Ltd"},
        {"symbol": "RRKABEL", "name": "R R Kabel Ltd"},
        {"symbol": "TRENT", "name": "Trent Ltd"},
        {"symbol": "SHOPERSTOP", "name": "Shoppers Stop Ltd"},
        {"symbol": "PAGEIND", "name": "Page Industries Ltd"},
        {"symbol": "AIAENG", "name": "AIA Engineering Ltd"},
        {"symbol": "SUPREMEIND", "name": "Supreme Industries Ltd"},
        {"symbol": "APLAPOLLO", "name": "APL Apollo Tubes Ltd"},
        {"symbol": "ASTRAL", "name": "Astral Ltd"},
        {"symbol": "POLYCAB", "name": "Polycab India Ltd"},
        {"symbol": "DIXON", "name": "Dixon Technologies (India) Ltd"},
        {"symbol": "KAYNES", "name": "Kaynes Technology India Ltd"},
        {"symbol": "SYRMA", "name": "Syrma SGS Technology Ltd"},
        {"symbol": "WAAREEENER", "name": "Waaree Energies Ltd"},
        {"symbol": "PREMIER", "name": "Premier Explosives Ltd"},
        {"symbol": "MAHABANK", "name": "Bank of Maharashtra"},
        {"symbol": "CANBK", "name": "Canara Bank"},
        {"symbol": "PNB", "name": "Punjab National Bank"},
        {"symbol": "UNIONBANK", "name": "Union Bank of India"},
        {"symbol": "FEDERALBNK", "name": "The Federal Bank Ltd"},
        {"symbol": "BANDHANBNK", "name": "Bandhan Bank Ltd"},
        {"symbol": "RBLBANK", "name": "RBL Bank Ltd"},
        {"symbol": "IDFCFIRSTB", "name": "IDFC First Bank Ltd"},
        {"symbol": "YESBANK", "name": "Yes Bank Ltd"},
        {"symbol": "KARURVYSYA", "name": "The Karur Vysya Bank Ltd"},
        {"symbol": "SOUTHBANK", "name": "South Indian Bank Ltd"},
        {"symbol": "DCBBANK", "name": "DCB Bank Ltd"},
        {"symbol": "FINPIPE", "name": "Finolex Industries Ltd"},
        {"symbol": "VBL", "name": "Varun Beverages Ltd"},
        {"symbol": "RADICO", "name": "Radico Khaitan Ltd"},
        {"symbol": "BALRAMCHIN", "name": "Balrampur Chini Mills Ltd"},
        {"symbol": "DHANUKA", "name": "Dhanuka Agritech Ltd"},
        {"symbol": "PIIND", "name": "PI Industries Ltd"},
        {"symbol": "SUMICHEM", "name": "Sumitomo Chemical India Ltd"},
        {"symbol": "GNFC", "name": "Gujarat Narmada Valley Fertilizers & Chemicals Ltd"},
        {"symbol": "DEEPAKFERT", "name": "Deepak Fertilizers and Petrochemicals Corporation Ltd"},
        {"symbol": "AARTIIND", "name": "Aarti Industries Ltd"},
        {"symbol": "VINATI", "name": "Vinati Organics Ltd"},
        {"symbol": "GALAXY", "name": "Galaxy Surfactants Ltd"},
        {"symbol": "SRF", "name": "SRF Ltd"},
        {"symbol": "NAVINFLUO", "name": "Navin Fluorine International Ltd"},
        {"symbol": "CLEAN", "name": "Clean Science and Technology Ltd"},
        {"symbol": "ALKYLAMINE", "name": "Alkyl Amines Chemicals Ltd"},
        {"symbol": "NOCIL", "name": "NOCIL Ltd"},
        {"symbol": "THYROCARE", "name": "Thyrocare Technologies Ltd"},
        {"symbol": "METROPOLIS", "name": "Metropolis Healthcare Ltd"},
        {"symbol": "KRSNAA", "name": "Krsnaa Diagnostics Ltd"},
        {"symbol": "MAXHEALTH", "name": "Max Healthcare Institute Ltd"},
        {"symbol": "FORTIS", "name": "Fortis Healthcare Ltd"},
        {"symbol": "MEDANTA", "name": "Global Health Ltd (Medanta)"},
        {"symbol": "RAINBOW", "name": "Rainbow Children's Medicare Ltd"},
        {"symbol": "VIJAYA", "name": "Vijaya Diagnostic Centre Ltd"},
        {"symbol": "HINDPETRO", "name": "Hindustan Petroleum Corporation Ltd"},
        {"symbol": "MGL", "name": "Mahanagar Gas Ltd"},
        {"symbol": "IGL", "name": "Indraprastha Gas Ltd"},
        {"symbol": "GUJGASLTD", "name": "Gujarat Gas Ltd"},
        {"symbol": "PETRONET", "name": "Petronet LNG Ltd"},
        {"symbol": "CONCOR", "name": "Container Corporation of India Ltd"},
        {"symbol": "BLUEDART", "name": "Blue Dart Express Ltd"},
        {"symbol": "MAHLOG", "name": "Mahindra Logistics Ltd"},
        {"symbol": "DELHIVERY", "name": "Delhivery Ltd"},
        {"symbol": "XPRO", "name": "Xpro India Ltd"},
        {"symbol": "TATACHEM", "name": "Tata Chemicals Ltd"},
        {"symbol": "DEEPAKNTR", "name": "Deepak Nitrite Ltd"},
        {"symbol": "FINEORG", "name": "Fine Organic Industries Ltd"},
    ]


def get_symbol_list(force_refresh: bool = False) -> list[dict]:
    """Returns the full NSE symbol list, using cache if available."""
    now = time.time()
    
    # Try cache first
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
            if now - cached.get("timestamp", 0) < CACHE_TTL:
                return cached["symbols"]
        except Exception:
            pass

    # Fetch live from NSE
    symbols = _fetch_from_nse()
    
    if len(symbols) < 100:
        # Fallback to built-in list if NSE fetch failed or returned too few
        symbols = _load_builtin_fallback()
    
    # Save to cache
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"timestamp": now, "symbols": symbols}, f)
    except Exception:
        pass
    
    return symbols


def search_symbols(query: str, limit: int = 10) -> list[dict]:
    """Fuzzy search over the NSE symbol list."""
    if not query or len(query) < 1:
        return []
    
    q = query.upper().strip()
    all_symbols = get_symbol_list()
    
    # Priority 1: symbol starts with query
    starts = [s for s in all_symbols if s["symbol"].startswith(q)]
    # Priority 2: name contains query (case insensitive)
    name_match = [s for s in all_symbols if q in s["name"].upper() and s not in starts]
    # Priority 3: symbol contains query
    sym_contains = [s for s in all_symbols if q in s["symbol"] and s not in starts and s not in name_match]
    
    results = (starts + name_match + sym_contains)[:limit]
    return results
