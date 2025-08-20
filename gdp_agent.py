"""
GDP Agent for Economic Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
from base_agent import BaseEconomicAgent
from config import FRED_SERIES

class GDPAgent(BaseEconomicAgent):
    """
    Agent specialized in GDP and economic growth analysis
    """
    
    def __init__(self, fred_api_key: str):
        """
        Initialize the GDP Agent
        
        Args:
            fred_api_key (str): FRED API key
        """
        super().__init__("GDPAgent", fred_api_key)
        self.gdp_series = FRED_SERIES['gdp']
        
    def collect_data(self, start_date: str, end_date: str) -> Dict[str, pd.Series]:
        """
        Collect GDP-related data from FRED
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            Dict[str, pd.Series]: Dictionary of GDP data series
        """
        self.logger.info("Collecting GDP data...")
        
        data = {}
        
        for name, series_id in self.gdp_series.items():
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
        Perform GDP analysis
        
        Args:
            data (Dict[str, pd.Series]): Dictionary of GDP data series
            
        Returns:
            Dict: Analysis results
        """
        self.logger.info("Analyzing GDP data...")
        
        analysis = {}
        
        # Calculate growth rates
        growth_rates = {}
        
        # For level data (real_gdp, nominal_gdp, gdp_per_capita), calculate QoQ and YoY growth
        level_series = ['real_gdp', 'nominal_gdp', 'gdp_per_capita']
        for name in level_series:
            if name in data:
                series = data[name]
                # Quarterly growth rate (annualized)
                growth_rates[f"{name}_qoq"] = (series.pct_change() * 4) * 100  # Annualized quarterly growth
                # Year-over-year growth rate
                growth_rates[f"{name}_yoy"] = self.calculate_growth_rate(series, periods=4) # 4 quarters = 1 year
        
        # GDP growth rate series is already in growth format
        if 'gdp_growth' in data:
            growth_rates['gdp_growth_official'] = data['gdp_growth']
        
        analysis['growth_rates'] = growth_rates
        
        # Current levels and latest values
        current_values = {}
        for name, series in data.items():
            current_values[name] = self.get_latest_value(series)
            
        for name, series in growth_rates.items():
            current_values[name] = self.get_latest_value(series)
            
        analysis['current_values'] = current_values
        
        # Historical growth analysis
        historical_analysis = {}
        for name, series in growth_rates.items():
            clean_series = series.dropna()
            if not clean_series.empty:
                historical_analysis[name] = {
                    'average_growth': clean_series.mean(),
                    'median_growth': clean_series.median(),
                    'volatility': clean_series.std(),
                    'min_growth': clean_series.min(),
                    'max_growth': clean_series.max(),
                    'positive_quarters': (clean_series > 0).sum(),
                    'negative_quarters': (clean_series < 0).sum(),
                    'total_quarters': len(clean_series)
                }
                
                # Recession indicators (2 consecutive quarters of negative growth)
                if len(clean_series) > 1:
                    negative_consecutive = []
                    count = 0
                    for value in clean_series:
                        if value < 0:
                            count += 1
                        else:
                            if count >= 2:
                                negative_consecutive.append(count)
                            count = 0
                    if count >= 2:  # Handle case where recession continues to end
                        negative_consecutive.append(count)
                    
                    historical_analysis[name]['recession_periods'] = negative_consecutive
                    historical_analysis[name]['recession_quarters'] = sum(negative_consecutive)
        
        analysis['historical_analysis'] = historical_analysis
        
        # Business cycle analysis
        if 'real_gdp_yoy' in growth_rates:
            real_gdp_growth = growth_rates['real_gdp_yoy'].dropna()
            if not real_gdp_growth.empty:
                # Identify expansion and contraction periods
                business_cycle = self._analyze_business_cycle(real_gdp_growth)
                analysis['business_cycle'] = business_cycle
        
        # GDP components analysis (if available)
        if 'real_gdp' in data and 'nominal_gdp' in data:
            real_gdp = data['real_gdp']
            nominal_gdp = data['nominal_gdp']
            
            # Calculate implied GDP deflator growth
            common_dates = real_gdp.index.intersection(nominal_gdp.index)
            if len(common_dates) > 0:
                real_aligned = real_gdp.loc[common_dates]
                nominal_aligned = nominal_gdp.loc[common_dates]
                
                # GDP deflator (implicit price deflator)
                implied_deflator = (nominal_aligned / real_aligned) * 100
                deflator_growth = self.calculate_growth_rate(implied_deflator, periods=4)
                
                analysis['price_analysis'] = {
                    'implied_deflator': implied_deflator,
                    'deflator_growth': deflator_growth,
                    'current_deflator_growth': self.get_latest_value(deflator_growth)
                }
        
        # Productivity analysis (GDP per capita trends)
        if 'gdp_per_capita_yoy' in growth_rates:
            productivity_growth = growth_rates['gdp_per_capita_yoy'].dropna()
            if not productivity_growth.empty:
                analysis['productivity_analysis'] = {
                    'average_productivity_growth': productivity_growth.mean(),
                    'recent_productivity_trend': productivity_growth.tail(8).mean(),  # Last 2 years
                    'productivity_volatility': productivity_growth.std(),
                    'moving_average': self.calculate_moving_average(productivity_growth, window=8)
                }
        
        # Economic strength indicators
        strength_indicators = {}
        if 'real_gdp_yoy' in growth_rates:
            latest_growth = current_values.get('real_gdp_yoy', np.nan)
            avg_growth = historical_analysis.get('real_gdp_yoy', {}).get('average_growth', np.nan)
            
            if not np.isnan(latest_growth) and not np.isnan(avg_growth):
                strength_indicators['growth_relative_to_average'] = latest_growth - avg_growth
                strength_indicators['growth_percentile'] = self._calculate_percentile(
                    growth_rates['real_gdp_yoy'], latest_growth
                )
        
        analysis['strength_indicators'] = strength_indicators
        
        return analysis
    
    def _analyze_business_cycle(self, growth_series: pd.Series) -> Dict:
        """
        Analyze business cycle phases
        
        Args:
            growth_series (pd.Series): GDP growth rate series
            
        Returns:
            Dict: Business cycle analysis
        """
        # Simple business cycle identification
        # Expansion: positive growth, Contraction: negative growth
        # Peak: transition from positive to negative
        # Trough: transition from negative to positive
        
        cycle_analysis = {
            'current_phase': 'unknown',
            'phase_duration': 0,
            'phases': [],
            'average_expansion_length': 0,
            'average_contraction_length': 0
        }
        
        if len(growth_series) < 2:
            return cycle_analysis
        
        # Identify phases
        phases = []
        current_phase = 'expansion' if growth_series.iloc[0] >= 0 else 'contraction'
        phase_start = growth_series.index[0]
        
        for i in range(1, len(growth_series)):
            if growth_series.iloc[i] >= 0 and current_phase == 'contraction':
                # End contraction, start expansion
                phases.append({
                    'phase': current_phase,
                    'start': phase_start,
                    'end': growth_series.index[i-1],
                    'duration': i - phases.__len__() if phases else i
                })
                current_phase = 'expansion'
                phase_start = growth_series.index[i]
            elif growth_series.iloc[i] < 0 and current_phase == 'expansion':
                # End expansion, start contraction
                phases.append({
                    'phase': current_phase,
                    'start': phase_start,
                    'end': growth_series.index[i-1],
                    'duration': i - sum(1 for p in phases)
                })
                current_phase = 'contraction'
                phase_start = growth_series.index[i]
        
        # Add current ongoing phase
        phases.append({
            'phase': current_phase,
            'start': phase_start,
            'end': growth_series.index[-1],
            'duration': len(growth_series) - sum(p.get('duration', 0) for p in phases)
        })
        
        cycle_analysis['phases'] = phases
        cycle_analysis['current_phase'] = current_phase
        cycle_analysis['phase_duration'] = phases[-1]['duration'] if phases else 0
        
        # Calculate average phase lengths
        expansions = [p['duration'] for p in phases if p['phase'] == 'expansion']
        contractions = [p['duration'] for p in phases if p['phase'] == 'contraction']
        
        cycle_analysis['average_expansion_length'] = np.mean(expansions) if expansions else 0
        cycle_analysis['average_contraction_length'] = np.mean(contractions) if contractions else 0
        
        return cycle_analysis
    
    def _calculate_percentile(self, series: pd.Series, value: float) -> float:
        """Calculate what percentile a value represents in a series"""
        clean_series = series.dropna()
        if clean_series.empty:
            return np.nan
        return (clean_series < value).mean() * 100
    
    def generate_insights(self, analysis_results: Dict) -> Dict:
        """
        Generate insights from GDP analysis
        
        Args:
            analysis_results (Dict): Results from GDP analysis
            
        Returns:
            Dict: Generated insights
        """
        self.logger.info("Generating GDP insights...")
        
        insights = {
            'summary': {},
            'alerts': [],
            'observations': [],
            'economic_assessment': {}
        }
        
        current_values = analysis_results.get('current_values', {})
        historical_analysis = analysis_results.get('historical_analysis', {})
        business_cycle = analysis_results.get('business_cycle', {})
        strength_indicators = analysis_results.get('strength_indicators', {})
        
        # Current GDP growth assessment
        if 'real_gdp_yoy' in current_values:
            current_growth = current_values['real_gdp_yoy']
            if not np.isnan(current_growth):
                insights['summary']['current_gdp_growth'] = f"{current_growth:.2f}%"
                
                # Growth classification
                if current_growth < 0:
                    insights['economic_assessment']['growth_status'] = 'Contraction'
                    insights['alerts'].append(f"Economic contraction: GDP declining at {current_growth:.2f}% annual rate")
                elif current_growth < 1.0:
                    insights['economic_assessment']['growth_status'] = 'Slow Growth'
                    insights['observations'].append(f"Slow economic growth: GDP growing at {current_growth:.2f}% annual rate")
                elif current_growth < 3.0:
                    insights['economic_assessment']['growth_status'] = 'Moderate Growth'
                elif current_growth < 5.0:
                    insights['economic_assessment']['growth_status'] = 'Strong Growth'
                else:
                    insights['economic_assessment']['growth_status'] = 'Very Strong Growth'
                    insights['observations'].append(f"Exceptionally strong growth: GDP growing at {current_growth:.2f}% annual rate")
        
        # Historical comparison
        if 'real_gdp_yoy' in historical_analysis:
            hist_data = historical_analysis['real_gdp_yoy']
            avg_growth = hist_data.get('average_growth', np.nan)
            
            if not np.isnan(avg_growth):
                insights['summary']['historical_average_growth'] = f"{avg_growth:.2f}%"
                
                # Compare current to historical average
                if 'real_gdp_yoy' in current_values:
                    current_growth = current_values['real_gdp_yoy']
                    if not np.isnan(current_growth):
                        deviation = current_growth - avg_growth
                        insights['summary']['growth_vs_historical'] = f"{deviation:+.2f} pp vs historical average"
                        
                        if abs(deviation) > 2.0:
                            if deviation > 0:
                                insights['observations'].append(f"Growth significantly above historical average (+{deviation:.2f} percentage points)")
                            else:
                                insights['observations'].append(f"Growth significantly below historical average ({deviation:.2f} percentage points)")
        
        # Business cycle insights
        if business_cycle:
            current_phase = business_cycle.get('current_phase', 'unknown')
            phase_duration = business_cycle.get('phase_duration', 0)
            
            insights['economic_assessment']['business_cycle_phase'] = current_phase.title()
            insights['summary']['cycle_phase_duration'] = f"{phase_duration} quarters"
            
            if current_phase == 'contraction':
                insights['alerts'].append(f"Economy in contraction phase for {phase_duration} quarters")
                
                # Check for technical recession (2+ quarters)
                if phase_duration >= 2:
                    insights['alerts'].append("Technical recession: 2+ consecutive quarters of negative growth")
            
            elif current_phase == 'expansion':
                avg_expansion = business_cycle.get('average_expansion_length', 0)
                if phase_duration > avg_expansion * 1.5:
                    insights['observations'].append(f"Extended expansion: Current expansion ({phase_duration} quarters) is longer than historical average")
        
        # Productivity insights
        productivity_analysis = analysis_results.get('productivity_analysis', {})
        if productivity_analysis:
            avg_productivity = productivity_analysis.get('average_productivity_growth', np.nan)
            recent_productivity = productivity_analysis.get('recent_productivity_trend', np.nan)
            
            if not np.isnan(avg_productivity):
                insights['summary']['average_productivity_growth'] = f"{avg_productivity:.2f}%"
            
            if not np.isnan(recent_productivity) and not np.isnan(avg_productivity):
                productivity_change = recent_productivity - avg_productivity
                if abs(productivity_change) > 0.5:
                    if productivity_change > 0:
                        insights['observations'].append(f"Improving productivity: Recent trend ({recent_productivity:.2f}%) above historical average")
                    else:
                        insights['observations'].append(f"Declining productivity: Recent trend ({recent_productivity:.2f}%) below historical average")
        
        # Recession risk assessment
        recession_risk = self._assess_recession_risk(analysis_results)
        insights['economic_assessment']['recession_risk'] = recession_risk
        
        # Growth strength assessment
        if strength_indicators:
            growth_percentile = strength_indicators.get('growth_percentile', np.nan)
            if not np.isnan(growth_percentile):
                if growth_percentile > 75:
                    insights['observations'].append(f"Growth in top quartile of historical distribution ({growth_percentile:.0f}th percentile)")
                elif growth_percentile < 25:
                    insights['observations'].append(f"Growth in bottom quartile of historical distribution ({growth_percentile:.0f}th percentile)")
        
        # Price pressure insights
        price_analysis = analysis_results.get('price_analysis', {})
        if price_analysis:
            deflator_growth = price_analysis.get('current_deflator_growth', np.nan)
            if not np.isnan(deflator_growth):
                insights['summary']['gdp_deflator_growth'] = f"{deflator_growth:.2f}%"
                if deflator_growth > 4.0:
                    insights['observations'].append(f"High GDP deflator growth ({deflator_growth:.2f}%) suggests broad price pressures")
        
        return insights
    
    def _assess_recession_risk(self, analysis_results: Dict) -> str:
        """Assess recession risk based on current indicators"""
        risk_factors = 0
        
        current_values = analysis_results.get('current_values', {})
        business_cycle = analysis_results.get('business_cycle', {})
        
        # Factor 1: Current growth rate
        if 'real_gdp_yoy' in current_values:
            current_growth = current_values['real_gdp_yoy']
            if not np.isnan(current_growth):
                if current_growth < 0:
                    risk_factors += 3  # Already in contraction
                elif current_growth < 1.0:
                    risk_factors += 2  # Very slow growth
                elif current_growth < 2.0:
                    risk_factors += 1  # Below-trend growth
        
        # Factor 2: Business cycle phase
        if business_cycle:
            if business_cycle.get('current_phase') == 'contraction':
                risk_factors += 2
        
        # Factor 3: Recent trend
        if 'real_gdp_qoq' in current_values:
            recent_qoq = current_values['real_gdp_qoq']
            if not np.isnan(recent_qoq) and recent_qoq < 0:
                risk_factors += 1
        
        # Risk assessment
        if risk_factors >= 5:
            return "Very High"
        elif risk_factors >= 3:
            return "High"
        elif risk_factors >= 2:
            return "Moderate"
        elif risk_factors >= 1:
            return "Low"
        else:
            return "Very Low"
    
    def create_visualizations(self, data: Dict[str, pd.Series], analysis_results: Dict):
        """
        Create GDP visualizations
        
        Args:
            data (Dict[str, pd.Series]): Dictionary of GDP data series
            analysis_results (Dict): Analysis results
        """
        self.logger.info("Creating GDP visualizations...")
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        growth_rates = analysis_results.get('growth_rates', {})
        
        # 1. GDP Growth Dashboard
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('GDP Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # Real GDP level
        ax1 = axes[0, 0]
        if 'real_gdp' in data:
            real_gdp = data['real_gdp'].dropna()
            if not real_gdp.empty:
                ax1.plot(real_gdp.index, real_gdp.values, linewidth=2, color='blue')
                ax1.fill_between(real_gdp.index, real_gdp.values, alpha=0.3, color='blue')
        
        ax1.set_title('Real GDP Level', fontweight='bold')
        ax1.set_ylabel('Billions of Chained 2012 Dollars')
        ax1.grid(True, alpha=0.3)
        
        # GDP Growth Rates
        ax2 = axes[0, 1]
        growth_measures = ['real_gdp_yoy', 'real_gdp_qoq']
        colors = ['green', 'orange']
        
        for i, measure in enumerate(growth_measures):
            if measure in growth_rates:
                series = growth_rates[measure].dropna()
                if not series.empty:
                    label = 'Year-over-Year' if 'yoy' in measure else 'Quarter-over-Quarter (Annualized)'
                    ax2.plot(series.index, series.values, label=label, linewidth=2, color=colors[i])
        
        ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Zero Growth')
        ax2.set_title('GDP Growth Rates', fontweight='bold')
        ax2.set_ylabel('Growth Rate (%)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Business Cycle Visualization
        ax3 = axes[1, 0]
        if 'real_gdp_yoy' in growth_rates:
            yoy_growth = growth_rates['real_gdp_yoy'].dropna()
            if not yoy_growth.empty:
                # Color by expansion/contraction
                expansion_mask = yoy_growth >= 0
                contraction_mask = yoy_growth < 0
                
                if expansion_mask.any():
                    ax3.bar(yoy_growth[expansion_mask].index, yoy_growth[expansion_mask].values,
                           color='green', alpha=0.7, label='Expansion', width=80)
                
                if contraction_mask.any():
                    ax3.bar(yoy_growth[contraction_mask].index, yoy_growth[contraction_mask].values,
                           color='red', alpha=0.7, label='Contraction', width=80)
        
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.8)
        ax3.set_title('Business Cycle (Expansion vs Contraction)', fontweight='bold')
        ax3.set_ylabel('GDP Growth Rate (%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # GDP Per Capita Growth
        ax4 = axes[1, 1]
        if 'gdp_per_capita_yoy' in growth_rates:
            per_capita_growth = growth_rates['gdp_per_capita_yoy'].dropna()
            if not per_capita_growth.empty:
                ax4.plot(per_capita_growth.index, per_capita_growth.values, 
                        linewidth=2, color='purple')
                
                # Add trend line
                productivity_analysis = analysis_results.get('productivity_analysis', {})
                if 'moving_average' in productivity_analysis:
                    ma = productivity_analysis['moving_average'].dropna()
                    ax4.plot(ma.index, ma.values, 
                            linestyle='--', color='red', label='8-Quarter Moving Average')
        
        ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax4.set_title('GDP Per Capita Growth (Productivity)', fontweight='bold')
        ax4.set_ylabel('Growth Rate (%)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self.save_chart(fig, 'gdp_dashboard.png')
        plt.close()
        
        # 2. Real vs Nominal GDP Comparison
        if 'real_gdp' in data and 'nominal_gdp' in data:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            real_gdp = data['real_gdp'].dropna()
            nominal_gdp = data['nominal_gdp'].dropna()
            
            # Levels comparison
            if not real_gdp.empty and not nominal_gdp.empty:
                ax1.plot(real_gdp.index, real_gdp.values, label='Real GDP', linewidth=2, color='blue')
                ax1.plot(nominal_gdp.index, nominal_gdp.values, label='Nominal GDP', linewidth=2, color='green')
                
                ax1.set_title('Real vs Nominal GDP', fontsize=14, fontweight='bold')
                ax1.set_ylabel('Billions of Dollars')
                ax1.legend()
                ax1.grid(True, alpha=0.3)
            
            # GDP Deflator
            price_analysis = analysis_results.get('price_analysis', {})
            if 'deflator_growth' in price_analysis:
                deflator_growth = price_analysis['deflator_growth'].dropna()
                if not deflator_growth.empty:
                    ax2.plot(deflator_growth.index, deflator_growth.values, 
                            linewidth=2, color='red')
                    ax2.axhline(y=2.0, color='black', linestyle='--', alpha=0.7, label='2% Target')
                    
                    ax2.set_title('GDP Deflator Growth', fontsize=14, fontweight='bold')
                    ax2.set_ylabel('Growth Rate (%)')
                    ax2.legend()
                    ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            self.save_chart(fig, 'real_vs_nominal_gdp.png')
            plt.close()
        
        # 3. GDP Growth Distribution and Statistics
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Growth rate distribution
        if 'real_gdp_yoy' in growth_rates:
            growth_data = growth_rates['real_gdp_yoy'].dropna()
            if not growth_data.empty:
                ax1.hist(growth_data.values, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
                ax1.axvline(x=growth_data.mean(), color='red', linestyle='--', 
                           label=f'Mean: {growth_data.mean():.2f}%', linewidth=2)
                ax1.axvline(x=0, color='black', linestyle='--', 
                           label='Zero Growth', linewidth=2)
                
                ax1.set_title('GDP Growth Rate Distribution', fontweight='bold')
                ax1.set_xlabel('Growth Rate (%)')
                ax1.set_ylabel('Frequency')
                ax1.legend()
                ax1.grid(True, alpha=0.3)
        
        # Growth statistics comparison
        historical_analysis = analysis_results.get('historical_analysis', {})
        stats_data = []
        labels = []
        
        for measure in ['real_gdp_yoy', 'real_gdp_qoq', 'gdp_per_capita_yoy']:
            if measure in historical_analysis:
                hist_data = historical_analysis[measure]
                avg_growth = hist_data.get('average_growth', np.nan)
                if not np.isnan(avg_growth):
                    stats_data.append(avg_growth)
                    labels.append(measure.replace('_', ' ').replace('yoy', 'YoY').replace('qoq', 'QoQ').title())
        
        if stats_data:
            bars = ax2.bar(labels, stats_data, color=['lightblue', 'lightgreen', 'lightcoral'][:len(stats_data)])
            ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
            
            # Add value labels on bars
            for bar, value in zip(bars, stats_data):
                ax2.text(bar.get_x() + bar.get_width()/2, 
                        bar.get_height() + (0.1 if bar.get_height() >= 0 else -0.3),
                        f'{value:.1f}%', ha='center', va='bottom' if bar.get_height() >= 0 else 'top', 
                        fontweight='bold')
            
            ax2.set_title('Average Growth Rates Comparison', fontweight='bold')
            ax2.set_ylabel('Average Growth Rate (%)')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self.save_chart(fig, 'gdp_distribution_stats.png')
        plt.close()
        
        # 4. Business Cycle Timeline
        business_cycle = analysis_results.get('business_cycle', {})
        if business_cycle and 'phases' in business_cycle:
            fig, ax = plt.subplots(figsize=(14, 6))
            
            phases = business_cycle['phases']
            if phases and 'real_gdp_yoy' in growth_rates:
                growth_data = growth_rates['real_gdp_yoy'].dropna()
                
                # Plot growth rate
                ax.plot(growth_data.index, growth_data.values, linewidth=2, color='blue', alpha=0.7)
                
                # Shade recession periods
                for phase in phases:
                    if phase['phase'] == 'contraction':
                        ax.axvspan(phase['start'], phase['end'], alpha=0.3, color='red', label='Recession')
                
                # Remove duplicate labels
                handles, labels = ax.get_legend_handles_labels()
                by_label = dict(zip(labels, handles))
                ax.legend(by_label.values(), by_label.keys())
                
                ax.axhline(y=0, color='black', linestyle='--', alpha=0.8)
                ax.set_title('Business Cycle Timeline', fontsize=14, fontweight='bold')
                ax.set_ylabel('GDP Growth Rate (%)')
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            self.save_chart(fig, 'business_cycle_timeline.png')
            plt.close()
        
        # Save processed data
        if growth_rates:
            # Combine original data and calculated growth rates
            all_data = {**data, **growth_rates}
            df = pd.DataFrame(all_data)
            self.save_data(df, 'gdp_data.csv')
        
        self.logger.info("GDP visualizations completed")