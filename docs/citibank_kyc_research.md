# Citibank KYC Process: Digital Onboarding & Document Submission Research

> Research compiled February 2026 for the Citibank AI Hackathon

---

## 1. OneKYC Program — Global Unified Framework

Citibank operates a **OneKYC Program** that unifies its Know Your Customer process across all geographies under:

- **One global policy** aligned with the highest regulatory standard Citi has adopted as its baseline
- **One client risk scoring model** applied consistently worldwide
- **One enterprise data repository** — CitiKYC — acting as the single source of truth for all KYC records
- **Unified governance** spanning more than 100 countries where Citi conducts business

The OneKYC Program exists to prevent the flow of illicit funds through the financial system and to meet local regulatory requirements that, in many jurisdictions, exceed the US baseline.

---

## 2. CitiDirect® Commercial Banking Platform

CitiDirect® is Citi's flagship digital platform for commercial clients, bringing together Cash, Loans, Trade, FX, Servicing, and **KYC/Onboarding** into a single 360° view of the client's banking relationship.

### Key Digital Onboarding Capabilities

| Feature | Detail |
|---|---|
| **Streamlined Onboarding** | Fully digitised process with real-time status updates |
| **Onboarding Time Reduction** | Cut by **41%** since digital rollout |
| **Country Coverage** | Account opening expedited in **49 countries and jurisdictions** |
| **Digital Request Coverage** | **90% of incoming account requests** handled digitally in live countries |
| **E-Signatures** | Supported in **72 countries and jurisdictions** |
| **KYC Renewals** | *'One field, one-time'* approach — pre-filled data, automated notifications |
| **Document Submission** | Single unified checklist covering Account Opening, KYC, and Product docs |
| **Digital Servicing Hub** | Centralises client queries, updates, and document submissions |

### Documentation 2.0
Citi introduced **Documentation 2.0** to eliminate local country-specific terms wherever possible, centralising essential terms into a simplified structure that reduces complexity and friction for international clients.

---

## 3. Fenergo Platform — Transfer Agency (2025)

Citi's Global Transfer Agency business deployed **Fenergo's Client Lifecycle Management platform** for regulated funds in Europe. This provides:

- Customised, policy-driven risk assessment for AML and KYC checks
- Automated data validations
- Real-time reporting via API connectivity
- More seamless investor onboarding and due diligence

---

## 4. AML/KYC Document Requirements

Citi's AML documentation requirements vary by jurisdiction and entity type but typically include:

- **Corporate entity documents**: Certificate of Incorporation, Articles of Association, board resolutions
- **Beneficial ownership**: Identification of shareholders, directors, and account operators
- **Personal identification**: Government-issued ID for key persons (in many jurisdictions)
- **Business purpose**: Documentation explaining the nature and purpose of the banking relationship

> **Critical Compliance Point**: Account openings cannot be completed until **all AML/KYC requirements are fully satisfied**, with no exceptions.

Citi is also a contributor and user of the **SWIFT KYC Registry**, an information-exchange platform that enables financial institutions to share KYC data centrally, increasing transparency and making correspondent banking relationships easier to maintain.

---

## 5. Citi's AML Control Lifecycle

Citi structures its AML compliance around three phases:

1. **Prevention** — Robust KYC program with globally consistent standards, customer risk scoring, and an enterprise-wide data repository
2. **Detection** — AI-powered transaction monitoring, anomaly detection, and behavioural analytics
3. **Reporting** — SAR (Suspicious Activity Report) filing and regulatory reporting

---

## 6. Technology Investment & AI Strategy

### Scale of Investment
- **~$12 billion** invested in technology in 2024 alone
- **$30 billion+** invested in technology over the past three years
- **$2.4 billion** in technology and communications in Q1 2025

### Google Cloud Strategic Partnership (October 2024)
Citi signed a **multi-year strategic agreement** with Google Cloud to:
- Migrate workloads to secure, scalable cloud infrastructure
- Enhance AI/ML capabilities across the enterprise
- Enable high-performance computing for millions of daily financial calculations

