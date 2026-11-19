# Enhanced CreditVision Score & Consumer CIR Guide

## Executive Overview
TransUnion CIBIL's **Enhanced CreditVision® Score** and **Enhanced Consumer Credit Information Report (CIR)** represent the modern standard in consumer credit intelligence, moving from static single-point-in-time bureau snapshots to 36 months of longitudinal trended payment behavior.

## Enhanced CreditVision® Score (300 to 900)
The Enhanced CreditVision Score evaluates dynamic repayment patterns to assess the probability of a consumer defaulting within the subsequent 12 months.

### Score Range & Credit Quality Tiers
- **750 – 900 (Super Prime / Excellent)**: Default rate < 1.0%; eligible for premium interest rate discounts and pre-approved personal loans.
- **700 – 749 (Prime / Good)**: Healthy repayment history with low utilization; high approval certainty.
- **650 – 699 (Near Prime / Fair)**: Minor blemishes or high revolving credit card utilization; acceptable under standard underwriting terms.
- **600 – 649 (Sub-prime / Cautionary)**: Recent 30-day DPD or multiple unsecured inquiries; elevated default likelihood.
- **300 – 599 (High Risk / Severely Delinquent)**: Serious payment defaults, charge-offs, or settled accounts.

### Trended CreditVision Telemetry
Unlike traditional bureau algorithms, CreditVision evaluates:
- **Balance Velocity**: Whether a borrower's overall outstanding balances are increasing, staying flat, or paying down over time.
- **Payment-to-Balance Ratio**: Distinguishes between "transactors" who clear their full credit card dues every billing cycle versus "revolvers" who pay only the minimum amount due (MAD).
- **Utilization Trajectory**: Flags borrowers who are rapidly exhausting their credit card limits across multiple banks.
- **Credit Migration**: Identifies consumers whose financial health is improving, opening credit opportunities for previously denied applicants.

## Enhanced Consumer CIR (Credit Information Report) Layout
The standardized CIR contains 6 primary sections:
1. **Identification Section**: Name, Date of Birth, Gender, PAN, Passport, Voter ID, and Driver's License identifiers.
2. **Contact Telemetry**: Historical residential and office addresses, mobile phone numbers, and email IDs with timestamped reporting dates.
3. **CIBIL Score & Risk Factors**: The latest 3-digit score accompanied by top negative and positive contributing factors.
4. **Summary Grid**: Total number of accounts, total current balance, total overdue balance, and date of most recent account opened.
5. **Detailed Account Tradelines**: Granular account-by-account breakdown (lender type, account type, sanctioned limit, current balance, and up to 36 months of monthly payment status / DPD grid).
6. **Inquiry Log**: Comprehensive timestamped history of all hard inquiries initiated by prospective lenders within the past 24 months.
