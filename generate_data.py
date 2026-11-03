"""
Data Generator for 'Reasoning Is All You Need'
Generates realistic historical stock CSV datasets and fictional news JSON.
"""

import os
import json
import random
import datetime

# Ensure directories exist
os.makedirs("data/stocks", exist_ok=True)
os.makedirs("data/news", exist_ok=True)

# Configuration for the 5 demonstration stocks
STOCKS_CONFIG = {
    "TCS": {
        "start_price": 3750.0,
        "volatility": 0.012,
        "drift": 0.0004,
        "avg_volume": 140000,
        "currency": "INR"
    },
    "INFY": {
        "start_price": 1520.0,
        "volatility": 0.015,
        "drift": 0.0006,
        "avg_volume": 350000,
        "currency": "INR"
    },
    "RELIANCE": {
        "start_price": 2720.0,
        "volatility": 0.013,
        "drift": 0.0005,
        "avg_volume": 280000,
        "currency": "INR"
    },
    "HDFCBANK": {
        "start_price": 1580.0,
        "volatility": 0.011,
        "drift": 0.0002,
        "avg_volume": 420000,
        "currency": "INR"
    },
    "AAPL": {
        "start_price": 182.0,
        "volatility": 0.014,
        "drift": 0.0007,
        "avg_volume": 850000,
        "currency": "USD"
    }
}

