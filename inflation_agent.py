"""
Inflation Agent for Economic Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
from base_agent import BaseEconomicAgent
from config import FRED_SERIES

class InflationAgent(BaseEconomicAgent):
    """
    Agent specialized in inflation analysis
    """
    
    def __init__(self, fred_api_key: str):
        """
        Initialize the Inflation Agent
        
        Args:
            fred_api_key (str): FRED API key
        """
        super().__init__("InflationAgent", fred_api_key)
        self.inflation_series = FRED_SERIES['inflation']
        
    def collect_data(self, start_date: str, end_date: str) -> Dict[str, pd.Series]:
        """
        Collect inflation-related data from FRED
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            Dict[str, pd.Series]: Dictionary of inflation data series
        """
        self.logger.info("Collecting inflation data...")
        
        data = {}
        
        for name, series_id in self.inflation_series.items():
            try:
                series_data = self.fetch_data(series_id, start_date, end_date)
                if not series_data.empty:
                    data[name] = series_data
                    self.logger.info(f"Collected {len(series_data)} data points for {name}")
                else:
                    self.logger.warning(f"No data available for {name} ({series_id})")
                    
            except Exception as e:
                self.logger.error(f"Error collecting {name} data: {str(e)}")
        
        return data
    
    def analyze_data(self, data: Dict[str, pd.Series]) -> Dict:
        """
        Perform inflation analysis
        
        Args:
            data (Dict[str, pd.Series]): Dictionary of inflation data series
            
        Returns:
            Dict: Analysis results
        """
        self.logger.info("Analyzing inflation data...")
        
        analysis = {}
        
        # Calculate inflation rates (year-over-year changes)
        inflation_rates = {}
        for name, series in data.items():
            if name in ['cpi_all', 'core_cpi', 'pce', 'core_pce']:
                # Calculate YoY percentage change for price indices
                inflation_rates[f"{name}_rate"] = self.calculate_growth_rate(series, periods=12)
            else:
                # For other series, use as-is
                inflation_rates[name] = series
        
        analysis['inflation_rates'] = inflation_rates
        
        # Current inflation levels
        current_levels = {}
        for name, series in inflation_rates.items():
            current_levels[name] = self.get_latest_value(series)
        
        analysis['current_levels'] = current_levels
        
        # Historical averages
        historical_averages = {}
        for name, series in inflation_rates.items():
            clean_series = series.dropna()
            if not clean_series.empty:
                historical_averages[name] = {
                    'all_time': clean_series.mean(),
                    '5_year': clean_series.tail(60).mean(),  # Last 5 years (monthly data)
                    '1_year': clean_series.tail(12).mean()   # Last 1 year
                }
        
        analysis['historical_averages'] = historical_averages
        
        # Volatility analysis
        volatility_analysis = {}
        for name, series in inflation_rates.items():
            clean_series = series.dropna()
            if len(clean_series) > 12:
                volatility_analysis[name] = {
                    'standard_deviation': clean_series.std(),
                    'coefficient_variation': clean_series.std() / abs(clean_series.mean()) if clean_series.mean() != 0 else np.nan,
                    'rolling_volatility': self.calculate_volatility(clean_series, window=12)
                }
        
        analysis['volatility'] = volatility_analysis
        
        # Trend analysis
        trend_analysis = {}
        for name, series in inflation_rates.items():
            clean_series = series.dropna()
            if len(clean_series) > 24:  # At least 2 years of data
                # Calculate 12-month moving average
                ma_12 = self.calculate_moving_average(clean_series, window=12)
                
                # Determine trend direction (last 6 months vs previous 6 months)
                recent_avg = ma_12.tail(6).mean()
                previous_avg = ma_12.tail(12).head(6).mean()
                
                trend_analysis[name] = {
                    'moving_average_12m': ma_12,
                    'recent_average': recent_avg,
                    'previous_average': previous_avg,
                    'trend_direction': 'increasing' if recent_avg > previous_avg else 'decreasing',
                    'trend_magnitude': abs(recent_avg - previous_avg)
                }
        
        analysis['trends'] = trend_analysis
        
        # Core vs Headline inflation comparison
        if 'cpi_all_rate' in inflation_rates and 'core_cpi_rate' in inflation_rates:
            cpi_all = inflation_rates['cpi_all_rate'].dropna()
            core_cpi = inflation_rates['core_cpi_rate'].dropna()
            
            # Align the series
            common_dates = cpi_all.index.intersection(core_cpi.index)
            if len(common_dates) > 0:
                cpi_aligned = cpi_all.loc[common_dates]
                core_aligned = core_cpi.loc[common_dates]
                
                analysis['core_vs_headline'] = {
                    'correlation': cpi_aligned.corr(core_aligned),
                    'average_difference': (cpi_aligned - core_aligned).mean(),
                    'current_difference': cpi_aligned.iloc[-1] - core_aligned.iloc[-1] if len(cpi_aligned) > 0 else np.nan
                }
        
        return analysis
    
    def generate_insights(self, analysis_results: Dict) -> Dict:
        """
        Generate insights from inflation analysis
        
        Args:
            analysis_results (Dict): Results from inflation analysis
            
        Returns:
            Dict: Generated insights
        """
        self.logger.info("Generating inflation insights...")
        
        insights = {
            'summary': {},
            'alerts': [],
            'observations': []
        }
        
        current_levels = analysis_results.get('current_levels', {})
        historical_averages = analysis_results.get('historical_averages', {})
        trends = analysis_results.get('trends', {})
        
        # Current inflation assessment
        if 'cpi_all_rate' in current_levels:
            current_cpi = current_levels['cpi_all_rate']
            if not np.isnan(current_cpi):
                insights['summary']['current_headline_inflation'] = f"{current_cpi:.2f}%"
                
                # Compare to historical average
                if 'cpi_all_rate' in historical_averages:
                    hist_avg = historical_averages['cpi_all_rate']['all_time']
                    if current_cpi > hist_avg * 1.5:
                        insights['alerts'].append(f"High inflation alert: Current CPI inflation ({current_cpi:.2f}%) is significantly above historical average ({hist_avg:.2f}%)")
                    elif current_cpi < 0:
                        insights['alerts'].append(f"Deflation alert: Current CPI inflation is negative ({current_cpi:.2f}%)")
        
        if 'core_cpi_rate' in current_levels:
            current_core = current_levels['core_cpi_rate']
            if not np.isnan(current_core):
                insights['summary']['current_core_inflation'] = f"{current_core:.2f}%"
        
        # Federal Reserve target analysis (2% inflation target)
        fed_target = 2.0
        if 'pce_rate' in current_levels:  # Fed uses PCE for target
            current_pce = current_levels['pce_rate']
            if not np.isnan(current_pce):
                distance_from_target = current_pce - fed_target
                insights['summary']['distance_from_fed_target'] = f"{distance_from_target:+.2f} percentage points"
                
                if abs(distance_from_target) > 1.0:
                    insights['alerts'].append(f"Fed target deviation: PCE inflation ({current_pce:.2f}%) is {abs(distance_from_target):.2f} percentage points away from Fed's 2% target")
        
        # Trend insights
        for name, trend_data in trends.items():
            if 'trend_direction' in trend_data:
                direction = trend_data['trend_direction']
                magnitude = trend_data.get('trend_magnitude', 0)
                
                if magnitude > 0.5:  # Significant trend change
                    readable_name = name.replace('_rate', '').replace('_', ' ').title()
                    insights['observations'].append(f"{readable_name} is {direction} with magnitude of {magnitude:.2f} percentage points")
        
        # Volatility insights
        volatility_data = analysis_results.get('volatility', {})
        for name, vol_data in volatility_data.items():
            coef_var = vol_data.get('coefficient_variation', np.nan)
            if not np.isnan(coef_var) and coef_var > 0.5:
                readable_name = name.replace('_rate', '').replace('_', ' ').title()
                insights['observations'].append(f"{readable_name} shows high volatility (coefficient of variation: {coef_var:.2f})")
        
        # Core vs Headline comparison
        if 'core_vs_headline' in analysis_results:
            comparison = analysis_results['core_vs_headline']
            current_diff = comparison.get('current_difference', np.nan)
            if not np.isnan(current_diff):
                if current_diff > 1.0:
                    insights['observations'].append(f"Headline inflation is {current_diff:.2f} percentage points above core inflation, suggesting food/energy price pressures")
                elif current_diff < -1.0:
                    insights['observations'].append(f"Core inflation is {abs(current_diff):.2f} percentage points above headline inflation, suggesting underlying price pressures")
        
        return insights
    
    def create_visualizations(self, data: Dict[str, pd.Series], analysis_results: Dict):
        """
        Create inflation visualizations
        
        Args:
            data (Dict[str, pd.Series]): Dictionary of inflation data series
            analysis_results (Dict): Analysis results
        """
        self.logger.info("Creating inflation visualizations...")
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        inflation_rates = analysis_results.get('inflation_rates', {})
        
        # 1. Inflation Rates Time Series
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Inflation Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # Main inflation measures
        ax1 = axes[0, 0]
        main_measures = ['cpi_all_rate', 'core_cpi_rate', 'pce_rate', 'core_pce_rate']
        for measure in main_measures:
            if measure in inflation_rates:
                series = inflation_rates[measure].dropna()
                if not series.empty:
                    ax1.plot(series.index, series.values, label=measure.replace('_', ' ').title(), linewidth=2)
        
        ax1.axhline(y=2.0, color='red', linestyle='--', alpha=0.7, label='Fed Target (2%)')
        ax1.set_title('Key Inflation Measures', fontweight='bold')
        ax1.set_ylabel('Inflation Rate (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Historical comparison (last 5 years)
        ax2 = axes[0, 1]
        if 'cpi_all_rate' in inflation_rates:
            recent_data = inflation_rates['cpi_all_rate'].dropna().tail(60)  # Last 5 years
            if not recent_data.empty:
                ax2.plot(recent_data.index, recent_data.values, linewidth=2, color='blue')
                ax2.fill_between(recent_data.index, recent_data.values, alpha=0.3, color='blue')
        
        ax2.axhline(y=2.0, color='red', linestyle='--', alpha=0.7, label='Fed Target')
        ax2.set_title('CPI Inflation - Last 5 Years', fontweight='bold')
        ax2.set_ylabel('Inflation Rate (%)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Volatility analysis
        ax3 = axes[1, 0]
        volatility_data = analysis_results.get('volatility', {})
        if 'cpi_all_rate' in volatility_data:
            rolling_vol = volatility_data['cpi_all_rate'].get('rolling_volatility')
            if rolling_vol is not None and not rolling_vol.empty:
                vol_clean = rolling_vol.dropna()
                ax3.plot(vol_clean.index, vol_clean.values, color='orange', linewidth=2)
                ax3.fill_between(vol_clean.index, vol_clean.values, alpha=0.3, color='orange')
        
        ax3.set_title('CPI Inflation Volatility (12M Rolling)', fontweight='bold')
        ax3.set_ylabel('Volatility')
        ax3.grid(True, alpha=0.3)
        
        # Current levels bar chart
        ax4 = axes[1, 1]
        current_levels = analysis_results.get('current_levels', {})
        measures_to_plot = ['cpi_all_rate', 'core_cpi_rate', 'pce_rate', 'core_pce_rate']
        
        values = []
        labels = []
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        for i, measure in enumerate(measures_to_plot):
            if measure in current_levels and not np.isnan(current_levels[measure]):
                values.append(current_levels[measure])
                labels.append(measure.replace('_rate', '').replace('_', ' ').upper())
        
        if values:
            bars = ax4.bar(labels, values, color=colors[:len(values)])
            ax4.axhline(y=2.0, color='red', linestyle='--', alpha=0.7, label='Fed Target')
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax4.set_title('Current Inflation Levels', fontweight='bold')
        ax4.set_ylabel('Inflation Rate (%)')
        ax4.tick_params(axis='x', rotation=45)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self.save_chart(fig, 'inflation_dashboard.png')
        plt.close()
        
        # 2. Core vs Headline Inflation Comparison
        if 'core_vs_headline' in analysis_results:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            if 'cpi_all_rate' in inflation_rates and 'core_cpi_rate' in inflation_rates:
                headline = inflation_rates['cpi_all_rate'].dropna()
                core = inflation_rates['core_cpi_rate'].dropna()
                
                # Align series
                common_dates = headline.index.intersection(core.index)
                if len(common_dates) > 0:
                    headline_aligned = headline.loc[common_dates]
                    core_aligned = core.loc[common_dates]
                    
                    # Time series comparison
                    ax1.plot(headline_aligned.index, headline_aligned.values, 
                            label='Headline CPI', linewidth=2, color='blue')
                    ax1.plot(core_aligned.index, core_aligned.values, 
                            label='Core CPI', linewidth=2, color='green')
                    ax1.axhline(y=2.0, color='red', linestyle='--', alpha=0.7, label='Fed Target')
                    
                    ax1.set_title('Headline vs Core CPI Inflation', fontsize=14, fontweight='bold')
                    ax1.set_ylabel('Inflation Rate (%)')
                    ax1.legend()
                    ax1.grid(True, alpha=0.3)
                    
                    # Difference plot
                    difference = headline_aligned - core_aligned
                    ax2.plot(difference.index, difference.values, linewidth=2, color='purple')
                    ax2.fill_between(difference.index, difference.values, alpha=0.3, color='purple')
                    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
                    
                    ax2.set_title('Headline vs Core CPI Difference', fontsize=14, fontweight='bold')
                    ax2.set_ylabel('Difference (Headline - Core) %')
                    ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            self.save_chart(fig, 'core_vs_headline_comparison.png')
            plt.close()
        
        # 3. Inflation Distribution Analysis
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Histogram of inflation rates
        if 'cpi_all_rate' in inflation_rates:
            cpi_data = inflation_rates['cpi_all_rate'].dropna()
            if not cpi_data.empty:
                ax1.hist(cpi_data.values, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
                ax1.axvline(x=cpi_data.mean(), color='red', linestyle='--', 
                           label=f'Mean: {cpi_data.mean():.2f}%', linewidth=2)
                ax1.axvline(x=2.0, color='green', linestyle='--', 
                           label='Fed Target: 2.0%', linewidth=2)
                
                ax1.set_title('CPI Inflation Distribution', fontweight='bold')
                ax1.set_xlabel('Inflation Rate (%)')
                ax1.set_ylabel('Frequency')
                ax1.legend()
                ax1.grid(True, alpha=0.3)
        
        # Box plot comparison
        box_data = []
        box_labels = []
        for measure in ['cpi_all_rate', 'core_cpi_rate', 'pce_rate', 'core_pce_rate']:
            if measure in inflation_rates:
                clean_data = inflation_rates[measure].dropna()
                if not clean_data.empty:
                    box_data.append(clean_data.values)
                    box_labels.append(measure.replace('_rate', '').replace('_', ' ').upper())
        
        if box_data:
            bp = ax2.boxplot(box_data, labels=box_labels, patch_artist=True)
            colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
            for patch, color in zip(bp['boxes'], colors[:len(bp['boxes'])]):
                patch.set_facecolor(color)
            
            ax2.axhline(y=2.0, color='red', linestyle='--', alpha=0.7, label='Fed Target')
            ax2.set_title('Inflation Measures Comparison', fontweight='bold')
            ax2.set_ylabel('Inflation Rate (%)')
            ax2.tick_params(axis='x', rotation=45)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self.save_chart(fig, 'inflation_distribution.png')
        plt.close()
        
        # Save processed data
        if inflation_rates:
            df = pd.DataFrame(inflation_rates)
            self.save_data(df, 'inflation_data.csv')
        
        self.logger.info("Inflation visualizations completed")