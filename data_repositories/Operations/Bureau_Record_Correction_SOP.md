# Bureau Record Correction SOP

## Scope & Applicability
This standard operating procedure governs the rectification of erroneous credit lines, charge-off misclassifications, and identity merge errors across all 4 licensed credit information companies (CIBIL, Experian, Equifax, CRIF).

## Prerequisites
- Valid customer authorization mandate signed digitally.
- Lender confirmation letter specifying Account Number and Corrected DPDO (Days Past Due).
- Internal Incident Ticket ID linked to TruCortex CRM.

## Step-by-Step Rectification Workflow
1. **Intake Validation**: Verify that dispute reason is supported by documentary evidence.
2. **Payload Construction**: Generate the XML/JSON dispute correction packet according to CIR v5.0 specifications.
3. **Gateway Dispatch**: Transmit batch updates through the Technical API Gateway using OAuth2 MTLS credentials.
4. **Reconciliation**: Parse response acknowledgments (ACK/NACK) within 24 hours.

## Escalation Matrix
- **L1 Support**: First contact verification and data capture (SLA: 24h).
- **L2 Operations Specialist**: Lender data reconciliation and bureau liaison (SLA: 72h).
- **L3 Governance & Legal**: Regulatory disputes and ombudsman complaints (SLA: 5 business days).
