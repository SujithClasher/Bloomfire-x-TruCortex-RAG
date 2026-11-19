# TransUnion CIBIL Microfinance Solutions & SRO Governance Framework

## Executive Overview
TransUnion CIBIL's **Microfinance Solutions & Products** ecosystem is purpose-built to accelerate **Financial Inclusion** while maintaining strict risk controls for microfinance institutions (NBFC-MFIs), Small Finance Banks (SFBs), rural cooperatives, and commercial banks in India.

The suite comprises **CIBIL Microfinance Score, CIBIL Microfinance Report, Microfinance CreditVision® Algorithms, Microfinance Portfolio Review, and Grameen Score**, operating under the regulatory supervision of the **Reserve Bank of India (RBI)** and the industry oversight of Self-Regulatory Organizations (SROs like MFIN and Sa-Dhan).

## CIBIL Microfinance Report (MFI CIR)
The CIBIL Microfinance Report delivers a 360-degree consolidated credit profile of low-income and rural micro-borrowers, enabling lenders to make informed, responsible underwriting decisions.

### Structural Sections of the MFI Report
1. **Demographic & Center Identification**:
   - Borrower Name, Spouse/Father Name, verified Voter ID (EPIC), Ration Card number, and anonymized biometric Aadhaar verification token.
   - Microfinance Center Name, JLG Center ID, Village/Ward Code, and Center Meeting Day.
2. **Microfinance Score Summary**: The active 3-digit score (300–900), risk band category, and key risk driver codes.
3. **Aggregate Loan Summary**: Total active loans, total sanctioned limit, total current outstanding balance, and total overdue amount across all institutional lenders.
4. **Granular Tradeline Accounts Table**:
   - Week-by-week and month-by-month repayment telemetry for up to 36 months.
   - Frequency tracking: Weekly, Fortnightly, and Monthly loan installment collections.
   - Days Past Due (DPD) status: `000` (on-time), `030`, `060`, `090+`, or settled/written-off status.
5. **Inquiry Log**: Timestamped record of inquiries submitted by other microfinance lenders within the past 12 to 24 months.

## CIBIL Microfinance Score (300 to 900)
A specialized statistical score calibrating default probability specifically for collateral-free micro-credit:
- **700 – 900 (Prime / Very Low Default Risk)**: Impeccable peer repayment record; eligible for higher ticket-size micro-enterprise loans.
- **650 – 699 (Near Prime / Low Risk)**: Steady repayment track record; standard approval.
- **600 – 649 (Moderate Risk)**: Occasional 30+ DPD delays or multiple concurrent loans; requires household income re-verification.
- **550 – 599 (High Risk / Sub-prime)**: Elevated delinquency; concurrent overdue loans.
- **300 – 549 (Very High Risk / Severe Default)**: High probability of default or loss classification.
- **Score 0 or -1 (Untapped / New-to-MFI)**: Borrowers with less than 6 months of active microfinance history.

## Microfinance CreditVision® Algorithms
Microfinance CreditVision Algorithms analyze longitudinal, trended bureau data over time rather than static single-point-in-time snapshots:
- **Borrower Over-Leverage Detection**: Evaluates the velocity of loan acquisitions across multiple MFIs to detect credit-hungry borrowing spirals.
- **Repayment Acceleration & Deceleration**: Analyzes whether a borrower's overall indebtedness is shrinking or snowballing across lenders.
- **SRO Guardrails & Code of Conduct Compliance**: Enforces regulatory limits established by MFIN (Microfinance Institutions Network) and Sa-Dhan, preventing multi-lending defaults.

## Microfinance Portfolio Review
A powerful retrospective and ongoing portfolio risk management tool:
- **Vintage Analysis**: Tracks loan cohorts by sanction vintage to evaluate credit underwriting quality over time.
- **Geographic Risk Concentration**: Identifies high-risk districts, blocks, or pin codes impacted by local agricultural shocks, natural disasters, or community stress.
- **Early Warning Signals (EWS)**: Proactively alerts lenders when their existing borrowers begin defaulting on tradelines held at other competing MFIs.

## Financial Inclusion & Grameen Score
- **Grameen Score**: Dedicated 300–900 rural credit scoring model tailored for agricultural households, factoring Kisan Credit Cards (KCC), tractor loans, crop harvest rhythms, and Mudra loans (Shishu, Kishore, Tarun).
- **Graduation to Formal Credit**: Tracks microfinance borrowers as they establish credit histories, enabling them to graduate from Joint Liability Group (JLG) group-lending to individual MSME commercial facilities.
