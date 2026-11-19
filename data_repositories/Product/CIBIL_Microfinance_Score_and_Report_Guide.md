# CIBIL Microfinance Score & Report Specification

## Executive Overview
The **CIBIL Microfinance Score (MFI Score)** is TransUnion CIBIL's specialized 3-digit credit score ranging from **300 to 900**, designed specifically to assess the creditworthiness and default probability of microfinance, rural, and semi-urban borrowers. 

It provides banks, Non-Banking Financial Company - Microfinance Institutions (NBFC-MFIs), and Small Finance Banks (SFBs) with a standardized numeric risk assessment tailored to collateral-free micro-credit, Joint Liability Group (JLG) lending, and Self-Help Group (SHG) financing.

## Scoring Range & Risk Categorization
The CIBIL Microfinance Score is calibrated on a scale of 300 to 900:
- **700 – 900 (Prime / Very Low Risk)**: Borrowers demonstrating impeccable repayment discipline across all micro-loans. Highest approval rates and eligibility for preferential interest rates.
- **650 – 699 (Near Prime / Low Risk)**: Consistent repayment track record with minor seasonal delays; highly acceptable for standard microfinance disbursements.
- **600 – 649 (Moderate Risk)**: Occasional 30+ DPD delinquencies or multiple active micro-loans; requires closer assessment of household income.
- **550 – 599 (High Risk / Sub-prime)**: Elevated delinquency risk; multiple overdue payments across concurrent lenders.
- **300 – 549 (Very High Risk)**: High probability of default, charge-offs, or wilful default; typically rejected under standard underwriting rules.
- **Score 0 or -1 (New-to-Microfinance / Untapped)**: Borrowers with less than 6 months of active microfinance tradeline history or zero prior micro-credit records.

## Key Scoring Parameters & Weightages
The CIBIL Microfinance scoring algorithm is evaluated on 4 core behavioral dimensions:
1. **Repayment Discipline & DPD History (35% weight)**: Analysis of past payment track record over a 24-to-36 month window, tracking on-time settlement of weekly, fortnightly, and monthly installments.
2. **Indebtedness & Multiple Lending Exposure (25% weight)**: Evaluation of total outstanding micro-loans, aggregate balance, and the number of concurrent active MFI lenders to prevent borrower over-indebtedness.
3. **Inquiry Velocity & Credit Seeking Behavior (20% weight)**: Frequency of recent loan applications submitted across member institutions within the last 30, 60, and 90 days.
4. **Tradeline Vintage & Credit Relationship Mix (20% weight)**: Length of borrower's microfinance credit history, completion of prior loan cycles, and graduation from JLG group loans to individual enterprise loans.

## Regulatory Framework & RBI Microfinance Directives
The CIBIL Microfinance Score and Report operate under strict compliance with the **RBI Master Directions on Regulatory Framework for Microfinance Loans (2022/2026)**:
- **Household Income Limit**: Microfinance loans are defined as collateral-free credit extended to households having an annual income up to **₹3,00,000**.
- **Debt Service Ratio (Limit on Monthly EMI Outflow)**: Total monthly loan repayment obligations (including principal and interest across all lenders) must **not exceed 50%** of the borrower's monthly household income.
- **Real-Time Bureau Submission**: Every member lender is mandated by RBI and CICRA 2005 to submit all microfinance loan originations, weekly/monthly collections, and defaults to CIBIL and all credit information companies in real-time or weekly batch cycles.
- **Prohibition on Prepayment Penalties**: Borrowers with CIBIL Microfinance accounts cannot be charged prepayment or foreclosure penalties for settling dues ahead of schedule.

## CIBIL Microfinance Report Structure
The standardized CIBIL Microfinance Report contains:
- **Demographic Identification**: Borrower name, spouse/father name, verified Voter ID (EPIC), Ration Card, and biometric Aadhaar reference token (never unmasked 12-digit Aadhaar).
- **Group Details**: JLG / SHG center name, group leader ID, and village/ward geographic cluster code.
- **Summary Section**: Aggregate active loans, total sanctioned amount, total current outstanding balance, total overdue amount, and latest CIBIL MFI Score.
- **Account Details Grid**: Granular week-by-week and month-by-month Days Past Due (DPD) telemetry (e.g. 000 = on-time, 030 = 30 days overdue, 060 = 60 days overdue, LSS = loss asset).
- **Inquiry History**: Complete timestamped audit of member MFIs that have accessed the borrower's credit profile.