### Internal AI Deployments
| Tool | Purpose |
|---|---|
| **Citi Stylus** | Document intelligence — automated extraction from regulatory and client documents |
| **Citi Assist** | Knowledge management assistant for compliance and operations teams |
| **AskWealth** | Generative AI assistant for wealth advisory teams |
| **Advisor Insights** | ML-based markets dashboard for wealth advisors |
| AI Coding Tools | Deployed to **30,000 developers**; completed ~220,000 automated code reviews |

### Legacy Modernisation
- **2,000+ legacy applications decommissioned** over three years
- **130 more retired or replaced** in Q1 2025 alone
- CEO Jane Fraser acknowledged "decades of underinvestment" driving the transformation

---

## 7. The Threat: AI-Generated Content in KYC Workflows

### Scale of the Problem (2024–2025)

| Metric | Figure |
|---|---|
| Deepfake fraud attempts, US (Q1 2025) | **Up 1,100%** YoY |
| Synthetic-ID document fraud (Q1 2025) | **Up 300%** YoY |
| Deepfake files in circulation | ~500K in 2023 → **8 million in 2025** |
| Deepfake fraud losses, H1 2025 | **$410M** (more than all of 2024) |
| Cumulative deepfake losses since 2019 | Approaching **$900M** |
| Average loss per financial sector company | **$600,000+** |
| Financial companies losing $1M+ to deepfakes | **23%** |
| Banks experiencing fraud increase in 2024 | **50%** |
| Synthetic identities undetected at onboarding | **95%** |
| Global AML/KYC penalties in 2024 | **$4.5 billion** |
| Deloitte projected US AI fraud losses by 2027 | **$40 billion** |

### Primary Attack Vectors

1. **Synthetic Identity Fraud at Onboarding**
   - GenAI creates realistic fake or altered government IDs, utility bills, and bank statements
   - LLMs fabricate complete personal histories — employment, addresses, financial behaviour
   - Fraudsters bypass liveness checks via third-party webcam plugins or faked "technical glitches"

2. **Deepfake Video Calls**
   - **February 2024, Hong Kong (Arup)**: An employee was directed to transfer **HK$200M (~$25.6M USD)** after a multi-participant video call where every "executive" was a real-time deepfake. All 15 transactions were authorised before the fraud was discovered.

3. **AI-Cloned Voice Fraud at Call Centres**
   - Attackers impersonate customers with voice-cloned audio to trigger account resets or wire transfers

4. **AI-Generated Document Submissions in KYC**
   - Entire document packages — including IDs, proof of address, and corporate records — fabricated with generative AI, passing visual inspection and many automated checks

### Human Detection Failure
> Only **0.1% of people** asked to identify deepfakes correctly identified all deepfakes and real stimuli — making human review effectively useless as a standalone defence.

---

## 8. Regulatory Imperatives

### FinCEN Deepfake Alert (November 13, 2024)
The US Financial Crimes Enforcement Network issued formal alert **FIN-2024-DEEPFAKEFRAUD**, requiring financial institutions to:
- Identify and guard against fraud using GenAI-created deepfake media
- Watch for red flags: deepfake-flagged photos/videos, AI-generated text in customer profiles, geographic/device inconsistencies
- File SARs referencing `FIN-2024-DEEPFAKEFRAUD` in field 2 when applicable

### FATF Guidance
- Issued **explicit guidance on AI-manipulated identities**
- Clarified that **name-matching alone is insufficient** for identity verification
- Revised Travel Rule (Recommendation 16) demanding complete, validated payment chain data

### Global Regulatory Summary

| Regulatory Body | Key 2024–2025 Action |
|---|---|
| **FinCEN (US)** | FIN-2024-DEEPFAKEFRAUD alert; Beneficial Ownership Rule (Jan 2024) |
| **FATF** | AI/deepfake identity guidance; Travel Rule revision |
| **EU** | EU AI Act (penalties up to €35M or 7% global turnover); AMLA launch |
| **FCA (UK)** | £176M in fines in 2024 (3× YoY); "failure to prevent fraud" law |
| **NYDFS** | Deepfake detection required in baseline cyber programmes |
| **MAS (Singapore)** | Best practices for deepfake mitigation published Sept 2025 |

