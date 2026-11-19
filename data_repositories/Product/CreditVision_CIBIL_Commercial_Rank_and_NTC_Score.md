# CreditVision CIBIL Commercial Rank (CV CMR) & Commercial NTC Score Specification

## Executive Overview
TransUnion CIBIL provides two cornerstone scoring solutions for commercial and business underwriting:
1. **CreditVision® CIBIL Commercial Rank (CV CMR)**: For commercial enterprises with existing credit facilities.
2. **Commercial NTC (New-to-Credit) Score**: For new commercial entities, MSMEs, and startups lacking prior commercial credit histories.

## CreditVision® CIBIL Commercial Rank (CV CMR)
CreditVision CMR is an advanced commercial credit ranking system that assesses the risk of a commercial entity defaulting on its credit obligations over the next 12 months.

### Commercial Rank Scale (CMR-1 to CMR-10)
CV CMR maps enterprise risk onto a standardized 10-point scale:
- **CMR-1 to CMR-3 (Prime Commercial / Lowest Risk)**:
  - Benchmark default probability: **0.5% – 2.5%**.
  - High-tier corporate enterprises, flawless multi-bank repayment history, low balance volatility, excellent debt service coverage.
- **CMR-4 to CMR-6 (Moderate Risk / Acceptable Commercial Profile)**:
  - Benchmark default probability: **2.6% – 7.5%**.
  - Established MSMEs with healthy turnover; occasional temporary working capital overutilization or minor non-delinquent delayed collections.
- **CMR-7 to CMR-10 (High Risk / Severe Default Probability)**:
  - Benchmark default probability: **> 7.5% (up to 35% in CMR-10)**.
  - Entities exhibiting high revolving credit leverage, multiple recent dishonored cheques/NACH mandates, and 60+ DPD delinquencies.

### Key Analytical Dimensions Evaluated by CV CMR
- **Trended Working Capital Velocity**: 36 months of longitudinal balance trends, detecting early signs of credit stress before formal default.
- **Cross-Lender Exposure Telemetry**: Aggregated exposure across consortium banking arrangements, term loans, non-fund-based limits (Letter of Credit, Bank Guarantees).
- **Payment Delay Trajectory**: Accelerating or decelerating trend in settling supplier credit and bank dues.

## Commercial NTC (New-to-Credit) Score
The **Commercial NTC Score** solves the classic "thin-file" challenge where newly incorporated companies, partnership firms, and micro-enterprises cannot obtain credit due to lack of prior commercial bureau records.

### Core Architecture & Surrogate Data Feeds
- **Promoter & Director Personal Credit Discipline**: Evaluates the personal CIBIL Credit Scores (300–900) of company directors, partners, and key managerial personnel (KMP).
- **GSTN & Tax Compliance Telemetry**: Consistency of monthly and quarterly Goods and Services Tax (GST) filings, tax payment consistency, and reported turnover volumes.
- **Banking Transaction Metrics**: Average monthly banking balances, transaction velocity, and cheque return frequency derived from consent-based Account Aggregator (AA) feeds.
- **Entity Firmographics**: Business vintage, industry sector risk coefficient, geographical operating cluster, and corporate structure (Private Limited, LLP, Sole Proprietorship).

### Underwriting Impact
By combining Commercial NTC Score with CV CMR, financial institutions can safely onboard unbanked MSMEs, expand commercial portfolios, and implement risk-based interest pricing without increasing provisioning costs.
