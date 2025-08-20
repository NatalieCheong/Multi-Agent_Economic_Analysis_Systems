"""
Multi-Agent Economy Analysis System
Main application file for coordinating economic analysis agents
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd

# Import configuration and agents
from config import FRED_API_KEY, DEFAULT_START_DATE, DEFAULT_END_DATE, OUTPUT_DIR, LOG_LEVEL
from inflation_agent import InflationAgent
from gdp_agent import GDPAgent
from trade_agent import TradeAgent

class EconomicAnalysisOrchestrator:
    """
    Main orchestrator for coordinating multiple economic analysis agents
    """
    
    def __init__(self, fred_api_key: str):
        """
        Initialize the orchestrator
        
        Args:
            fred_api_key (str): FRED API key
        """
        self.fred_api_key = fred_api_key
        self.agents = {}
        self.analysis_results = {}
        self.combined_insights = {}
        
        # Setup logging
        self.logger = self._setup_logger()
        
        # Initialize agents
        self._initialize_agents()
        
        # Create output directories
        self._create_output_directories()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup main logger"""
        logger = logging.getLogger("EconomicOrchestrator")
        logger.setLevel(getattr(logging, LOG_LEVEL))
        
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # File handler
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            file_handler = logging.FileHandler(
                os.path.join(OUTPUT_DIR, 'economic_analysis.log')
            )
            file_handler.setFormatter(console_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def _initialize_agents(self):
        """Initialize all economic analysis agents"""
        try:
            self.agents = {
                'inflation': InflationAgent(self.fred_api_key),
                'gdp': GDPAgent(self.fred_api_key),
                'trade': TradeAgent(self.fred_api_key)
            }
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing agents: {str(e)}")
            raise
    
    def _create_output_directories(self):
        """Create necessary output directories"""
        directories = [
            OUTPUT_DIR,
            os.path.join(OUTPUT_DIR, 'charts'),
            os.path.join(OUTPUT_DIR, 'data'),
            os.path.join(OUTPUT_DIR, 'reports')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
        self.logger.info("Output directories created")
    
    def run_individual_analysis(self, agent_name: str, start_date: str = None, end_date: str = None) -> Dict:
        """
        Run analysis for a single agent
        
        Args:
            agent_name (str): Name of the agent ('inflation', 'gdp', 'trade')
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            Dict: Analysis results from the agent
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found. Available agents: {list(self.agents.keys())}")
        
        start_date = start_date or DEFAULT_START_DATE
        end_date = end_date or DEFAULT_END_DATE
        
        self.logger.info(f"Running {agent_name} analysis from {start_date} to {end_date}")
        
        try:
            agent = self.agents[agent_name]
            results = agent.run_analysis(start_date, end_date)
            
            self.analysis_results[agent_name] = results
            
            # Save individual results
            self._save_agent_results(agent_name, results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error running {agent_name} analysis: {str(e)}")
            raise
    
    def run_comprehensive_analysis(self, start_date: str = None, end_date: str = None) -> Dict:
        """
        Run comprehensive analysis using all agents
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            Dict: Combined analysis results from all agents
        """
        start_date = start_date or DEFAULT_START_DATE
        end_date = end_date or DEFAULT_END_DATE
        
        self.logger.info(f"Running comprehensive economic analysis from {start_date} to {end_date}")
        
        # Run all agents
        for agent_name in self.agents.keys():
            try:
                self.run_individual_analysis(agent_name, start_date, end_date)
            except Exception as e:
                self.logger.error(f"Failed to run {agent_name} analysis: {str(e)}")
                # Continue with other agents even if one fails
        
        # Generate cross-agent insights
        self.combined_insights = self._generate_combined_insights()
        
        # Create comprehensive report
        comprehensive_report = {
            'analysis_metadata': {
                'start_date': start_date,
                'end_date': end_date,
                'analysis_timestamp': datetime.now().isoformat(),
                'agents_used': list(self.analysis_results.keys())
            },
            'individual_results': self.analysis_results,
            'combined_insights': self.combined_insights,
            'summary': self._generate_executive_summary()
        }
        
        # Save comprehensive report
        self._save_comprehensive_report(comprehensive_report)
        
        return comprehensive_report
    
    def _generate_combined_insights(self) -> Dict:
        """
        Generate insights that combine findings from multiple agents
        
        Returns:
            Dict: Combined insights across all agents
        """
        self.logger.info("Generating combined cross-agent insights...")
        
        combined_insights = {
            'economic_overview': {},
            'cross_correlations': {},
            'policy_implications': [],
            'risk_assessment': {},
            'forecasting_signals': []
        }
        
        # Economic overview combining all agents
        if self.analysis_results:
            combined_insights['economic_overview'] = self._create_economic_overview()
            combined_insights['cross_correlations'] = self._analyze_cross_correlations()
            combined_insights['risk_assessment'] = self._assess_overall_economic_risk()
            combined_insights['policy_implications'] = self._identify_policy_implications()
            combined_insights['forecasting_signals'] = self._identify_forecasting_signals()
        
        return combined_insights
    
    def _create_economic_overview(self) -> Dict:
        """Create an overall economic overview"""
        overview = {
            'current_state': 'Unknown',
            'growth_momentum': 'Unknown',
            'inflation_pressure': 'Unknown',
            'external_balance': 'Unknown',
            'overall_assessment': 'Unknown'
        }
        
        # GDP assessment
        if 'gdp' in self.analysis_results:
            gdp_insights = self.analysis_results['gdp'].get('insights', {})
            economic_assessment = gdp_insights.get('economic_assessment', {})
            
            overview['current_state'] = economic_assessment.get('growth_status', 'Unknown')
            overview['growth_momentum'] = economic_assessment.get('business_cycle_phase', 'Unknown')
        
        # Inflation assessment
        if 'inflation' in self.analysis_results:
            inflation_current = self.analysis_results['inflation'].get('insights', {}).get('summary', {})
            current_inflation = inflation_current.get('current_headline_inflation', 'Unknown')
            overview['inflation_pressure'] = current_inflation
        
        # Trade assessment
        if 'trade' in self.analysis_results:
            trade_assessment = self.analysis_results['trade'].get('insights', {}).get('trade_assessment', {})
            overview['external_balance'] = trade_assessment.get('balance_status', 'Unknown')
        
        # Overall assessment logic
        growth_status = overview['current_state']
        if 'Contraction' in str(growth_status):
            overview['overall_assessment'] = 'Economic Weakness'
        elif 'Strong Growth' in str(growth_status):
            overview['overall_assessment'] = 'Economic Strength'
        elif 'Moderate Growth' in str(growth_status):
            overview['overall_assessment'] = 'Stable Growth'
        else:
            overview['overall_assessment'] = 'Mixed Signals'
        
        return overview
    
    def _analyze_cross_correlations(self) -> Dict:
        """Analyze correlations between different economic indicators"""
        correlations = {
            'inflation_gdp': 'No data',
            'trade_gdp': 'No data',
            'inflation_trade': 'No data',
            'insights': []
        }
        
        # This would require access to the raw data series from each agent
        # For now, we'll provide qualitative insights based on the analysis results
        
        # Check for common themes in insights
        all_insights = []
        for agent_name, results in self.analysis_results.items():
            agent_insights = results.get('insights', {})
            observations = agent_insights.get('observations', [])
            alerts = agent_insights.get('alerts', [])
            all_insights.extend(observations + alerts)
        
        # Look for cross-cutting themes
        common_themes = []
        if any('growth' in insight.lower() for insight in all_insights):
            common_themes.append("Growth concerns appear across multiple indicators")
        
        if any('inflation' in insight.lower() or 'price' in insight.lower() for insight in all_insights):
            common_themes.append("Price pressures evident in multiple sectors")
        
        if any('volatility' in insight.lower() for insight in all_insights):
            common_themes.append("High volatility observed across economic indicators")
        
        correlations['insights'] = common_themes
        
        return correlations
    
    def _assess_overall_economic_risk(self) -> Dict:
        """Assess overall economic risk based on all agents"""
        risk_assessment = {
            'overall_risk_level': 'Medium',
            'risk_factors': [],
            'risk_mitigation_factors': [],
            'key_risks': []
        }
        
        risk_factors = []
        mitigation_factors = []
        
        # Collect alerts (risk factors) and positive observations (mitigation factors)
        for agent_name, results in self.analysis_results.items():
            insights = results.get('insights', {})
            alerts = insights.get('alerts', [])
            observations = insights.get('observations', [])
            
            risk_factors.extend([f"{agent_name.title()}: {alert}" for alert in alerts])
            
            # Positive observations as mitigation factors
            positive_obs = [obs for obs in observations if any(word in obs.lower() 
                          for word in ['strong', 'improving', 'growth', 'positive', 'above average'])]
            mitigation_factors.extend([f"{agent_name.title()}: {obs}" for obs in positive_obs])
        
        # Risk level assessment
        risk_score = len(risk_factors) - len(mitigation_factors)
        
        if risk_score >= 3:
            risk_assessment['overall_risk_level'] = 'High'
        elif risk_score >= 1:
            risk_assessment['overall_risk_level'] = 'Medium-High'
        elif risk_score >= -1:
            risk_assessment['overall_risk_level'] = 'Medium'
        elif risk_score >= -3:
            risk_assessment['overall_risk_level'] = 'Medium-Low'
        else:
            risk_assessment['overall_risk_level'] = 'Low'
        
        risk_assessment['risk_factors'] = risk_factors
        risk_assessment['risk_mitigation_factors'] = mitigation_factors
        
        # Identify key risks
        if 'gdp' in self.analysis_results:
            gdp_assessment = self.analysis_results['gdp'].get('insights', {}).get('economic_assessment', {})
            recession_risk = gdp_assessment.get('recession_risk', 'Unknown')
            if recession_risk in ['High', 'Very High']:
                risk_assessment['key_risks'].append(f"Recession risk: {recession_risk}")
        
        return risk_assessment
    
    def _identify_policy_implications(self) -> List[str]:
        """Identify potential policy implications based on analysis"""
        implications = []
        
        # Monetary policy implications
        if 'inflation' in self.analysis_results:
            inflation_insights = self.analysis_results['inflation'].get('insights', {})
            inflation_summary = inflation_insights.get('summary', {})
            
            fed_target_distance = inflation_summary.get('distance_from_fed_target', '')
            if 'above' in fed_target_distance.lower() or '+' in fed_target_distance:
                implications.append("Monetary Policy: Consider tighter policy to combat inflation")
            elif 'below' in fed_target_distance.lower() or '-' in fed_target_distance:
                implications.append("Monetary Policy: Consider accommodative policy to boost inflation")
        
        # Fiscal policy implications
        if 'gdp' in self.analysis_results:
            gdp_insights = self.analysis_results['gdp'].get('insights', {})
            growth_status = gdp_insights.get('economic_assessment', {}).get('growth_status', '')
            
            if 'Contraction' in growth_status:
                implications.append("Fiscal Policy: Consider stimulus measures to support growth")
            elif 'Strong Growth' in growth_status:
                implications.append("Fiscal Policy: Consider measured approach to avoid overheating")
        
        # Trade policy implications
        if 'trade' in self.analysis_results:
            trade_insights = self.analysis_results['trade'].get('insights', {})
            trade_assessment = trade_insights.get('trade_assessment', {})
            
            balance_status = trade_assessment.get('balance_status', '')
            if 'Deficit' in balance_status:
                implications.append("Trade Policy: Monitor trade deficit and competitiveness")
        
        return implications
    
    def _identify_forecasting_signals(self) -> List[str]:
        """Identify key signals for economic forecasting"""
        signals = []
        
        # Business cycle signals
        if 'gdp' in self.analysis_results:
            gdp_insights = self.analysis_results['gdp'].get('insights', {})
            cycle_phase = gdp_insights.get('economic_assessment', {}).get('business_cycle_phase', '')
            
            if cycle_phase:
                signals.append(f"Business Cycle: Currently in {cycle_phase} phase")
        
        # Inflation signals
        if 'inflation' in self.analysis_results:
            inflation_insights = self.analysis_results['inflation'].get('insights', {})
            observations = inflation_insights.get('observations', [])
            
            trend_observations = [obs for obs in observations if 'trend' in obs.lower() or 'increasing' in obs.lower() or 'decreasing' in obs.lower()]
            signals.extend([f"Inflation Signal: {obs}" for obs in trend_observations])
        
        # Trade signals
        if 'trade' in self.analysis_results:
            trade_insights = self.analysis_results['trade'].get('insights', {})
            observations = trade_insights.get('observations', [])
            
            competitiveness_obs = [obs for obs in observations if 'competitiveness' in obs.lower() or 'terms of trade' in obs.lower()]
            signals.extend([f"Trade Signal: {obs}" for obs in competitiveness_obs])
        
        return signals
    
    def _generate_executive_summary(self) -> Dict:
        """Generate an executive summary of the analysis"""
        summary = {
            'key_findings': [],
            'current_economic_state': 'Unknown',
            'major_risks': [],
            'opportunities': [],
            'recommendations': []
        }
        
        # Current economic state from overview
        overview = self.combined_insights.get('economic_overview', {})
        summary['current_economic_state'] = overview.get('overall_assessment', 'Unknown')
        
        # Key findings from each agent
        key_findings = []
        for agent_name, results in self.analysis_results.items():
            insights = results.get('insights', {})
            summary_data = insights.get('summary', {})
            
            agent_findings = []
            for key, value in summary_data.items():
                if value and str(value) != 'Unknown':
                    agent_findings.append(f"{key.replace('_', ' ').title()}: {value}")
            
            if agent_findings:
                key_findings.append(f"{agent_name.title()} - {'; '.join(agent_findings[:3])}")  # Top 3 findings
        
        summary['key_findings'] = key_findings
        
        # Major risks from risk assessment
        risk_assessment = self.combined_insights.get('risk_assessment', {})
        risk_factors = risk_assessment.get('risk_factors', [])
        summary['major_risks'] = risk_factors[:5]  # Top 5 risks
        
        # Opportunities (positive observations)
        opportunities = []
        for agent_name, results in self.analysis_results.items():
            insights = results.get('insights', {})
            observations = insights.get('observations', [])
            
            positive_obs = [obs for obs in observations if any(word in obs.lower() 
                          for word in ['strong', 'improving', 'growth', 'positive', 'above', 'advantage'])]
            opportunities.extend(positive_obs[:2])  # Top 2 per agent
        
        summary['opportunities'] = opportunities
        
        # Recommendations from policy implications
        policy_implications = self.combined_insights.get('policy_implications', [])
        summary['recommendations'] = policy_implications
        
        return summary
    
    def _save_agent_results(self, agent_name: str, results: Dict):
        """Save individual agent results to file"""
        filename = f"{agent_name}_analysis_results.json"
        filepath = os.path.join(OUTPUT_DIR, 'reports', filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            self.logger.info(f"Saved {agent_name} results to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving {agent_name} results: {str(e)}")
    
    def _save_comprehensive_report(self, report: Dict):
        """Save comprehensive analysis report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_economic_analysis_{timestamp}.json"
        filepath = os.path.join(OUTPUT_DIR, 'reports', filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Saved comprehensive report to {filepath}")
            
            # Also save a summary report in readable format
            self._save_readable_summary(report, timestamp)
            
        except Exception as e:
            self.logger.error(f"Error saving comprehensive report: {str(e)}")
    
    def _save_readable_summary(self, report: Dict, timestamp: str):
        """Save a human-readable summary report"""
        filename = f"economic_analysis_summary_{timestamp}.txt"
        filepath = os.path.join(OUTPUT_DIR, 'reports', filename)
        
        try:
            with open(filepath, 'w') as f:
                f.write("ECONOMIC ANALYSIS SUMMARY REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                # Metadata
                metadata = report.get('analysis_metadata', {})
                f.write(f"Analysis Period: {metadata.get('start_date')} to {metadata.get('end_date')}\n")
                f.write(f"Analysis Date: {metadata.get('analysis_timestamp', '')[:10]}\n")
                f.write(f"Agents Used: {', '.join(metadata.get('agents_used', []))}\n\n")
                
                # Executive Summary
                summary = report.get('summary', {})
                f.write("EXECUTIVE SUMMARY\n")
                f.write("-" * 20 + "\n")
                f.write(f"Current Economic State: {summary.get('current_economic_state', 'Unknown')}\n\n")
                
                # Key Findings
                f.write("KEY FINDINGS\n")
                f.write("-" * 15 + "\n")
                for finding in summary.get('key_findings', []):
                    f.write(f"• {finding}\n")
                f.write("\n")
                
                # Major Risks
                f.write("MAJOR RISKS\n")
                f.write("-" * 12 + "\n")
                for risk in summary.get('major_risks', []):
                    f.write(f"• {risk}\n")
                f.write("\n")
                
                # Opportunities
                f.write("OPPORTUNITIES\n")
                f.write("-" * 14 + "\n")
                for opportunity in summary.get('opportunities', []):
                    f.write(f"• {opportunity}\n")
                f.write("\n")
                
                # Recommendations
                f.write("RECOMMENDATIONS\n")
                f.write("-" * 16 + "\n")
                for recommendation in summary.get('recommendations', []):
                    f.write(f"• {recommendation}\n")
                f.write("\n")
                
                # Combined Insights
                combined_insights = report.get('combined_insights', {})
                
                # Economic Overview
                overview = combined_insights.get('economic_overview', {})
                if overview:
                    f.write("ECONOMIC OVERVIEW\n")
                    f.write("-" * 17 + "\n")
                    for key, value in overview.items():
                        f.write(f"{key.replace('_', ' ').title()}: {value}\n")
                    f.write("\n")
                
                # Risk Assessment
                risk_assessment = combined_insights.get('risk_assessment', {})
                if risk_assessment:
                    f.write("RISK ASSESSMENT\n")
                    f.write("-" * 16 + "\n")
                    f.write(f"Overall Risk Level: {risk_assessment.get('overall_risk_level', 'Unknown')}\n\n")
                
                # Individual Agent Summaries
                f.write("DETAILED AGENT ANALYSIS\n")
                f.write("=" * 25 + "\n\n")
                
                individual_results = report.get('individual_results', {})
                for agent_name, results in individual_results.items():
                    f.write(f"{agent_name.upper()} ANALYSIS\n")
                    f.write("-" * (len(agent_name) + 9) + "\n")
                    
                    insights = results.get('insights', {})
                    
                    # Summary
                    agent_summary = insights.get('summary', {})
                    if agent_summary:
                        f.write("Summary:\n")
                        for key, value in agent_summary.items():
                            if value and str(value) != 'Unknown':
                                f.write(f"  {key.replace('_', ' ').title()}: {value}\n")
                        f.write("\n")
                    
                    # Alerts
                    alerts = insights.get('alerts', [])
                    if alerts:
                        f.write("Alerts:\n")
                        for alert in alerts:
                            f.write(f"  ⚠ {alert}\n")
                        f.write("\n")
                    
                    # Observations
                    observations = insights.get('observations', [])
                    if observations:
                        f.write("Key Observations:\n")
                        for obs in observations[:5]:  # Top 5 observations
                            f.write(f"  • {obs}\n")
                        f.write("\n")
                    
                    f.write("\n")
            
            self.logger.info(f"Saved readable summary to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving readable summary: {str(e)}")
    
    def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        status = {}
        for agent_name, agent in self.agents.items():
            status[agent_name] = {
                'initialized': True,
                'last_analysis': agent.analysis_results.get('timestamp', 'Never'),
                'data_cache_size': len(agent.data_cache)
            }
        return status
    
    def clear_cache(self):
        """Clear data cache for all agents"""
        for agent in self.agents.values():
            agent.data_cache.clear()
        self.logger.info("Cleared cache for all agents")


def main():
    """Main function to run the economic analysis system"""
    
    # Check for API key
    if not FRED_API_KEY or FRED_API_KEY == 'YOUR_FRED_API_KEY_HERE':
        print("Error: Please set your FRED API key in config.py or as an environment variable")
        print("You can get a free API key from: https://research.stlouisfed.org/docs/api/api_key.html")
        return
    
    # Initialize orchestrator
    try:
        orchestrator = EconomicAnalysisOrchestrator(FRED_API_KEY)
        print("Economic Analysis System initialized successfully!")
        print(f"Output directory: {OUTPUT_DIR}")
        
    except Exception as e:
        print(f"Error initializing system: {str(e)}")
        return
    
    # Example usage
    print("\nRunning comprehensive economic analysis...")
    
    try:
        # Run comprehensive analysis
        results = orchestrator.run_comprehensive_analysis()
        
        print("\nAnalysis completed successfully!")
        print(f"Results saved to: {OUTPUT_DIR}")
        
        # Print quick summary
        summary = results.get('summary', {})
        print(f"\nQuick Summary:")
        print(f"Economic State: {summary.get('current_economic_state', 'Unknown')}")
        print(f"Key Findings: {len(summary.get('key_findings', []))}")
        print(f"Major Risks: {len(summary.get('major_risks', []))}")
        print(f"Opportunities: {len(summary.get('opportunities', []))}")
        
    except Exception as e:
        print(f"Error running analysis: {str(e)}")
        return
    
    # Optional: Run individual agent analysis
    print("\nFor individual agent analysis, you can run:")
    print("orchestrator.run_individual_analysis('inflation')")
    print("orchestrator.run_individual_analysis('gdp')")
    print("orchestrator.run_individual_analysis('trade')")


if __name__ == "__main__":
    main()

    # Create global orchestrator for interactive use
    if FRED_API_KEY and FRED_API_KEY != 'YOUR_FRED_API_KEY_HERE':
        globals()['orchestrator'] = EconomicAnalysisOrchestrator(FRED_API_KEY)
        print("\nOrchestrator is now available globally!")
        print("You can run: orchestrator.run_individual_analysis('inflation')")