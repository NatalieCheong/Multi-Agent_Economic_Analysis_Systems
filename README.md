# Multi-Agent Economic Analysis System

A sophisticated economic analysis system that uses specialized AI agents to analyze inflation, GDP, and international trade data from the Federal Reserve Economic Data (FRED) API. This system provides comprehensive economic insights through automated data collection, analysis, and visualization.

## 🎯 **System Overview**

This multi-agent system employs five specialized economic analysis agents:
- **🔴 Inflation Agent**: Monitors CPI, PCE, core inflation, and producer prices
- **🟢 GDP Agent**: Analyzes economic growth, business cycles, and productivity
- **🟠 Trade Agent**: Examines international trade flows, competitiveness, and trade balance
- **🔮 Forecast Agent**: Provides 12-month economic predictions using machine learning models
- **📊 Economic Cycle Agent**: Identifies business cycle phases and leading/lagging indicators

## 📊 **Recent Analysis Results**

### **Latest US Economic Assessment (August 2025)**
- **Overall State**: Stable Growth in Expansion Phase
- **Headline Inflation**: 2.73% (near Fed's 2% target)
- **Core Inflation**: 3.05% (+0.58 pp above target)
- **GDP Growth**: 1.99% (below historical 3.15% average)
- **Trade Balance**: -$60.2B deficit (improving competitiveness)
- **Risk Level**: Medium-High

### **New Forecasting & Cycle Analysis Capabilities**
✅ **12-Month Economic Forecasts**: 8 series forecasted using ML models  
✅ **Best Performing Model**: Linear Regression across all economic indicators  
✅ **Business Cycle Detection**: Advanced phase identification with leading indicators  
✅ **Predictive Analytics**: Machine learning models for economic trend prediction  

### **Key Economic Trends Identified**
✅ **Inflation Moderating**: All inflation measures showing decreasing trends  
✅ **Export Competitiveness**: Improving (+5.0 pp vs imports)  
✅ **Forecast Reliability**: High-confidence 12-month predictions available  
⚠️ **Cycle Uncertainty**: Low confidence in current business cycle phase identification  
⚠️ **Trade Deficit**: Large but stable at current levels  

### **COVID-19 Economic Impact Analysis (2020-2022)**
The system successfully captured the economic disruption and recovery:
- Maintained classification as "Stable Growth" despite volatility
- Identified trade balance deterioration during recovery
- Tracked inflation acceleration and subsequent moderation
- Demonstrated economy's resilience through unprecedented crisis

## 🚀 **Features**

### **Core Capabilities**
- **Real-time Data Integration**: Automatic FRED API data retrieval
- **Multi-Agent Architecture**: Specialized agents for different economic domains
- **Comprehensive Analysis**: Growth rates, volatility, trends, and correlations
- **Business Cycle Detection**: Automated expansion/contraction identification
- **Policy-Relevant Insights**: Fed target comparisons and recession risk assessment

### **Advanced Analytics**
- **Historical Context**: Analysis spans back to 1947 for comprehensive perspective
- **Volatility Assessment**: Rolling volatility and coefficient of variation calculations
- **Seasonal Pattern Recognition**: Monthly seasonality detection in trade data
- **Cross-Agent Correlation**: Multi-dimensional economic relationship analysis
- **Custom Date Range Analysis**: Flexible period selection for specific economic events
- **Machine Learning Forecasting**: 12-month predictions using multiple ML models
- **Business Cycle Detection**: Automated identification of economic cycle phases
- **Leading Indicator Analysis**: Early warning signals for economic turning points

### **Automated Outputs**
- **Rich Visualizations**: Dashboard-style charts, time series plots, distribution analysis
- **Executive Reports**: Human-readable summaries with key findings and recommendations
- **Structured Data**: CSV exports for further analysis
- **JSON Reports**: Detailed machine-readable results

## 📁 **Project Structure**

```
Multi-Agent_Economic_Analysis_Systems/
├── 📋 requirements.txt          # Python dependencies
├── ⚙️ config.py                # Configuration and FRED series IDs
├── 🏗️ base_agent.py            # Abstract base class for agents
├── 🔴 inflation_agent.py       # Inflation analysis specialist
├── 🟢 gdp_agent.py             # GDP and growth analysis
├── 🟠 trade_agent.py           # International trade analysis
├── 🔮 forecast_agent.py        # Economic forecasting with ML models
├── 📊 economic_cycle_agent.py  # Business cycle analysis
├── 🎯 main.py                  # Main orchestrator application
├── 📄 README.md               # This documentation
├── 🚫 .gitignore              # Git exclusions
├── 📈 charts/                 # Visualization files (PNG)
├── 📋 data/                   # Processed datasets (CSV)
└── 📊 output/                 # Generated analysis outputs
    └── 📖 reports/            # Analysis reports (JSON/TXT)
```

## 🛠️ **Installation & Setup**

### **Prerequisites**
- Python 3.8+
- FRED API key (free from Federal Reserve)

### **Quick Start**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/NatalieCheong/Multi-Agent_Economic_Analysis_Systems.git
   cd Multi-Agent_Economic_Analysis_Systems
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Get FRED API key:**
   - Visit: https://research.stlouisfed.org/docs/api/api_key.html
   - Create free account and generate API key

5. **Configure API key:**
   
   Create `.env` file:
   ```
   FRED_API_KEY=your_actual_api_key_here
   ```

6. **Run analysis:**
   ```bash
   python main.py
   ```

## 💡 **Usage Examples**

### **Comprehensive Analysis**
```python
python main.py  # Runs all agents with 10-year historical data
```

### **Interactive Analysis**
```python
python3 -i main.py

# After initialization:
>>> orchestrator.run_individual_analysis('inflation')
>>> orchestrator.run_individual_analysis('gdp')
>>> orchestrator.run_individual_analysis('trade')
>>> orchestrator.run_individual_analysis('forecast')
>>> orchestrator.run_individual_analysis('economic_cycle')
```

### **Custom Date Range Analysis**
```python
# Analyze COVID-19 economic impact
>>> covid_results = orchestrator.run_comprehensive_analysis('2020-01-01', '2022-12-31')

# Recent inflation trends
>>> recent_inflation = orchestrator.run_individual_analysis('inflation', '2023-01-01', '2025-08-20')

# Financial crisis comparison
>>> crisis_analysis = orchestrator.run_comprehensive_analysis('2007-01-01', '2009-12-31')

# Get 12-month economic forecasts
>>> forecast_results = orchestrator.run_individual_analysis('forecast', '2020-01-01', '2025-08-20')

# Analyze business cycle patterns
>>> cycle_analysis = orchestrator.run_individual_analysis('economic_cycle', '2015-01-01', '2025-08-20')
```

## 📊 **Agent Specifications**

### **🔴 Inflation Agent**
- **Data Sources**: CPI, Core CPI, PCE, Core PCE, Producer Price Index
- **Analysis Capabilities**:
  - Year-over-year inflation rate calculations
  - Fed target (2%) comparison analysis
  - Core vs headline inflation divergence
  - Volatility and trend assessment
  - 12-month moving averages

### **🟢 GDP Agent** 
- **Data Sources**: Real GDP, Nominal GDP, GDP per capita, GDP growth rate, GDP deflator
- **Analysis Capabilities**:
  - Quarterly and annual growth rate calculations
  - Business cycle phase identification
  - Recession risk assessment (technical definition)
  - Productivity trend analysis
  - Economic strength indicators and percentile rankings

### **🟠 Trade Agent**
- **Data Sources**: Exports, Imports, Trade balance
- **Analysis Capabilities**:
  - Trade competitiveness assessment
  - Export coverage ratio calculations
  - Seasonal pattern recognition
  - Growth differential analysis (export vs import)
  - Trade intensity and volume analysis

### **🔮 Forecast Agent** 
- **Data Sources**: GDP, Inflation, Employment, Interest Rates
- **Analysis Capabilities**:
  - 12-month economic forecasts using ML models
  - Model performance comparison (Linear Regression, Random Forest, Exponential Smoothing)
  - Feature engineering with lag variables and seasonal patterns
  - Automatic best model selection based on accuracy metrics
  - Directional trend predictions with statistical confidence

### **📊 Economic Cycle Agent**
- **Data Sources**: Leading (S&P 500, Yield Curve), Coincident (GDP, Employment), Lagging (Unemployment, Debt) indicators
- **Analysis Capabilities**:
  - Business cycle phase identification (Expansion, Peak, Contraction, Trough)
  - Composite leading, coincident, and lagging indicator construction
  - Cycle turning point detection and timing analysis
  - Cross-indicator correlation and lead/lag relationship analysis
  - Historical cycle statistics and pattern recognition

## 📈 **Sample Outputs**

### **Economic Dashboard Charts**

#### **GDP Analysis Dashboard**
![GDP Dashboard](https://github.com/NatalieCheong/Multi-Agent_Economic_Analysis_Systems/blob/main/charts/GDPAgent_gdp_dashboard.png)

*Comprehensive GDP analysis showing real GDP levels, growth rates, business cycle phases, and productivity trends*

#### **Inflation Analysis - Core vs Headline Comparison**
![Inflation Comparison](https://github.com/NatalieCheong/Multi-Agent_Economic_Analysis_Systems/blob/main/charts/InflationAgent_core_vs_headline_comparison.png)

*Detailed comparison of headline vs core inflation rates with Fed target overlay and divergence analysis*

#### **Trade Competitiveness Analysis**
![Trade Competitiveness](https://github.com/NatalieCheong/Multi-Agent_Economic_Analysis_Systems/blob/main/charts/TradeAgent_trade_competitiveness.png)

*Export vs import growth comparison and trade competitiveness differential analysis showing economic performance trends*

### **Executive Summary Report**
```
ECONOMIC ANALYSIS SUMMARY REPORT
Analysis Period: 2015-08-24 to 2025-08-21
Current Economic State: Stable Growth

KEY FINDINGS:
• Forecast - Total Forecasts: 8; Horizon: 12 months; Best Model: Linear Regression
• Economic Cycle - Current Phase: Expansion (Low Confidence); Avg Cycle: 0.3 years
• Inflation - Current Headline: 2.73%; Core: 3.05%; Fed Distance: +0.58pp
• GDP - Current Growth: 1.99%; Historical Average: 3.15%; Variance: -1.16pp  
• Trade - Exports: $3241.9B; Imports: $4114.3B; Balance: -$60.2B

MAJOR RISKS:
• Business cycle phase identification uncertainty
• Large trade deficit requiring monitoring
• Low export coverage (78.8% of imports)

OPPORTUNITIES:
• Export competitiveness improving (+5.0pp advantage)
• Advanced forecasting capabilities providing 12-month outlook
• Leading indicators available for early economic signals
```

## 🔧 **Configuration**

### **Customizing Economic Indicators**
Modify `config.py` to analyze different FRED series:

```python
FRED_SERIES = {
    'inflation': {
        'cpi_all': 'CPIAUCSL',           # Consumer Price Index
        'core_cpi': 'CPILFESL',         # Core CPI
        'pce': 'PCEPI',                 # PCE Price Index
        # Add custom series here
    }
}
```

### **Analysis Parameters**
- `DEFAULT_START_DATE`: Historical analysis start point
- `DEFAULT_END_DATE`: Analysis end date  
- `CORRELATION_THRESHOLD`: Cross-agent correlation significance
- `VOLATILITY_WINDOW`: Rolling volatility calculation window

## 🎯 **Key Insights Demonstrated**

### **Economic Accuracy**
The system accurately identified real economic conditions:
- ✅ Inflation moderation trend (confirmed by Fed policy)
- ✅ Trade competitiveness improvement 
- ✅ Economic resilience during COVID-19
- ✅ Current expansion phase maintenance

### **Policy Relevance**
Generated actionable insights:
- 💼 **Monetary Policy**: Suggested tighter policy during high inflation
- 🏛️ **Trade Policy**: Recommended deficit monitoring
- 📊 **Risk Assessment**: Accurate recession risk evaluation

## 🔮 **Future Enhancements**

### **Planned Agent Additions**
- **Employment Agent**: Labor market analysis (unemployment, job growth, wage trends)
- **Housing Agent**: Real estate and construction indicators
- **Financial Agent**: Stock market, bond yields, credit conditions
- **Consumer Agent**: Sentiment, spending patterns, confidence indices
- **International Agent**: Global economic comparisons and cross-country analysis

### **Advanced Features**
- **Enhanced ML Models**: Deep learning forecasts with neural networks
- **Real-time Alert System**: Automated economic threshold monitoring
- **Interactive Web Dashboard**: Browser-based visualization and analysis
- **PDF Report Generation**: Professional formatted analytical reports
- **API Integration**: RESTful API for external system integration

## ⚠️ **Important Notes**

### **Data Limitations**
- FRED API rate limits: 120 requests per 60 seconds
- Some historical series have limited availability
- Data revisions may affect historical comparisons

### **API Key Security**
- Never commit API keys to version control
- Use environment variables or `.env` files
- Keep `.env` file in `.gitignore`

## 📚 **Dependencies**

```
fredapi>=0.5.1          # FRED API access
pandas>=1.5.0           # Data manipulation
numpy>=1.24.0           # Numerical computations  
matplotlib>=3.6.0       # Basic plotting
seaborn>=0.12.0         # Statistical visualizations
plotly>=5.15.0          # Interactive charts
python-dotenv>=1.0.0    # Environment variable management
scikit-learn>=1.3.0     # Machine learning models
scipy>=1.11.0           # Signal processing and statistics
```

## 🤝 **Contributing**

Contributions welcome! Areas for improvement:
- Additional economic indicators
- Enhanced visualization techniques
- Machine learning integration
- Performance optimizations
- Documentation improvements

## ⚠️ **Disclaimer**

### **Educational and Research Purpose Only**

This Multi-Agent Economic Analysis System is developed and provided **for educational, research, and demonstration purposes only**. The system is designed to showcase advanced data science techniques, machine learning applications, and economic analysis methodologies.

### **Not Financial Advice**

**IMPORTANT**: This system and its outputs:
- ❌ **Are NOT financial advice** or investment recommendations
- ❌ **Should NOT be used** for making financial, investment, or business decisions
- ❌ **Do not constitute** professional economic, financial, or investment advice
- ❌ **Are not endorsed** by any financial institution, government agency, or professional organization

### **Data and Model Limitations**

Users should be aware that:
- **Data Accuracy**: Economic data may be subject to revisions, delays, or errors
- **Model Limitations**: Machine learning models are based on historical patterns and may not predict future events accurately
- **Forecast Uncertainty**: Economic forecasts are inherently uncertain and subject to significant variability
- **Academic Exercise**: This system represents an academic and educational exploration of economic analysis techniques

### **User Responsibility**

By using this system, you acknowledge that:
- You understand this is an educational tool and demonstration project
- You will not rely on the outputs for financial or investment decisions
- You will seek appropriate professional advice for any financial or economic decisions
- You use this system at your own risk and discretion

### **No Warranty**

This software is provided "as is" without warranty of any kind, express or implied. The authors and contributors make no representations or warranties regarding the accuracy, completeness, or reliability of the economic analysis, forecasts, or any other outputs generated by this system.

### **Data Source Attribution**

This system uses data from the Federal Reserve Economic Data (FRED) API. Users must comply with FRED's terms of use and data licensing requirements. The Federal Reserve Bank of St. Louis is not affiliated with this project and does not endorse this system or its outputs.

### **Academic and Learning Context**

This project demonstrates:
- Multi-agent system architecture
- Economic data analysis techniques
- Machine learning applications in economics
- Time series analysis and forecasting
- Data visualization and reporting methodologies

**For educational exploration and learning purposes only.**

---

**⚖️ Legal Notice**: If you require economic analysis for professional or commercial purposes, please consult qualified economists, financial advisors, or authorized economic research institutions.

## 🙏 **Acknowledgments**

- **Federal Reserve Bank of St. Louis** for providing comprehensive economic data through FRED
- **Python Data Science Community** for excellent analytical libraries
- **Economic Research Community** for methodology and best practices

## 📞 **Support**

For issues or questions:
- Check existing issues on GitHub
- Review FRED API documentation for data-related questions
- Ensure all dependencies are correctly installed
- Verify API key configuration

---

**Built with ❤️ for economic analysis and data-driven insights**
