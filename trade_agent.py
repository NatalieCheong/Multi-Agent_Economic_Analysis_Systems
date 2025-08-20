"""
Trade Agent for Economic Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
from base_agent import BaseEconomicAgent
from config import FRED_SERIES

class TradeAgent(BaseEconomicAgent):
    """
    Agent specialized in international trade analysis
    """
    
    def __init__(self, fred_api_key: str):
        """
        Initialize the Trade Agent
        
        Args:
            fred_api_key (str): FRED API key
        """
        super().__init__("TradeAgent", fred_api_key)
        self.trade_series = FRED_SERIES['trade']
        
    def collect_data(self, start_date: str, end_date: str) -> Dict[str, pd.Series]:
        """
        Collect trade-related data from FRED
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            Dict[str, pd.Series]: Dictionary of trade data series
        """
        self.logger.info("Collecting trade data...")
        
        data = {}
        
        for name, series_id in self.trade_series.items():
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
        Perform trade analysis
        
        Args:
            data (Dict[str, pd.Series]): Dictionary of trade data series
            
        Returns:
            Dict: Analysis results
        """
        self.logger.info("Analyzing trade data...")
        
        analysis = {}
        
        # Calculate growth rates for trade volumes
        growth_rates = {}
        volume_series = ['exports', 'imports']
        
        for name in volume_series:
            if name in data:
                series = data[name]
                # Month-over-month growth (annualized)
                growth_rates[f"{name}_mom"] = (series.pct_change() * 12) * 100
                # Year-over-year growth
                growth_rates[f"{name}_yoy"] = self.calculate_growth_rate(series, periods=12)
        
        # Price index growth rates
        price_series = ['export_price_index', 'import_price_index']
        for name in price_series:
            if name in data:
                series = data[name]
                growth_rates[f"{name}_yoy"] = self.calculate_growth_rate(series, periods=12)
        
        analysis['growth_rates'] = growth_rates
        
        # Current levels
        current_values = {}
        for name, series in data.items():
            current_values[name] = self.get_latest_value(series)
        
        for name, series in growth_rates.items():
            current_values[name] = self.get_latest_value(series)
        
        analysis['current_values'] = current_values
        
        # Trade balance analysis
        if 'exports' in data and 'imports' in data:
            exports = data['exports']
            imports = data['imports']
            
            # Align the series on common dates
            common_dates = exports.index.intersection(imports.index)
            if len(common_dates) > 0:
                exports_aligned = exports.loc[common_dates]
                imports_aligned = imports.loc[common_dates]
                
                # Calculate trade balance if not provided
                calculated_balance = exports_aligned - imports_aligned
                
                trade_balance_analysis = {
                    'calculated_balance': calculated_balance,
                    'current_balance': calculated_balance.iloc[-1] if len(calculated_balance) > 0 else np.nan,
                    'average_balance': calculated_balance.mean(),
                    'balance_trend': self.calculate_moving_average(calculated_balance, window=12),
                    'export_import_ratio': exports_aligned / imports_aligned,
                    'coverage_ratio': (exports_aligned / imports_aligned * 100)  # Export coverage of imports
                }
                
                # Trade balance volatility
                balance_volatility = self.calculate_volatility(calculated_balance, window=12)
                trade_balance_analysis['balance_volatility'] = balance_volatility
                
                analysis['trade_balance_analysis'] = trade_balance_analysis
        
        # Use official trade balance if available
        if 'trade_balance' in data:
            official_balance = data['trade_balance']
            analysis['official_trade_balance'] = {
                'series': official_balance,
                'current_balance': self.get_latest_value(official_balance),
                'average_balance': official_balance.mean(),
                'balance_growth': self.calculate_growth_rate(official_balance, periods=12),
                'trend': self.calculate_moving_average(official_balance, window=12)
            }
        
        # Export and import composition analysis
        export_import_analysis = {}
        
        if 'exports' in data and 'imports' in data:
            exports = data['exports'].dropna()
            imports = data['imports'].dropna()
            
            # Align series
            common_dates = exports.index.intersection(imports.index)
            if len(common_dates) > 0:
                exports_aligned = exports.loc[common_dates]
                imports_aligned = imports.loc[common_dates]
                
                export_import_analysis = {
                    'exports_summary': self.get_summary_stats(exports_aligned),
                    'imports_summary': self.get_summary_stats(imports_aligned),
                    'exports_growth_summary': self.get_summary_stats(growth_rates.get('exports_yoy', pd.Series())),
                    'imports_growth_summary': self.get_summary_stats(growth_rates.get('imports_yoy', pd.Series())),
                    'correlation': exports_aligned.corr(imports_aligned),
                    'exports_volatility': exports_aligned.std(),
                    'imports_volatility': imports_aligned.std()
                }
        
        analysis['export_import_analysis'] = export_import_analysis
        
        # Price analysis
        price_analysis = {}
        if 'export_price_index' in data and 'import_price_index' in data:
            export_prices = data['export_price_index'].dropna()
            import_prices = data['import_price_index'].dropna()
            
            # Align series
            common_dates = export_prices.index.intersection(import_prices.index)
            if len(common_dates) > 0:
                export_prices_aligned = export_prices.loc[common_dates]
                import_prices_aligned = import_prices.loc[common_dates]
                
                # Terms of trade (export prices / import prices)
                terms_of_trade = export_prices_aligned / import_prices_aligned
                terms_of_trade_growth = self.calculate_growth_rate(terms_of_trade, periods=12)
                
                price_analysis = {
                    'terms_of_trade': terms_of_trade,
                    'terms_of_trade_growth': terms_of_trade_growth,
                    'current_terms_of_trade': self.get_latest_value(terms_of_trade),
                    'current_terms_growth': self.get_latest_value(terms_of_trade_growth),
                    'export_price_growth': growth_rates.get('export_price_index_yoy'),
                    'import_price_growth': growth_rates.get('import_price_index_yoy'),
                    'price_correlation': export_prices_aligned.corr(import_prices_aligned)
                }
        
        analysis['price_analysis'] = price_analysis
        
        # Trade competitiveness indicators
        competitiveness_analysis = {}
        
        # Export growth vs import growth comparison
        if 'exports_yoy' in growth_rates and 'imports_yoy' in growth_rates:
            export_growth = growth_rates['exports_yoy'].dropna()
            import_growth = growth_rates['imports_yoy'].dropna()
            
            common_dates = export_growth.index.intersection(import_growth.index)
            if len(common_dates) > 0:
                export_growth_aligned = export_growth.loc[common_dates]
                import_growth_aligned = import_growth.loc[common_dates]
                
                growth_differential = export_growth_aligned - import_growth_aligned
                
                competitiveness_analysis = {
                    'export_import_growth_diff': growth_differential,
                    'current_growth_diff': self.get_latest_value(growth_differential),
                    'average_growth_diff': growth_differential.mean(),
                    'competitiveness_trend': self.calculate_moving_average(growth_differential, window=12),
                    'export_advantage_periods': (growth_differential > 0).sum(),
                    'import_advantage_periods': (growth_differential < 0).sum()
                }
        
        analysis['competitiveness_analysis'] = competitiveness_analysis
        
        # Seasonal analysis
        seasonal_analysis = {}
        for name, series in data.items():
            if len(series) > 24:  # At least 2 years of data
                seasonal_pattern = self._analyze_seasonality(series)
                seasonal_analysis[name] = seasonal_pattern
        
        analysis['seasonal_analysis'] = seasonal_analysis
        
        # Trade intensity analysis (relative to GDP if available)
        # This would require GDP data, but we can analyze relative changes
        trade_intensity = {}
        if 'exports' in data and 'imports' in data:
            exports = data['exports'].dropna()
            imports = data['imports'].dropna()
            
            common_dates = exports.index.intersection(imports.index)
            if len(common_dates) > 0:
                exports_aligned = exports.loc[common_dates]
                imports_aligned = imports.loc[common_dates]
                
                # Total trade volume
                total_trade = exports_aligned + imports_aligned
                
                trade_intensity = {
                    'total_trade_volume': total_trade,
                    'total_trade_growth': self.calculate_growth_rate(total_trade, periods=12),
                    'exports_share_of_trade': exports_aligned / total_trade * 100,
                    'imports_share_of_trade': imports_aligned / total_trade * 100,
                    'trade_growth_volatility': self.calculate_volatility(self.calculate_growth_rate(total_trade, periods=12), window=12)
                }
        
        analysis['trade_intensity'] = trade_intensity
        
        return analysis
    
    def _analyze_seasonality(self, series: pd.Series) -> Dict:
        """
        Analyze seasonal patterns in trade data
        
        Args:
            series (pd.Series): Time series data
            
        Returns:
            Dict: Seasonal analysis results
        """
        try:
            # Group by month to find seasonal patterns
            monthly_data = series.groupby(series.index.month)
            
            seasonal_stats = {
                'monthly_averages': monthly_data.mean().to_dict(),
                'monthly_std': monthly_data.std().to_dict(),
                'peak_month': monthly_data.mean().idxmax(),
                'trough_month': monthly_data.mean().idxmin(),
                'seasonal_range': monthly_data.mean().max() - monthly_data.mean().min(),
                'coefficient_variation': (monthly_data.mean().std() / monthly_data.mean().mean()) * 100
            }
            
            return seasonal_stats
            
        except Exception as e:
            self.logger.warning(f"Could not analyze seasonality: {str(e)}")
            return {}
    
    def generate_insights(self, analysis_results: Dict) -> Dict:
        """
        Generate insights from trade analysis
        
        Args:
            analysis_results (Dict): Results from trade analysis
            
        Returns:
            Dict: Generated insights
        """
        self.logger.info("Generating trade insights...")
        
        insights = {
            'summary': {},
            'alerts': [],
            'observations': [],
            'trade_assessment': {}
        }
        
        current_values = analysis_results.get('current_values', {})
        trade_balance_analysis = analysis_results.get('trade_balance_analysis', {})
        official_trade_balance = analysis_results.get('official_trade_balance', {})
        price_analysis = analysis_results.get('price_analysis', {})
        competitiveness_analysis = analysis_results.get('competitiveness_analysis', {})
        
        # Current trade levels
        if 'exports' in current_values:
            exports_level = current_values['exports']
            if not np.isnan(exports_level):
                insights['summary']['current_exports'] = f"${exports_level:.1f}B"
        
        if 'imports' in current_values:
            imports_level = current_values['imports']
            if not np.isnan(imports_level):
                insights['summary']['current_imports'] = f"${imports_level:.1f}B"
        
        # Trade balance assessment
        current_balance = None
        if official_trade_balance and 'current_balance' in official_trade_balance:
            current_balance = official_trade_balance['current_balance']
        elif trade_balance_analysis and 'current_balance' in trade_balance_analysis:
            current_balance = trade_balance_analysis['current_balance']
        
        if current_balance is not None and not np.isnan(current_balance):
            insights['summary']['current_trade_balance'] = f"${current_balance:.1f}B"
            
            if current_balance < 0:
                insights['trade_assessment']['balance_status'] = 'Trade Deficit'
                if abs(current_balance) > 50:  # Large deficit
                    insights['alerts'].append(f"Large trade deficit: ${abs(current_balance):.1f}B")
            else:
                insights['trade_assessment']['balance_status'] = 'Trade Surplus'
                insights['observations'].append(f"Trade surplus of ${current_balance:.1f}B")
        
        # Export and import growth assessment
        if 'exports_yoy' in current_values:
            export_growth = current_values['exports_yoy']
            if not np.isnan(export_growth):
                insights['summary']['export_growth'] = f"{export_growth:.1f}%"
                
                if export_growth < -5:
                    insights['alerts'].append(f"Sharp export decline: {export_growth:.1f}% year-over-year")
                elif export_growth > 10:
                    insights['observations'].append(f"Strong export growth: {export_growth:.1f}% year-over-year")
        
        if 'imports_yoy' in current_values:
            import_growth = current_values['imports_yoy']
            if not np.isnan(import_growth):
                insights['summary']['import_growth'] = f"{import_growth:.1f}%"
                
                if import_growth < -5:
                    insights['observations'].append(f"Import decline: {import_growth:.1f}% year-over-year")
                elif import_growth > 15:
                    insights['alerts'].append(f"Rapid import growth: {import_growth:.1f}% year-over-year")
        
        # Terms of trade analysis
        if price_analysis:
            current_terms = price_analysis.get('current_terms_of_trade', np.nan)
            terms_growth = price_analysis.get('current_terms_growth', np.nan)
            
            if not np.isnan(terms_growth):
                insights['summary']['terms_of_trade_growth'] = f"{terms_growth:.1f}%"
                
                if terms_growth > 5:
                    insights['observations'].append(f"Improving terms of trade: {terms_growth:.1f}% growth (export prices rising faster than import prices)")
                elif terms_growth < -5:
                    insights['alerts'].append(f"Deteriorating terms of trade: {terms_growth:.1f}% decline (import prices rising faster than export prices)")
        
        # Competitiveness assessment
        if competitiveness_analysis:
            growth_diff = competitiveness_analysis.get('current_growth_diff', np.nan)
            avg_growth_diff = competitiveness_analysis.get('average_growth_diff', np.nan)
            
            if not np.isnan(growth_diff):
                if growth_diff > 5:
                    insights['observations'].append(f"Export competitiveness improving: exports growing {growth_diff:.1f} pp faster than imports")
                elif growth_diff < -5:
                    insights['observations'].append(f"Export competitiveness declining: exports growing {abs(growth_diff):.1f} pp slower than imports")
            
            # Historical competitiveness
            if not np.isnan(avg_growth_diff):
                if avg_growth_diff > 2:
                    insights['trade_assessment']['historical_competitiveness'] = 'Generally Competitive'
                elif avg_growth_diff < -2:
                    insights['trade_assessment']['historical_competitiveness'] = 'Generally Less Competitive'
                else:
                    insights['trade_assessment']['historical_competitiveness'] = 'Balanced'
        
        # Trade coverage analysis
        if trade_balance_analysis and 'export_import_ratio' in trade_balance_analysis:
            coverage_ratio = trade_balance_analysis['export_import_ratio']
            current_coverage = self.get_latest_value(coverage_ratio)
            
            if not np.isnan(current_coverage):
                coverage_pct = current_coverage * 100
                insights['summary']['export_coverage'] = f"{coverage_pct:.1f}%"
                
                if coverage_pct < 80:
                    insights['alerts'].append(f"Low export coverage: exports cover only {coverage_pct:.1f}% of imports")
                elif coverage_pct > 120:
                    insights['observations'].append(f"High export coverage: exports exceed imports by {coverage_pct-100:.1f}%")
        
        # Price pressure insights
        if 'import_price_index_yoy' in current_values:
            import_price_growth = current_values['import_price_index_yoy']
            if not np.isnan(import_price_growth):
                if import_price_growth > 10:
                    insights['alerts'].append(f"High import price inflation: {import_price_growth:.1f}% year-over-year")
                elif import_price_growth < -5:
                    insights['observations'].append(f"Import price deflation: {import_price_growth:.1f}% year-over-year")
        
        # Trade volatility assessment
        export_import_analysis = analysis_results.get('export_import_analysis', {})
        if export_import_analysis:
            exports_summary = export_import_analysis.get('exports_summary', {})
            imports_summary = export_import_analysis.get('imports_summary', {})
            
            exports_vol = exports_summary.get('std', np.nan)
            imports_vol = imports_summary.get('std', np.nan)
            
            if not np.isnan(exports_vol) and not np.isnan(imports_vol):
                if exports_vol > imports_vol * 1.5:
                    insights['observations'].append("Export volumes significantly more volatile than imports")
                elif imports_vol > exports_vol * 1.5:
                    insights['observations'].append("Import volumes significantly more volatile than exports")
        
        # Seasonal insights
        seasonal_analysis = analysis_results.get('seasonal_analysis', {})
        if seasonal_analysis:
            for series_name, seasonal_data in seasonal_analysis.items():
                if 'coefficient_variation' in seasonal_data:
                    cv = seasonal_data['coefficient_variation']
                    if cv > 10:  # High seasonality
                        peak_month = seasonal_data.get('peak_month', 'Unknown')
                        trough_month = seasonal_data.get('trough_month', 'Unknown')
                        insights['observations'].append(f"{series_name.title()} shows high seasonality (peak: month {peak_month}, trough: month {trough_month})")
        
        return insights
    
    def create_visualizations(self, data: Dict[str, pd.Series], analysis_results: Dict):
        """
        Create trade visualizations
        
        Args:
            data (Dict[str, pd.Series]): Dictionary of trade data series
            analysis_results (Dict): Analysis results
        """
        self.logger.info("Creating trade visualizations...")
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        growth_rates = analysis_results.get('growth_rates', {})
        
        # 1. Trade Overview Dashboard
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Trade Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # Exports and Imports Levels
        ax1 = axes[0, 0]
        if 'exports' in data and 'imports' in data:
            exports = data['exports'].dropna()
            imports = data['imports'].dropna()
            
            if not exports.empty:
                ax1.plot(exports.index, exports.values, label='Exports', linewidth=2, color='green')
            if not imports.empty:
                ax1.plot(imports.index, imports.values, label='Imports', linewidth=2, color='red')
        
        ax1.set_title('Exports and Imports Levels', fontweight='bold')
        ax1.set_ylabel('Billions of Dollars')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Trade Balance
        ax2 = axes[0, 1]
        trade_balance_data = None
        
        # Use official trade balance if available, otherwise calculate it
        if 'trade_balance' in data:
            trade_balance_data = data['trade_balance'].dropna()
        elif analysis_results.get('trade_balance_analysis', {}).get('calculated_balance') is not None:
            trade_balance_data = analysis_results['trade_balance_analysis']['calculated_balance'].dropna()
        
        if trade_balance_data is not None and not trade_balance_data.empty:
            # Color positive and negative differently
            positive_mask = trade_balance_data >= 0
            negative_mask = trade_balance_data < 0
            
            if positive_mask.any():
                ax2.bar(trade_balance_data[positive_mask].index, 
                       trade_balance_data[positive_mask].values,
                       color='green', alpha=0.7, label='Surplus', width=20)
            
            if negative_mask.any():
                ax2.bar(trade_balance_data[negative_mask].index, 
                       trade_balance_data[negative_mask].values,
                       color='red', alpha=0.7, label='Deficit', width=20)
            
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8)
        
        ax2.set_title('Trade Balance', fontweight='bold')
        ax2.set_ylabel('Billions of Dollars')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Trade Growth Rates
        ax3 = axes[1, 0]
        growth_measures = ['exports_yoy', 'imports_yoy']
        colors = ['green', 'red']
        
        for i, measure in enumerate(growth_measures):
            if measure in growth_rates:
                series = growth_rates[measure].dropna()
                if not series.empty:
                    label = measure.replace('_yoy', '').title() + ' YoY'
                    ax3.plot(series.index, series.values, label=label, linewidth=2, color=colors[i])
        
        ax3.axhline(y=0, color='black', linestyle='--', alpha=0.7)
        ax3.set_title('Trade Growth Rates', fontweight='bold')
        ax3.set_ylabel('Growth Rate (%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Terms of Trade
        ax4 = axes[1, 1]
        price_analysis = analysis_results.get('price_analysis', {})
        if 'terms_of_trade' in price_analysis:
            terms_of_trade = price_analysis['terms_of_trade'].dropna()
            if not terms_of_trade.empty:
                ax4.plot(terms_of_trade.index, terms_of_trade.values, 
                        linewidth=2, color='purple')
                
                # Add trend line
                terms_ma = self.calculate_moving_average(terms_of_trade, window=12)
                ax4.plot(terms_ma.index, terms_ma.values, 
                        linestyle='--', color='orange', label='12M Moving Average')
        
        ax4.set_title('Terms of Trade (Export/Import Prices)', fontweight='bold')
        ax4.set_ylabel('Index Ratio')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self.save_chart(fig, 'trade_dashboard.png')
        plt.close()
        
        # 2. Trade Competitiveness Analysis
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Export vs Import Growth Comparison
        if 'exports_yoy' in growth_rates and 'imports_yoy' in growth_rates:
            export_growth = growth_rates['exports_yoy'].dropna()
            import_growth = growth_rates['imports_yoy'].dropna()
            
            if not export_growth.empty and not import_growth.empty:
                ax1.plot(export_growth.index, export_growth.values, 
                        label='Export Growth', linewidth=2, color='green')
                ax1.plot(import_growth.index, import_growth.values, 
                        label='Import Growth', linewidth=2, color='red')
                
                ax1.axhline(y=0, color='black', linestyle='--', alpha=0.7)
                ax1.set_title('Export vs Import Growth Comparison', fontsize=14, fontweight='bold')
                ax1.set_ylabel('Growth Rate (%)')
                ax1.legend()
                ax1.grid(True, alpha=0.3)
        
        # Trade Competitiveness Differential
        competitiveness_analysis = analysis_results.get('competitiveness_analysis', {})
        if 'export_import_growth_diff' in competitiveness_analysis:
            growth_diff = competitiveness_analysis['export_import_growth_diff'].dropna()
            if not growth_diff.empty:
                # Color by positive/negative
                positive_mask = growth_diff >= 0
                negative_mask = growth_diff < 0
                
                if positive_mask.any():
                    ax2.bar(growth_diff[positive_mask].index, 
                           growth_diff[positive_mask].values,
                           color='green', alpha=0.7, label='Export Advantage', width=20)
                
                if negative_mask.any():
                    ax2.bar(growth_diff[negative_mask].index, 
                           growth_diff[negative_mask].values,
                           color='red', alpha=0.7, label='Import Advantage', width=20)
                
                ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8)
                
                # Add trend line
                if 'competitiveness_trend' in competitiveness_analysis:
                    trend = competitiveness_analysis['competitiveness_trend'].dropna()
                    ax2.plot(trend.index, trend.values, 
                            color='blue', linestyle='--', linewidth=2, label='Trend')
        
        ax2.set_title('Trade Competitiveness (Export Growth - Import Growth)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Growth Rate Difference (pp)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self.save_chart(fig, 'trade_competitiveness.png')
        plt.close()
        
        # 3. Price Analysis
        if price_analysis and 'export_price_index_yoy' in growth_rates and 'import_price_index_yoy' in growth_rates:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Export and Import Price Growth
            export_price_growth = growth_rates['export_price_index_yoy'].dropna()
            import_price_growth = growth_rates['import_price_index_yoy'].dropna()
            
            if not export_price_growth.empty:
                ax1.plot(export_price_growth.index, export_price_growth.values,
                        label='Export Price Growth', linewidth=2, color='green')
            
            if not import_price_growth.empty:
                ax1.plot(import_price_growth.index, import_price_growth.values,
                        label='Import Price Growth', linewidth=2, color='red')
            
            ax1.axhline(y=0, color='black', linestyle='--', alpha=0.7)
            ax1.set_title('Export and Import Price Growth', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Price Growth (%)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Terms of Trade Growth
            if 'terms_of_trade_growth' in price_analysis:
                terms_growth = price_analysis['terms_of_trade_growth'].dropna()
                if not terms_growth.empty:
                    # Color by positive/negative
                    positive_mask = terms_growth >= 0
                    negative_mask = terms_growth < 0
                    
                    if positive_mask.any():
                        ax2.bar(terms_growth[positive_mask].index, 
                               terms_growth[positive_mask].values,
                               color='green', alpha=0.7, label='Improving', width=20)
                    
                    if negative_mask.any():
                        ax2.bar(terms_growth[negative_mask].index, 
                               terms_growth[negative_mask].values,
                               color='red', alpha=0.7, label='Deteriorating', width=20)
                    
                    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8)
            
            ax2.set_title('Terms of Trade Growth', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Growth Rate (%)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            self.save_chart(fig, 'trade_price_analysis.png')
            plt.close()
        
        # 4. Trade Volume and Seasonal Analysis
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Export Coverage Ratio
        ax1 = axes[0, 0]
        trade_balance_analysis = analysis_results.get('trade_balance_analysis', {})
        if 'coverage_ratio' in trade_balance_analysis:
            coverage = trade_balance_analysis['coverage_ratio'].dropna()
            if not coverage.empty:
                ax1.plot(coverage.index, coverage.values, linewidth=2, color='blue')
                ax1.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='100% Coverage')
                ax1.fill_between(coverage.index, coverage.values, 100, 
                               where=(coverage.values >= 100), alpha=0.3, color='green', label='Surplus')
                ax1.fill_between(coverage.index, coverage.values, 100, 
                               where=(coverage.values < 100), alpha=0.3, color='red', label='Deficit')
        
        ax1.set_title('Export Coverage of Imports', fontweight='bold')
        ax1.set_ylabel('Coverage Ratio (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Trade Intensity
        ax2 = axes[0, 1]
        trade_intensity = analysis_results.get('trade_intensity', {})
        if 'total_trade_volume' in trade_intensity:
            total_trade = trade_intensity['total_trade_volume'].dropna()
            if not total_trade.empty:
                ax2.plot(total_trade.index, total_trade.values, linewidth=2, color='purple')
                ax2.fill_between(total_trade.index, total_trade.values, alpha=0.3, color='purple')
        
        ax2.set_title('Total Trade Volume (Exports + Imports)', fontweight='bold')
        ax2.set_ylabel('Billions of Dollars')
        ax2.grid(True, alpha=0.3)
        
        # Seasonal Pattern - Exports
        ax3 = axes[1, 0]
        seasonal_analysis = analysis_results.get('seasonal_analysis', {})
        if 'exports' in seasonal_analysis:
            monthly_avg = seasonal_analysis['exports'].get('monthly_averages', {})
            if monthly_avg:
                months = list(monthly_avg.keys())
                values = list(monthly_avg.values())
                
                bars = ax3.bar(months, values, color='lightgreen', alpha=0.7)
                
                # Highlight peak and trough
                peak_month = seasonal_analysis['exports'].get('peak_month')
                trough_month = seasonal_analysis['exports'].get('trough_month')
                
                for i, bar in enumerate(bars):
                    if months[i] == peak_month:
                        bar.set_color('green')
                    elif months[i] == trough_month:
                        bar.set_color('red')
        
        ax3.set_title('Export Seasonality by Month', fontweight='bold')
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Average Exports (Billions)')
        ax3.grid(True, alpha=0.3)
        
        # Seasonal Pattern - Imports
        ax4 = axes[1, 1]
        if 'imports' in seasonal_analysis:
            monthly_avg = seasonal_analysis['imports'].get('monthly_averages', {})
            if monthly_avg:
                months = list(monthly_avg.keys())
                values = list(monthly_avg.values())
                
                bars = ax4.bar(months, values, color='lightcoral', alpha=0.7)
                
                # Highlight peak and trough
                peak_month = seasonal_analysis['imports'].get('peak_month')
                trough_month = seasonal_analysis['imports'].get('trough_month')
                
                for i, bar in enumerate(bars):
                    if months[i] == peak_month:
                        bar.set_color('red')
                    elif months[i] == trough_month:
                        bar.set_color('green')
        
        ax4.set_title('Import Seasonality by Month', fontweight='bold')
        ax4.set_xlabel('Month')
        ax4.set_ylabel('Average Imports (Billions)')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self.save_chart(fig, 'trade_volume_seasonal.png')
        plt.close()
        
        # 5. Trade Statistics Summary
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Current Growth Rates Comparison
        current_values = analysis_results.get('current_values', {})
        growth_measures = ['exports_yoy', 'imports_yoy', 'export_price_index_yoy', 'import_price_index_yoy']
        
        values = []
        labels = []
        colors = ['green', 'red', 'lightgreen', 'lightcoral']
        
        for i, measure in enumerate(growth_measures):
            if measure in current_values and not np.isnan(current_values[measure]):
                values.append(current_values[measure])
                labels.append(measure.replace('_yoy', '').replace('_', ' ').title())
        
        if values:
            bars = ax1.bar(labels, values, color=colors[:len(values)])
            ax1.axhline(y=0, color='black', linestyle='--', alpha=0.7)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                ax1.text(bar.get_x() + bar.get_width()/2, 
                        bar.get_height() + (0.5 if bar.get_height() >= 0 else -1.5),
                        f'{value:.1f}%', ha='center', 
                        va='bottom' if bar.get_height() >= 0 else 'top', 
                        fontweight='bold')
        
        ax1.set_title('Current Growth Rates', fontweight='bold')
        ax1.set_ylabel('Growth Rate (%)')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # Trade Balance Distribution
        if trade_balance_data is not None and not trade_balance_data.empty:
            ax2.hist(trade_balance_data.values, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax2.axvline(x=trade_balance_data.mean(), color='red', linestyle='--', 
                       label=f'Mean: ${trade_balance_data.mean():.1f}B', linewidth=2)
            ax2.axvline(x=0, color='black', linestyle='--', 
                       label='Balanced Trade', linewidth=2)
            
            ax2.set_title('Trade Balance Distribution', fontweight='bold')
            ax2.set_xlabel('Trade Balance (Billions $)')
            ax2.set_ylabel('Frequency')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self.save_chart(fig, 'trade_statistics.png')
        plt.close()
        
        # Save processed data
        if data or growth_rates:
            # Combine original data and calculated metrics
            all_data = {**data, **growth_rates}
            
            # Add calculated trade balance if available
            if trade_balance_analysis and 'calculated_balance' in trade_balance_analysis:
                all_data['calculated_trade_balance'] = trade_balance_analysis['calculated_balance']
            
            # Add terms of trade if available
            if price_analysis and 'terms_of_trade' in price_analysis:
                all_data['terms_of_trade'] = price_analysis['terms_of_trade']
            
            df = pd.DataFrame(all_data)
            self.save_data(df, 'trade_data.csv')
        
        self.logger.info("Trade visualizations completed")