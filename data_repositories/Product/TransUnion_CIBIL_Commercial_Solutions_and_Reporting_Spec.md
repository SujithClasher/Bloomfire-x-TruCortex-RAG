# TransUnion CIBIL Commercial Solutions & Reporting Specification

## Executive Overview
TransUnion CIBIL's **Commercial Solutions & Products** suite delivers enterprise-grade risk assessment and intelligence for business underwriting in India. It encompasses **CreditVision® CIBIL Commercial Rank (CV CMR), the Enhanced CIBIL Commercial Report, Commercial NTC Score, Application Review, and Commercial Portfolio Management**.

The platform assists commercial banks, non-banking financial companies (NBFCs), and institutional lenders in evaluating micro, small, and medium enterprises (MSMEs), mid-market corporations, and large corporate entities.

## Enhanced CIBIL Commercial Report (Commercial CIR v5.0)
The Enhanced Commercial Report is TransUnion CIBIL's premier decisioning report for commercial credit evaluation, designed to give lenders a 360-degree view of business credit health, group corporate linkages, and counterparty risks.

### Advanced Architectural Capabilities
1. **Multi-Dimensional Business Profiles**: Evaluates corporate entities across legal constitutions—Private Limited Companies, Public Limited Companies, Limited Liability Partnerships (LLP), Partnership Firms, Trusts, and Sole Proprietorships.
2. **Intra-Month Reporting & Telemetry**:
   - Captures intraday and intra-month facility updates instead of relying solely on end-of-month bureau submissions.
   - Detects sudden spikes in working capital credit line utilization, ad-hoc limit drawdowns, or unpaid trade liabilities.
3. **Entity and Related-Party Cross-Linkages**:
   - Maps parent companies, subsidiary operating units, sister concerns, and cross-guarantors.
   - Cross-references the personal credit profiles and repayment discipline of company Promoters, Directors, and Key Managerial Personnel (KMP).
4. **Consortium and Multiple Banking Arrangements**:
   - Aggregates fund-based limits (Cash Credit, Overdraft, Term Loans, Working Capital Demand Loans) and non-fund-based facilities (Bank Guarantees, Letters of Credit) across all consortium lenders under RBI prudential directives.
5. **Commercial DPD & Asset Classification**:
   - Tracks 24 to 36 months of Days Past Due (DPD) telemetry across all institutional lenders.
   - Flags SMA-0 (1-30 days overdue), SMA-1 (31-60 days overdue), SMA-2 (61-90 days overdue), and Non-Performing Asset (NPA) classifications.

## CreditVision® CIBIL Commercial Rank (CV CMR)
CV CMR is a machine-learning-driven commercial credit rank that assesses the likelihood of a business defaulting on its credit facilities within the subsequent 12 months.

### Commercial Rank Scale (CMR-1 to CMR-10)
- **CMR-1 to CMR-3 (Prime Commercial / Lowest Default Risk)**:
  - Benchmark default rate: **0.5% – 2.5%**.
  - Blue-chip corporates and highly established enterprises with pristine banking relationships, stable working capital liquidity, and low credit volatility.
- **CMR-4 to CMR-6 (Moderate Risk / Acceptable Commercial Credit)**:
  - Benchmark default rate: **2.6% – 7.5%**.
  - Established MSMEs and growth businesses with healthy operational turnover; occasional short-term working capital friction.
- **CMR-7 to CMR-10 (High Risk / Severe Default Probability)**:
  - Benchmark default rate: **> 7.5% (exceeding 30% in CMR-10)**.
  - Entities exhibiting high revolving debt leverage, frequent cheque / NACH mandate dishonors, or active SMA-2 / NPA statuses across consortium lenders.

## Commercial NTC (New-to-Credit) Score
A specialized risk scoring solution designed for new commercial entities, newly registered MSMEs, and startups lacking formal commercial credit track records.

### Core Scoring Surrogates
- **Promoter & Director Personal Credit Discipline**: Evaluates the personal CIBIL Scores (300–900) of company directors and guarantors.
- **GSTN & Tax Compliance Metrics**: Analyzes Goods and Services Tax (GST) filing regularity, quarterly turnover volume consistency, and tax liability settlement velocity.
- **Banking Transaction Telemetry**: Evaluates average monthly balances, debit-to-credit turnover velocity, and inward/outward cheque returns via consent-based Account Aggregator (AA) feeds.

## Commercial Application Review & Portfolio Management
- **Application Review Solutions**: Flags undisclosed related-party liabilities, corporate registry anomalies, and synthetic entity formation before loan sanctioning.
- **Commercial Portfolio Management**: Automates covenant tracking, monitors cross-default occurrences at other lenders, and delivers real-time Early Warning Signals (EWS).
