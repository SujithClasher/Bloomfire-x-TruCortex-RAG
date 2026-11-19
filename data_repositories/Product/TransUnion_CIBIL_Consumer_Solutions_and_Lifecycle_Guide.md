# TransUnion CIBIL Consumer Solutions & Lifecycle Guide

## Executive Overview
TransUnion CIBIL's **Consumer Solutions & Products** suite provides end-to-end credit intelligence covering every phase of the consumer lending lifecycle: **Customer Acquisition, Application Review, Credit Information Reporting, Portfolio Management, and Collections Management**. 

Operating under the Credit Information Companies (Regulation) Act (CICRA 2005) and RBI oversight, TransUnion CIBIL compiles credit records for over 1 billion individual consumer profiles across India.

## CIBIL Consumer Report & Enhanced Consumer CIR (Credit Information Report)
The CIBIL Consumer Report is the industry-standard credit file utilized by banks, NBFCs, and fintechs to evaluate retail borrowers for personal loans, home loans, auto loans, and credit cards.

### Core Sections of the Enhanced Consumer CIR
1. **Identification Section**: Verified demographic identifiers including Full Name, Date of Birth (DOB), Gender, Income Tax PAN, Passport Number, Voter ID (EPIC), and Driver's License.
2. **Contact Telemetry**: Historical residential and employment addresses, postal pincodes, verified mobile numbers, and email IDs with reporting recency timestamps.
3. **CIBIL Credit Score (300–900)**: Numeric 3-digit score reflecting the borrower's probability of default over the next 12 months, accompanied by top contributing risk factors.
4. **Summary Grid**: High-level snapshot of total active facilities, total closed accounts, total sanctioned credit limits, total outstanding balance, and total overdue amounts.
5. **Detailed Account Tradelines & DPD Grid**:
   - Month-by-month payment tracking for up to 36 months per credit facility.
   - Standardized Days Past Due (DPD) status indicators:
     - `000`: Payment settled on-time / zero days past due.
     - `001–089`: Short-term delinquency (1 to 89 days past due).
     - `090`: Non-Performing Asset (NPA) classification under RBI prudential norms.
     - `SUB`: Sub-Standard Asset (delinquent beyond 90 days).
     - `DBT`: Doubtful Asset (uncollected beyond 12 months).
     - `LSS`: Loss Asset / Written-off debt.
6. **Inquiry Telemetry (Enquiry History)**: Comprehensive log of all "hard" credit inquiries made by prospective lenders within the past 24 to 36 months.

## Enhanced CreditVision® Score (300 to 900)
The **Enhanced CreditVision Score** enhances conventional bureau scores by replacing single-point-in-time snapshots with **36 months of longitudinal trended data telemetry**.

### Credit Quality Tiers & Risk Mapping
- **750 – 900 (Super Prime / Prime)**: Default probability < 1.0%. Borrowers qualify for automated straight-through processing (STP) and preferential interest rate discounts.
- **700 – 749 (Near Prime / Good)**: Healthy repayment discipline; standard retail credit approval with minimal underwriting friction.
- **650 – 699 (Moderate Risk / Fair)**: Acceptable credit profile; may exhibit high revolving card utilization or occasional seasonal delays.
- **600 – 649 (Sub-prime / Cautionary)**: Higher delinquency risk; requires stricter debt-to-income (DTI) and collateral checks.
- **300 – 599 (High Risk / Severe Delinquency)**: Accounts with active charge-offs, settled classifications, or chronic 60+ DPD delinquencies.

### Key Trended Behavioral Metrics
- **Transactor vs Revolver Segmentation**: Distinguishes responsible transactors (who clear credit card balances in full each billing cycle) from revolvers (who repeatedly roll over debt by paying only the Minimum Amount Due).
- **Balance Velocity & Trajectory**: Analyzes whether an applicant's total liabilities are amortizing downwards or accelerating upwards.
- **Utilization Velocity**: Monitors aggregate credit card utilization trends across all member banks over rolling 3, 6, and 12-month intervals.

## Consumer Customer Acquisition Solutions
- **Prescreen & Campaign Targeting**: Enables financial institutions to prescreen prospect lists against bureau risk score cutoffs, eliminating marketing spend on sub-prime segments.
- **Pre-Approved Offer Sizing**: Estimates pre-approved loan amounts and credit limits using bureau-derived debt capacity algorithms without logging hard inquiries.

## Consumer Collections Management & Debt Recovery
- **Debt Management Models (DMM)**: Predictive scorecards segmenting delinquent accounts by **willingness to pay** versus **capacity to pay**.
- **Delinquency Bucket Optimization**: Directs low-cost digital communication (SMS/WhatsApp) to early-bucket 1–30 DPD accounts, while routing chronic 60+ DPD accounts to specialized recovery units.
- **Skip Tracing & Contact Enrichment**: Surfaces recent address and phone updates reported by other credit institutions to re-establish contact with hard-to-reach borrowers.

## Portfolio Review Report
A strategic lifecycle management solution that monitors existing customer loan books:
- Detects early warning delinquency signals occurring at other external banks.
- Supports proactive Credit Limit Increases (CLI) for prime transactors and Credit Limit Decreases (CLD) for over-leveraged borrowers.
