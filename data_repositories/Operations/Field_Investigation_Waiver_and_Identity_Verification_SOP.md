# Field Investigation Waiver Policy & Identity Verification (IDV) SOP

## Executive Overview
The **Field Investigation Waiver Policy (FI Waiver Solution)** and **Identity Verification (IDV / IDVision)** represent TransUnion CIBIL's automated fraud risk mitigation and digital onboarding suite. 

Traditional lending workflows mandate that verification agents physically visit a customer's residence or office—a process that introduces 3 to 5 business days of latency, high field investigation costs, and vulnerability to human verification error. The FI Waiver Solution replaces physical inspections with instant digital verification.

## Field Investigation (FI) Waiver Policy & Automation Framework

### Operational Architecture
The FI Waiver engine analyzes multidimensional bureau and telecom signals to determine whether physical field visits can be safely waived:
- **Address Stability Index (ASI)**: Evaluates the historical stability and consistency of the applicant's residential and commercial addresses across past credit applications over a 36-month window.
- **Geographic & Demographic Match**: Cross-references postal pincode risk scores, geolocation metadata, and verified utility billing records.
- **Bureau Verification Score**: Evaluates credit bureau vintage, past successful repayments, and institutional lender confirmation.

### Operational Benefits & Business Impact
- **Turnaround Time (TAT)**: Replaces 72–120 hours of manual physical visits with an instantaneous **sub-30 second** automated decision.
- **Cost Reduction**: Eliminates third-party physical investigation agency fees, saving lenders up to **65% to 75%** per verified loan application.
- **Higher Conversion**: Dramatically reduces customer drop-off during the loan origination journey.

## Identity Verification (IDV / IDVision) Architecture

### Multi-Layered Digital Identity Validation
IDV operates in real-time to detect synthetic identities, identity theft, and application fraud:
1. **e-KYC & Demographic Verification**: Instant fuzzy matching of applicant identity against official records (PAN, Aadhaar virtual ID, Voter ID, Passport, Driving License) with strict adherence to RBI Master Directions on KYC.
2. **Fraud Velocity Alerts**: Triggers real-time security alerts if the applicant's phone number, PAN, or device fingerprint has appeared across an unusually high number of credit applications within a 24-hour or 7-day period.
3. **Address & Contact Discrepancy Heuristics**: Flags mismatches between applicant-provided details and existing bureau profile records.

## Compliance and Regulatory Governance
All automated FI waivers and digital IDV verifications comply with:
- **RBI Digital Lending Guidelines (2022/2026)**: Mandating explicit borrower consent and prohibiting unauthorized data scraping.
- **Prevention of Money Laundering Act (PMLA)**: Enforcing strict customer due diligence (CDD) and AML screening.
- **Digital Personal Data Protection (DPDP) Act 2023**: Requiring secure, tokenized storage of customer identity markers.
