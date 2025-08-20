"""
Base Agent class for Economic Analysis
"""

import logging
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from fredapi import Fred
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

class BaseEconomicAgent(ABC):
    """
    Abstract base class for all economic analysis agents
    """
    
    def __init__(self, name: str, fred_api_key: str):
        """
        Initialize the base economic agent
        
        Args:
            name (str): Name of the agent
            fred_api_key (str): FRED API key
        """
        self.name = name
        self.fred = Fred(api_key=fred_api_key)
        self.logger = self._setup_logger()
        self.data_cache = {}
        self.analysis_results = {}
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the agent"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def fetch_data(self, series_id: str, start_date: str, end_date: str) -> pd.Series:
        """
        Fetch data from FRED API
        
        Args:
            series_id (str): FRED series ID
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            pd.Series: Time series data
        """
        try:
            cache_key = f"{series_id}_{start_date}_{end_date}"
            
            if cache_key in self.data_cache:
                self.logger.info(f"Using cached data for {series_id}")
                return self.data_cache[cache_key]
            
            self.logger.info(f"Fetching {series_id} from FRED API")
            data = self.fred.get_series(series_id, start=start_date, end=end_date)
            
            # Cache the data
            self.data_cache[cache_key] = data
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {series_id}: {str(e)}")
            return pd.Series()
    
    def calculate_growth_rate(self, data: pd.Series, periods: int = 12) -> pd.Series:
        """
        Calculate year-over-year growth rate
        
        Args:
            data (pd.Series): Input data
            periods (int): Number of periods for growth calculation
            
        Returns:
            pd.Series: Growth rate series
        """
        return data.pct_change(periods=periods) * 100
    
    def calculate_moving_average(self, data: pd.Series, window: int = 12) -> pd.Series:
        """
        Calculate moving average
        
        Args:
            data (pd.Series): Input data
            window (int): Window size for moving average
            
        Returns:
            pd.Series: Moving average series
        """
        return data.rolling(window=window).mean()
    
    def calculate_volatility(self, data: pd.Series, window: int = 30) -> pd.Series:
        """
        Calculate rolling volatility
        
        Args:
            data (pd.Series): Input data
            window (int): Window size for volatility calculation
            
        Returns:
            pd.Series: Volatility series
        """
        returns = data.pct_change()
        return returns.rolling(window=window).std() * np.sqrt(252)  # Annualized volatility
    
    def get_latest_value(self, data: pd.Series) -> float:
        """Get the latest available value from the series"""
        return data.dropna().iloc[-1] if not data.empty else np.nan
    
    def get_summary_stats(self, data: pd.Series) -> Dict:
        """
        Calculate summary statistics for the data
        
        Args:
            data (pd.Series): Input data
            
        Returns:
            Dict: Summary statistics
        """
        clean_data = data.dropna()
        
        if clean_data.empty:
            return {}
        
        return {
            'mean': clean_data.mean(),
            'median': clean_data.median(),
            'std': clean_data.std(),
            'min': clean_data.min(),
            'max': clean_data.max(),
            'latest': clean_data.iloc[-1],
            'count': len(clean_data),
            'start_date': clean_data.index[0].strftime('%Y-%m-%d'),
            'end_date': clean_data.index[-1].strftime('%Y-%m-%d')
        }
    
    def save_chart(self, fig, filename: str, output_dir: str = 'charts'):
        """
        Save matplotlib figure to file
        
        Args:
            fig: Matplotlib figure object
            filename (str): Output filename
            output_dir (str): Output directory
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{self.name}_{filename}")
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        self.logger.info(f"Chart saved to {filepath}")
    
    def save_data(self, data: pd.DataFrame, filename: str, output_dir: str = 'data'):
        """
        Save data to CSV file
        
        Args:
            data (pd.DataFrame): Data to save
            filename (str): Output filename
            output_dir (str): Output directory
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{self.name}_{filename}")
        data.to_csv(filepath)
        self.logger.info(f"Data saved to {filepath}")
    
    @abstractmethod
    def collect_data(self, start_date: str, end_date: str) -> Dict[str, pd.Series]:
        """
        Collect relevant economic data
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            Dict[str, pd.Series]: Dictionary of collected data series
        """
        pass
    
    @abstractmethod
    def analyze_data(self, data: Dict[str, pd.Series]) -> Dict:
        """
        Perform analysis on the collected data
        
        Args:
            data (Dict[str, pd.Series]): Dictionary of data series
            
        Returns:
            Dict: Analysis results
        """
        pass
    
    @abstractmethod
    def generate_insights(self, analysis_results: Dict) -> Dict:
        """
        Generate insights from analysis results
        
        Args:
            analysis_results (Dict): Results from data analysis
            
        Returns:
            Dict: Generated insights
        """
        pass
    
    @abstractmethod
    def create_visualizations(self, data: Dict[str, pd.Series], analysis_results: Dict):
        """
        Create visualizations for the analysis
        
        Args:
            data (Dict[str, pd.Series]): Dictionary of data series
            analysis_results (Dict): Analysis results
        """
        pass
    
    def run_analysis(self, start_date: str, end_date: str) -> Dict:
        """
        Run complete analysis pipeline
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            Dict: Complete analysis results including insights
        """
        self.logger.info(f"Starting {self.name} analysis from {start_date} to {end_date}")
        
        # Collect data
        data = self.collect_data(start_date, end_date)
        
        if not data:
            self.logger.warning(f"No data collected for {self.name}")
            return {}
        
        # Analyze data
        analysis_results = self.analyze_data(data)
        
        # Generate insights
        insights = self.generate_insights(analysis_results)
        
        # Create visualizations
        self.create_visualizations(data, analysis_results)
        
        # Combine results
        complete_results = {
            'agent_name': self.name,
            'analysis_period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'data_summary': {key: self.get_summary_stats(series) for key, series in data.items()},
            'analysis_results': analysis_results,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache results
        self.analysis_results = complete_results
        
        self.logger.info(f"Completed {self.name} analysis")
        
        return complete_results