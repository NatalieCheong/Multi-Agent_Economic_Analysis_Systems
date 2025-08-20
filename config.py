"""
Configuration file for Multi-Agent Economy Analysis System
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# FRED API Configuration
FRED_API_KEY = os.getenv('FRED_API_KEY', 'YOUR_FRED_API_KEY_HERE')

# Data Configuration
DEFAULT_START_DATE = (datetime.now() - timedelta(days=365*10)).strftime('%Y-%m-%d')  # 10 years ago
DEFAULT_END_DATE = datetime.now().strftime('%Y-%m-%d')

# FRED Series IDs for Economic Indicators
FRED_SERIES = {
    'inflation': {
        'cpi_all': 'CPIAUCSL',           # Consumer Price Index for All Urban Consumers
        'core_cpi': 'CPILFESL',         # Core CPI (Less Food and Energy)
        'pce': 'PCEPI',                 # Personal Consumption Expenditures Price Index
        'core_pce': 'PCEPILFE',         # Core PCE Price Index
        'producer_price': 'PPIACO',     # Producer Price Index
    },
    'gdp': {
        'real_gdp': 'GDPC1',            # Real GDP
        'nominal_gdp': 'GDP',           # Nominal GDP
        'gdp_growth': 'A191RL1Q225SBEA', # Real GDP Growth Rate
        'gdp_per_capita': 'A939RX0Q048SBEA', # Real GDP Per Capita
        'gdp_deflator': 'GDPDEF',       # GDP Deflator
    },
    'trade': {
        'exports': 'EXPGS',             # Exports of Goods and Services
        'imports': 'IMPGS',             # Imports of Goods and Services
        'trade_balance': 'BOPGSTB',     # Trade Balance: Goods and Services
        #'export_price_index': 'EXPPI',  # Export Price Index
        #'import_price_index': 'IMPPI',  # Import Price Index
        #'export_price_index': 'XXXXXX',
        #'import_price_index': 'YYYYYY'
        'export_price_index': 'EXPGSC1',  # Exports Price Index (if available)
        'import_price_index': 'IMPGSC1',  # Imports Price Index (if available)
    }
}

# Analysis Configuration
ANALYSIS_PERIODS = ['1Y', '3Y', '5Y', '10Y']
CORRELATION_THRESHOLD = 0.7
VOLATILITY_WINDOW = 30

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Output Configuration
OUTPUT_DIR = 'output'
CHARTS_DIR = f'{OUTPUT_DIR}/charts'
DATA_DIR = f'{OUTPUT_DIR}/data'
REPORTS_DIR = f'{OUTPUT_DIR}/reports'