def generate_stock_csv(symbol, config, num_days=130):
    random.seed(42 + hash(symbol) % 1000)
    
    # Generate business days leading up to 2026-08-25
    end_date = datetime.date(2026, 8, 25)
    current_date = end_date
    dates = []
    
    while len(dates) < num_days:
        if current_date.weekday() < 5:  # Monday to Friday
            dates.append(current_date)
        current_date -= datetime.timedelta(days=1)
    
    dates.reverse()  # Chronological order
    
    price = config["start_price"]
    volatility = config["volatility"]
    drift = config["drift"]
    avg_vol = config["avg_volume"]
    
    rows = []
    for d in dates:
        # Generate daily return with random walk
        daily_return = random.gauss(drift, volatility)
        open_price = round(price * (1 + random.gauss(0, 0.003)), 2)
        close_price = round(price * (1 + daily_return), 2)
        
        # High and Low
        high_price = round(max(open_price, close_price) * (1 + abs(random.gauss(0.004, 0.003))), 2)
        low_price = round(min(open_price, close_price) * (1 - abs(random.gauss(0.004, 0.003))), 2)
        
        # Volume
        volume = int(avg_vol * random.uniform(0.7, 1.5))
        
        rows.append({
            "Date": d.strftime("%Y-%m-%d"),
            "Open": open_price,
            "High": high_price,
            "Low": low_price,
            "Close": close_price,
            "Volume": volume
        })
        
        price = close_price
    
    csv_path = os.path.join("data", "stocks", f"{symbol}.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("Date,Open,High,Low,Close,Volume\n")
        for r in rows:
            f.write(f"{r['Date']},{r['Open']},{r['High']},{r['Low']},{r['Close']},{r['Volume']}\n")
            
    print(f"Generated {len(rows)} rows for {symbol} at {csv_path}")

# Generate News Dataset
NEWS_DATA = [
    # TCS
    {
        "date": "2026-08-24",
        "stock": "TCS",
        "title": "TCS Secures Multi-Million Dollar AI Transformation Deal with European Banking Giant",
        "description": "Tata Consultancy Services announced a landmark multi-year contract to modernize core banking platforms using generative AI and cloud infrastructure.",
        "category": "Business"
    },
    {
        "date": "2026-08-20",
        "stock": "TCS",
        "title": "TCS Reports Strong Q1 Operating Margins Surpassing Street Expectations",
        "description": "TCS demonstrated resilient operational efficiency, delivering an operating margin of 26.2% driven by enterprise AI adoption and operational streamlining.",
        "category": "Earnings"
    },
    {
        "date": "2026-08-14",
        "stock": "TCS",
        "title": "TCS Launches Proprietary Enterprise Agentic AI Platform 'CogniSphere'",
        "description": "The new suite enables Fortune 500 enterprises to deploy autonomous AI agents across supply chain and customer lifecycle management.",
        "category": "Technology"
    },
    {
        "date": "2026-08-05",
        "stock": "TCS",
        "title": "TCS Expands Latin American Innovation Hubs with 5,000 New Technical Hires",
        "description": "Strategic expansion in Guadalajara and São Paulo aims to cater to surging nearshore demand from North American financial institutions.",
        "category": "Expansion"
    },
    {
        "date": "2026-07-28",
        "stock": "TCS",
        "title": "TCS Board Approves Interim Dividend of ₹28 Per Share",
        "description": "Shareholders rewarded with healthy dividend payout following robust free cash flow generation in the previous fiscal quarter.",
        "category": "Earnings"
    },
    {
        "date": "2026-07-15",
        "stock": "TCS",
        "title": "Leadership Transition: TCS Realigns Global Business Units for Cloud & AI Synergy",
        "description": "Management announced agile restructuring to accelerate cross-functional client delivery in AI and cybersecurity practices.",
        "category": "Management"
    },
    {
        "date": "2026-07-02",
        "stock": "TCS",
        "title": "Global Tech Spending Forecast Upgraded Benefiting Tier-1 Indian IT Exporters",
        "description": "Industry analysts project enterprise IT budgets to rebound strongly, positioning TCS for accelerated deal conversions.",
        "category": "Market"
    },
    {
        "date": "2026-06-18",
        "stock": "TCS",
        "title": "TCS Partners with Leading Automotive OEM for Autonomous Driving Simulation Stack",
        "description": "Collaborative initiative will harness high-performance cloud computing to train vision-language models for next-gen electric vehicles.",
        "category": "Products"
    },

    # INFY
    {
        "date": "2026-08-23",
        "stock": "INFY",
        "title": "Infosys Topaz Platform Crosses 150 Enterprise Client Deployments",
        "description": "Infosys reported accelerating traction for its suite of generative AI services across manufacturing, retail, and life sciences.",
        "category": "Technology"
    },
    {
        "date": "2026-08-18",
        "stock": "INFY",
        "title": "Infosys Upgrades Annual Constant-Currency Revenue Guidance to 5.5%-7.0%",
        "description": "Upward revision driven by mega-deal ramp-ups and improving discretionary tech spending in North America and Europe.",
        "category": "Earnings"
    },
    {
        "date": "2026-08-11",
        "stock": "INFY",
        "title": "Infosys Signs $450 Million Cloud Migration Contract with Nordic Telecom",
        "description": "Five-year agreement will consolidate legacy data centers into hybrid cloud architectures with zero-trust security frameworks.",
        "category": "Business"
    },
    {
        "date": "2026-08-01",
        "stock": "INFY",
        "title": "Infosys Inks Strategic Collaboration with Semiconductor Major for Silicon Design Automation",
        "description": "Partnership combines Infosys engineering services with advanced EDA tooling to expedite chip tape-outs for automotive edge devices.",
        "category": "Products"
    },
    {
        "date": "2026-07-22",
        "stock": "INFY",
        "title": "Attrition Rate at Infosys Drops to Multi-Year Low of 11.8%",
        "description": "Employee retention programs and internal upskilling in AI have stabilized workforce dynamics and reduced talent acquisition costs.",
        "category": "Management"
    },
    {
        "date": "2026-07-10",
        "stock": "INFY",
        "title": "Infosys Inaugurates New Digital Development Centre in Frankfurt, Germany",
        "description": "Facility will serve as a regional center of excellence for AI-driven sustainability and smart factory solutions.",
        "category": "Expansion"
    },
    {
        "date": "2026-06-25",
        "stock": "INFY",
        "title": "IT Sector Faces Temporary Margin Pressures Due to Annual Wage Hikes",
        "description": "Brokerage reports note short-term margin moderation across Tier-1 vendors while long-term deal pipeline remains healthy.",
        "category": "Market"
    },
    {
        "date": "2026-06-12",
        "stock": "INFY",
        "title": "Infosys Finacle Selected by Leading Southeast Asian Bank for Core Modernization",
        "description": "Cloud-native banking solution selected to power digital transactions and real-time payment rails for 20 million consumers.",
        "category": "Business"
    },

    # RELIANCE
    {
        "date": "2026-08-25",
        "stock": "RELIANCE",
        "title": "Jio Financial & Retail Synergies Fuel Robust Profitability Across Consumer Verticals",
        "description": "Reliance Industries highlighted accelerated customer additions in Jio 5G broadband and omnichannel retail store footprint.",
        "category": "Earnings"
    },
    {
        "date": "2026-08-19",
        "stock": "RELIANCE",
        "title": "Reliance New Energy Commences Phased Commissioning of Solar Giga Factory in Jamnagar",
        "description": "The integrated manufacturing complex aims to produce high-efficiency heterojunction solar modules and energy storage cells.",
        "category": "Expansion"
    },
    {
        "date": "2026-08-12",
        "stock": "RELIANCE",
        "title": "Reliance Retail Partners with Global Luxury Brands to Expand Omnichannel Footprint",
        "description": "Joint venture will introduce exclusive flagship fashion retail destinations across Mumbai, Delhi, and Bengaluru.",
        "category": "Business"
    },
    {
        "date": "2026-08-03",
        "stock": "RELIANCE",
        "title": "Jio Infocomm Crosses 50 Million True 5G Fixed Wireless Access (AirFiber) Subscribers",
        "description": "Rapid home broadband adoption strengthens average revenue per user (ARPU) and deepens consumer ecosystem monetization.",
        "category": "Technology"
    },
    {
        "date": "2026-07-25",
        "stock": "RELIANCE",
        "title": "Oil-to-Chemicals (O2C) Division Benefits from Favorable Gross Refining Margins",
        "description": "Refining throughput remained robust amid steady global distillate crack spreads and petrochemical demand recovery.",
        "category": "Market"
    },
    {
        "date": "2026-07-14",
        "stock": "RELIANCE",
        "title": "Reliance Announces Key Executive Appointments in Clean Hydrogen and Green Ammonia Divisions",
        "description": "Global energy industry veterans appointed to spearhead international green hydrogen export corridors and electrolyzer tech.",
        "category": "Management"
    },
    {
        "date": "2026-06-28",
        "stock": "RELIANCE",
        "title": "Jio Cloud AI Platform Unveiled with Free Cloud Storage for Indian Smartphone Users",
        "description": "Consumer cloud offering expected to drive customer stickiness and digital services engagement nationwide.",
        "category": "Products"
    },

    # HDFCBANK
    {
        "date": "2026-08-22",
        "stock": "HDFCBANK",
        "title": "HDFC Bank Net Interest Margin Stabilizes; Credit Growth Outpaces Industry Average",
        "description": "Leading private sector lender reported 16.5% year-on-year loan book expansion with stable asset quality metrics.",
        "category": "Earnings"
    },
    {
        "date": "2026-08-16",
        "stock": "HDFCBANK",
        "title": "HDFC Bank Expands Rural & Semi-Urban Branch Network with 300 New Smart Branches",
        "description": "Branch expansion aims to deepen low-cost CASA deposit mobilization and MSME priority sector lending.",
        "category": "Expansion"
    },
    {
        "date": "2026-08-09",
        "stock": "HDFCBANK",
        "title": "HDFC Bank Rolls Out Next-Gen Mobile Banking App with AI Financial Copilot",
        "description": "Rebuilt from ground up, the mobile application provides hyper-personalized wealth advisory and instant credit lines.",
        "category": "Products"
    },
    {
        "date": "2026-07-30",
        "stock": "HDFCBANK",
        "title": "Gross Non-Performing Assets (GNPA) Drop to 1.18%, Reflecting Prudent Risk Underwriting",
        "description": "Proactive provisioning and strong recovery mechanisms ensured superior asset quality across retail and wholesale books.",
        "category": "Business"
    },
    {
        "date": "2026-07-18",
        "stock": "HDFCBANK",
        "title": "Reserve Bank of India Monetary Policy Stance Keeps Liquidity Favorable for Large Banks",
        "description": "Central bank's balanced policy rate regime enables stable deposit accretion and credit off-take for premier private lenders.",
        "category": "Market"
    },
    {
        "date": "2026-07-05",
        "stock": "HDFCBANK",
        "title": "HDFC Bank Board Reappoints Key Risk and Compliance Committee Leadership",
        "description": "Strengthening institutional governance frameworks following successful integration of parent mortgage entity.",
        "category": "Management"
    },
    {
        "date": "2026-06-20",
        "stock": "HDFCBANK",
        "title": "HDFC Bank Launches Instant Pre-Approved Solar Rooftop Financing for Retail Consumers",
        "description": "Digital end-to-end green loan product offers subsidized rates under the national renewable energy mission.",
        "category": "Products"
    },

    # AAPL
    {
        "date": "2026-08-24",
        "stock": "AAPL",
        "title": "Apple Unveils On-Device Private Cloud AI Architecture Across Next-Gen Devices",
        "description": "Apple Intelligence features drive strong consumer upgrade intent with custom M-series and A-series silicon hardware accelerators.",
        "category": "Technology"
    },
    {
        "date": "2026-08-17",
        "stock": "AAPL",
        "title": "Apple Services Revenue Reaches All-Time Record of $24.8 Billion in Quarterly Results",
        "description": "App Store, iCloud, Apple Pay, and Music subscriptions continue double-digit expansion with over 1.1 billion paid subscribers.",
        "category": "Earnings"
    },
    {
        "date": "2026-08-10",
        "stock": "AAPL",
        "title": "Apple Expands Manufacturing Footprint with Increased Output in India and Vietnam",
        "description": "Supply chain diversification achieves over 25% production share outside China, mitigating geopolitical friction.",
        "category": "Expansion"
    },
    {
        "date": "2026-07-31",
        "stock": "AAPL",
        "title": "Apple Partners with Leading Health Research Institutions for Non-Invasive Glucose Monitoring Trials",
        "description": "Next-generation sensor research in wearable devices shows promising preliminary efficacy in optical biosensing.",
        "category": "Products"
    },
    {
        "date": "2026-07-20",
        "stock": "AAPL",
        "title": "Global Smartphone Shipments Show Strong Premiumization Trend Benefiting iPhone Pro Lineup",
        "description": "Market research reveals consumer preference shifting toward higher ASP flagship smartphones across emerging markets.",
        "category": "Market"
    },
    {
        "date": "2026-07-08",
        "stock": "AAPL",
        "title": "Apple Announces $110 Billion Share Repurchase Authorization and Increased Cash Dividend",
        "description": "Capital allocation strategy returns significant value to long-term institutional and retail shareholders.",
        "category": "Earnings"
    },
    {
        "date": "2026-06-22",
        "stock": "AAPL",
        "title": "Apple Vision Pro Ecosystem Expands with 2,500 Spatial Enterprise Productivity Applications",
        "description": "Medical training, architectural CAD, and immersive 3D collaboration gain commercial traction in Fortune 100 enterprises.",
        "category": "Business"
    }
]

def generate_news_json():
    json_path = os.path.join("data", "news", "news.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(NEWS_DATA, f, indent=2)
    print(f"Generated {len(NEWS_DATA)} news articles at {json_path}")

if __name__ == "__main__":
    for sym, cfg in STOCKS_CONFIG.items():
        generate_stock_csv(sym, cfg, num_days=130)
    generate_news_json()
    print("All sample datasets successfully generated!")
