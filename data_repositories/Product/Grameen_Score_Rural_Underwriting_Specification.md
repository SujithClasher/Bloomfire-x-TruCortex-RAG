# Grameen Score — Rural Credit Underwriting Specification

## Executive Overview
The **Grameen Score** is TransUnion CIBIL's dedicated scoring model tailored specifically for rural borrowers, agricultural households, and rural micro-enterprises. It bridges the financial inclusion divide by evaluating non-traditional rural credit behavior and seasonal income cycles.

Unlike conventional urban consumer scoring algorithms that assume steady monthly salaried cash flows, Grameen Score is architected to account for agricultural harvesting rhythms, crop sale cycles, and multi-stream rural income (farming, dairy, allied agricultural trades, and government subsidies).

## Methodological Architecture & Rural Data Inputs
The Grameen Score integrates diverse rural credit instruments:
- **Kisan Credit Cards (KCC)**: Credit limit utilization, seasonal drawdowns during sowing season (Kharif / Rabi), and post-harvest repayments.
- **Tractor & Agricultural Machinery Loans**: Equipment asset financing repayment track record.
- **Pradhan Mantri MUDRA Yojana (PMMY) Loans**: Shishu (up to ₹50,000), Kishore (₹50,000 to ₹5,00,000), and Tarun (₹5,00,000 to ₹10,00,000) small business loans.
- **Allied Agricultural Loans**: Dairy cattle loans, poultry farming credit, warehouse receipt financing, and solar pump irrigation loans.
- **Microfinance Tradelines**: Peer group JLG and SHG repayment discipline across 36 months of trended data.

## Score Range & Risk Segmentation
The Grameen Score generates a 3-digit score ranging from **300 to 900**:
- **720 – 900 (Rural Prime)**: Consistent multi-season loan renewal without default; immediate automated straight-through processing (STP) for rural credit approvals.
- **660 – 719 (Rural Near-Prime)**: Steady repayment track record with minor seasonal shifts in payment timing due to monsoon or market pricing volatility.
- **600 – 659 (Moderate Rural Risk)**: Seasonal crop delays resulting in 30-60 DPD; requires verification of crop yield or land holding documentation.
- **300 – 599 (High Risk / Default Prone)**: Severe non-performing assets (NPA) or willful defaults across institutional lenders.
- **Untapped / Thin File Segment**: Borrowers with zero formal credit history are scored using surrogate telemetry (geographical agricultural yields, district rainfall indices, and rural cooperative records).

## Strategic Value for Financial Institutions
- **Priority Sector Lending (PSL) Compliance**: Enables public sector and commercial banks to safely meet mandatory RBI Priority Sector Lending targets for small and marginal farmers (SMFs).
- **Default Reduction**: Benchmarking tests show that lenders deploying Grameen Score achieve a **28% reduction in rural credit default rates** compared to generic consumer credit scorecards.
- **Faster Turnaround Time (TAT)**: Rural branch managers can reduce sanction times from 10–14 days down to under 24 hours through automated rule-based policy triggers.