---

## 9. The Industry Response: What Leading Institutions Are Doing

- **Perpetual KYC (pKYC)**: Continuous automated monitoring replacing static one-time checks — triggers alerts on sudden changes in risk profile, cross-border transaction spikes, or ownership changes
- **Agentic AI KYC Factories**: One global bank deployed a 10-agent-squad AI architecture covering the full KYC workflow from initial trigger to final memo
- **Liveness Detection**: Multi-frame biometric analysis to distinguish live persons from replayed or generated video
- **Document Forensics**: Pixel-level analysis of submitted documents to detect generation artefacts, inconsistent fonts, metadata anomalies, and compression signatures
- **Multimodal Fusion**: Combining image, audio, text, and behavioural signals for ensemble fraud scoring

> Banks assign **10–15% of all full-time staff** to KYC/AML, yet financial institutions detect only **~2% of global financial crime flows** (Interpol). The imperative for AI-augmented detection is clear.

---

## 10. Citibank's Specific Vulnerabilities & Opportunity

### Known Gap (2024)
The New York Attorney General **sued Citibank in 2024** for failing to:
- Implement strong enough protections against account takeovers
- Flag suspicious signals (unrecognised devices, new locations, bulk transfers)
- Reimburse victims of electronic fraud

This underscores that **even the most technologically advanced banks have material gaps** in their fraud defences — specifically around detecting AI-generated or synthetic content submitted during client intake.

### The Opportunity
Citi's own strategic priorities — Google Cloud AI partnership, Citi Stylus document intelligence, AI-powered AML detection — create a **natural integration surface** for an advanced synthetic media detection layer within the CitiDirect KYC onboarding workflow.

---

## Sources

- [Citi Digital Onboarding](https://www.citibank.com/tts/solutions/digital-channels-data/digital-onboarding/)
- [Citi KYC — Digital Account Guide](https://www.citibank.com/tts/sa/digital-account-guide/account-opening/know-your-customer.html)
- [CitiDirect® Platform Enhancements 2025](https://www.citigroup.com/global/news/press-release/2025/citi-global-roll-out-enhancements-citidirect-commercial-banking-platform)
- [Citi Adopts Fenergo Platform (2025)](https://www.citigroup.com/global/news/press-release/2025/citi-adopts-fenergo-platform-to-digitize-select-transfer-agency-services-for-funds-in-europe)
- [Citi & Google Cloud Strategic Agreement](https://www.citigroup.com/global/news/press-release/2024/citi-and-google-cloud-announce-strategic-agreement)
- [Citi Gen AI Summit 2025 Takeaways](https://www.citi.com/ventures/perspectives/pressrelease/evolution-of-gen-ai-at-citi.html)
- [FinCEN Deepfake Alert FIN-2024-DEEPFAKEFRAUD](https://www.fincen.gov/news/news-releases/fincen-issues-alert-fraud-schemes-involving-deepfake-media-targeting-financial)
- [McKinsey: Agentic AI in Banking KYC/AML](https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/how-agentic-ai-can-change-the-way-banks-fight-financial-crime)
- [Veriff: Deepfakes in Financial Services 2025](https://www.veriff.com/identity-verification/the-growing-threat-of-deepfakes-in-financial-services-and-why-a-trust-infrastructure-is-the-future)
- [DuckDuckGoose: $193M Deepfake Question](https://www.duckduckgoose.ai/blog/deepfakes-in-financial-services-2025)
- [Themis: Banks Fear Deepfake Spikes 2025](https://www.bottomline.com/resources/blog/themis-study-banks-fear-deepfake-and-synthetic-identity-spikes-2025)
- [AI Tools & Synthetic IDs Fracturing KYC (BankInfoSecurity)](https://www.bankinfosecurity.com/ai-tools-synthetic-ids-are-fracturing-kyc-programs-a-30401)
- [NY AG Sues Citibank for Fraud Failures (2024)](https://ag.ny.gov/press-release/2024/attorney-general-james-sues-citibank-failing-protect-and-reimburse-victims)
- [Citi AML Programme](https://www.citigroup.com/global/investors/corporate-governance/anti-money-laundering)
