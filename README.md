# Multi-Agent Economic Analysis System

A sophisticated economic analysis system that uses specialized AI agents to analyze inflation, GDP, and international trade data from the Federal Reserve Economic Data (FRED) API. This system provides comprehensive economic insights through automated data collection, analysis, and visualization.

## 🎯 **System Overview**

This multi-agent system employs three specialized economic analysis agents:
- **🔴 Inflation Agent**: Monitors CPI, PCE, core inflation, and producer prices
- **🟢 GDP Agent**: Analyzes economic growth, business cycles, and productivity
- **🟠 Trade Agent**: Examines international trade flows, competitiveness, and trade balance

## 📊 **Recent Analysis Results**

### **Current US Economic Assessment (as of August 2025)**
- **Overall State**: Stable Growth in Expansion Phase
- **Headline Inflation**: 2.73% (near Fed's 2% target)
- **Core Inflation**: 3.05% (+0.58 pp above target)
- **GDP Growth**: 1.99% (below historical 3.15% average)
- **Trade Balance**: -$60.2B deficit (improving competitiveness)
- **Risk Level**: Medium-High

### **Key Economic Trends Identified**
✅ **Inflation Moderating**: All inflation measures showing decreasing trends  
✅ **Export Competitiveness**: Improving (+5.0 pp vs imports)  
✅ **Low Recession Risk**: Economy maintaining expansion  
⚠️ **Producer Price Pressures**: Rising with 1.52 pp magnitude  
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
├── 🎯 main.py                  # Main orchestrator application
├── 📄 README.md               # This documentation
├── 🚫 .gitignore              # Git exclusions
└── 📊 output/                 # Generated analysis outputs
    ├── 📈 charts/             # Visualization files (PNG)
    ├── 📋 data/               # Processed datasets (CSV)
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
```

### **Custom Date Range Analysis**
```python
# Analyze COVID-19 economic impact
>>> covid_results = orchestrator.run_comprehensive_analysis('2020-01-01', '2022-12-31')

# Recent inflation trends
>>> recent_inflation = orchestrator.run_individual_analysis('inflation', '2023-01-01', '2025-08-20')

# Financial crisis comparison
>>> crisis_analysis = orchestrator.run_comprehensive_analysis('2007-01-01', '2009-12-31')
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

## 📈 **Sample Outputs**

### **Economic Dashboard Charts**
- Multi-panel inflation dashboard with Fed target overlay
- GDP growth timeline with business cycle shading
- Trade balance evolution with competitiveness indicators
- Distribution analysis and statistical summaries

### **Executive Summary Report**
```
ECONOMIC ANALYSIS SUMMARY REPORT
Analysis Period: 2020-01-01 to 2022-12-31
Current Economic State: Stable Growth

KEY FINDINGS:
• Inflation - Current Headline: 2.73%; Core: 3.05%; Fed Distance: +0.58pp
• GDP - Current Growth: 1.99%; Historical Average: 3.15%; Variance: -1.16pp  
• Trade - Exports: $3241.9B; Imports: $4114.3B; Balance: -$60.2B

MAJOR RISKS:
• Large trade deficit requiring monitoring
• Low export coverage (78.8% of imports)

OPPORTUNITIES:
• Export competitiveness improving (+5.0pp advantage)
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
- **Employment Agent**: Labor market analysis (unemployment, job growth)
- **Housing Agent**: Real estate and construction indicators
- **Financial Agent**: Stock market, bond yields, credit conditions
- **Consumer Agent**: Sentiment, spending patterns, confidence indices

### **Advanced Features**
- Machine learning forecast models
- Real-time alert system
- Interactive web dashboard
- PDF report generation
- International economic comparisons

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
```

## 🤝 **Contributing**

Contributions welcome! Areas for improvement:
- Additional economic indicators
- Enhanced visualization techniques
- Machine learning integration
- Performance optimizations
- Documentation improvements

## 📄 **License**

This project is provided for educational and research purposes. Please ensure compliance with FRED's terms of use when accessing their data.

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
