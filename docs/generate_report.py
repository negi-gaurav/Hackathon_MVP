"""Generate Citibank KYC Research Word Document."""
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

# ── Citibank brand colours ──────────────────────────────────────────────────
CITI_NAVY   = RGBColor(0x00, 0x22, 0x66)   # #002266
CITI_BLUE   = RGBColor(0x00, 0x66, 0xCC)   # #0066CC
CITI_RED    = RGBColor(0xCC, 0x00, 0x00)   # #CC0000
DARK_GREY   = RGBColor(0x33, 0x33, 0x33)
MID_GREY    = RGBColor(0x66, 0x66, 0x66)
LIGHT_BLUE  = RGBColor(0xE5, 0xF2, 0xFF)   # table header fill
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)


# ── Helpers ──────────────────────────────────────────────────────────────────
def set_cell_bg(cell, rgb_hex: str):
    """Set cell background colour via XML."""
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  rgb_hex)
    tcPr.append(shd)


def set_cell_border(cell, **kwargs):
    """Add borders to a table cell (top/bottom/left/right)."""
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        tag = OxmlElement(f"w:{side}")
        tag.set(qn("w:val"),   kwargs.get("val",   "single"))
        tag.set(qn("w:sz"),    kwargs.get("sz",    "4"))
        tag.set(qn("w:space"), "0")
        tag.set(qn("w:color"), kwargs.get("color", "002266"))
        tcBorders.append(tag)
    tcPr.append(tcBorders)


def add_horizontal_rule(doc, color_hex="002266"):
    """Add a coloured horizontal line paragraph."""
    p   = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pb  = OxmlElement("w:pBdr")
    bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"),   "single")
    bot.set(qn("w:sz"),    "6")
    bot.set(qn("w:space"), "1")
    bot.set(qn("w:color"), color_hex)
    pb.append(bot)
    pPr.append(pb)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(4)
    return p


def heading(doc, text, level=1, colour=CITI_NAVY):
    """Add a styled heading."""
    p    = doc.add_paragraph()
    run  = p.add_run(text)
    size = {1: 18, 2: 14, 3: 12}.get(level, 11)
    run.font.size  = Pt(size)
    run.font.color.rgb = colour
    run.font.bold  = True
    run.font.name  = "Calibri"
    p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
    p.paragraph_format.space_after  = Pt(4)
    return p


def body(doc, text, bold=False, italic=False, colour=DARK_GREY, size=10.5):
    """Add a normal body paragraph."""
    p   = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size      = Pt(size)
    run.font.color.rgb = colour
    run.font.bold      = bold
    run.font.italic    = italic
    run.font.name      = "Calibri"
    p.paragraph_format.space_after = Pt(4)
    return p


def bullet(doc, text, level=0, bold_prefix=None):
    """Add a bullet-point paragraph, with optional bold prefix text."""
    style = "List Bullet" if level == 0 else "List Bullet 2"
    p     = doc.add_paragraph(style=style)
    if bold_prefix:
        r = p.add_run(bold_prefix)
        r.font.bold      = True
        r.font.name      = "Calibri"
        r.font.size      = Pt(10.5)
        r.font.color.rgb = DARK_GREY
    run = p.add_run(text)
    run.font.name      = "Calibri"
    run.font.size      = Pt(10.5)
    run.font.color.rgb = DARK_GREY
    p.paragraph_format.space_after = Pt(2)
    return p


def stat_box(doc, stats: list[tuple[str, str]]):
    """
    Render a row of key stats as a borderless table with shaded cells.
    stats: list of (value, label) tuples.
    """
    cols = len(stats)
    tbl  = doc.add_table(rows=2, cols=cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style     = "Table Grid"

    for i, (value, label) in enumerate(stats):
        # value row
        vc   = tbl.rows[0].cells[i]
        set_cell_bg(vc, "002266")
        vr   = vc.paragraphs[0].add_run(value)
        vr.font.bold      = True
        vr.font.size      = Pt(16)
        vr.font.color.rgb = WHITE
        vr.font.name      = "Calibri"
        vc.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        # label row
        lc   = tbl.rows[1].cells[i]
        set_cell_bg(lc, "E5F2FF")
        lr   = lc.paragraphs[0].add_run(label)
        lr.font.size      = Pt(8.5)
        lr.font.color.rgb = CITI_NAVY
        lr.font.name      = "Calibri"
        lc.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()  # spacer


def styled_table(doc, headers: list[str], rows: list[list[str]]):
    """Render a styled table with Citibank navy header row."""
    col_count = len(headers)
    tbl = doc.add_table(rows=1 + len(rows), cols=col_count)
    tbl.style     = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT

    # Header row
    hdr_cells = tbl.rows[0].cells
    for i, h in enumerate(headers):
        set_cell_bg(hdr_cells[i], "002266")
        run = hdr_cells[i].paragraphs[0].add_run(h)
        run.font.bold      = True
        run.font.color.rgb = WHITE
        run.font.size      = Pt(10)
        run.font.name      = "Calibri"
        hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Data rows
    for ri, row_data in enumerate(rows):
        cells = tbl.rows[ri + 1].cells
        bg    = "F0F7FF" if ri % 2 == 0 else "FFFFFF"
        for ci, val in enumerate(row_data):
            set_cell_bg(cells[ci], bg)
            run = cells[ci].paragraphs[0].add_run(val)
            run.font.size      = Pt(9.5)
            run.font.name      = "Calibri"
            run.font.color.rgb = DARK_GREY

    doc.add_paragraph()  # spacer after table


def callout(doc, text, bg="FFF3CD", border="CC0000"):
    """Render a highlighted callout / info box."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = "Table Grid"
    cell = tbl.rows[0].cells[0]
    set_cell_bg(cell, bg)
    run = cell.paragraphs[0].add_run(text)
    run.font.size      = Pt(10)
    run.font.italic    = True
    run.font.name      = "Calibri"
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    doc.add_paragraph()


# ═══════════════════════════════════════════════════════════════════════════
#  BUILD THE DOCUMENT
# ═══════════════════════════════════════════════════════════════════════════
doc = Document()

# Page margins
for section in doc.sections:
    section.top_margin    = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

# ── COVER ───────────────────────────────────────────────────────────────────
cover = doc.add_paragraph()
cover.paragraph_format.space_before = Pt(20)
cover.paragraph_format.space_after  = Pt(4)
cr = cover.add_run("CITIBANK  KYC  RESEARCH  REPORT")
cr.font.size      = Pt(24)
cr.font.bold      = True
cr.font.color.rgb = CITI_NAVY
cr.font.name      = "Calibri"
cover.alignment   = WD_ALIGN_PARAGRAPH.CENTER

sub = doc.add_paragraph()
sr  = sub.add_run(
    "Digital Onboarding, Document Submission & the Synthetic Media Threat"
)
sr.font.size      = Pt(13)
sr.font.color.rgb = CITI_BLUE
sr.font.name      = "Calibri"
sub.alignment     = WD_ALIGN_PARAGRAPH.CENTER

meta = doc.add_paragraph()
mr   = meta.add_run("Prepared for: Citibank AI Hackathon  |  February 2026")
mr.font.size      = Pt(9)
mr.font.color.rgb = MID_GREY
mr.font.name      = "Calibri"
meta.alignment    = WD_ALIGN_PARAGRAPH.CENTER

add_horizontal_rule(doc)
doc.add_paragraph()

# ── EXECUTIVE SUMMARY ───────────────────────────────────────────────────────
heading(doc, "Executive Summary", 1)
body(doc,
     "Citibank's Know Your Customer (KYC) process has undergone a fundamental digital "
     "transformation over the past three years, anchored by the OneKYC global programme, "
     "the CitiDirect® Commercial Banking platform, and a $30 billion technology investment "
     "spanning 2022–2025. Digital onboarding now covers 90 % of incoming account requests, "
     "e-signatures are accepted in 72 countries, and onboarding turnaround time has been "
     "cut by 41 %.")
body(doc,
     "However, this digital acceleration has coincided with an explosive surge in "
     "AI-generated fraud. Deepfake fraud attempts in the United States rose more than 1,100 % "
     "in Q1 2025 alone, and 95 % of synthetic identities go undetected during the onboarding "
     "process at financial institutions. Regulators have responded forcefully: FinCEN issued "
     "formal alert FIN-2024-DEEPFAKEFRAUD in November 2024, and global AML/KYC penalties "
     "reached $4.5 billion in 2024.")
body(doc,
     "This report synthesises Citi's current KYC digital infrastructure, the document "
     "submission workflow, the emerging threat landscape, the regulatory environment, and "
     "the strategic opportunity to embed AI-powered synthetic media detection directly "
     "into Citi's client intake processes.")
add_horizontal_rule(doc)

# ── KEY STATS SNAPSHOT ───────────────────────────────────────────────────────
heading(doc, "Key Statistics at a Glance", 1)
stat_box(doc, [
    ("41%",   "Reduction in\nonboarding time"),
    ("72",    "Countries with\ne-signature support"),
    ("90%",   "Account requests\nhandled digitally"),
    ("49",    "Countries with\ndigital account opening"),
])
stat_box(doc, [
    ("+1,100%", "US deepfake fraud\nattempts, Q1 2025"),
    ("95%",     "Synthetic IDs\nundetected at onboarding"),
    ("$4.5B",   "Global AML/KYC\npenalties in 2024"),
    ("$40B",    "Projected US AI fraud\nlosses by 2027 (Deloitte)"),
])
add_horizontal_rule(doc)

# ── SECTION 1 ────────────────────────────────────────────────────────────────
heading(doc, "1.  OneKYC Program — Global Unified Framework", 1)
body(doc,
     "Citibank operates a OneKYC Program that unifies its Know Your Customer process "
     "across all geographies under four pillars:")
bullet(doc, "One global policy aligned with the highest regulatory standard Citi has adopted as its baseline", bold_prefix="One Global Policy — ")
bullet(doc, "Applied consistently worldwide, adjusting for local requirements that exceed the US baseline", bold_prefix="One Risk Scoring Model — ")
bullet(doc, "CitiKYC — the single enterprise data repository acting as source of truth for all KYC records", bold_prefix="One Data Repository — ")
bullet(doc, "Spanning more than 100 countries where Citi conducts business", bold_prefix="Unified Governance — ")
doc.add_paragraph()
body(doc,
     "The OneKYC Program exists to prevent the flow of illicit funds through the global "
     "financial system and to ensure that local regulatory requirements — some of which "
     "exceed Citi's US baseline — are consistently met across all jurisdictions.")
add_horizontal_rule(doc)

# ── SECTION 2 ────────────────────────────────────────────────────────────────
heading(doc, "2.  CitiDirect® — Digital Onboarding Platform", 1)
body(doc,
     "CitiDirect® Commercial Banking is Citi's flagship client-facing platform, providing "
     "a 360° consolidated view of the entire banking relationship — Cash, Loans, Trade, FX, "
     "Servicing, and KYC Onboarding — within a single digital interface.")

heading(doc, "2.1  Core Digital Onboarding Capabilities", 2)
styled_table(doc,
    headers=["Feature", "Detail"],
    rows=[
        ["Streamlined Onboarding",    "Fully digitised process with real-time status updates"],
        ["Onboarding Time",           "Cut by 41% since digital rollout"],
        ["Country Coverage",          "Account opening expedited in 49 countries and jurisdictions"],
        ["Digital Request Coverage",  "90% of incoming account requests handled digitally"],
        ["E-Signatures",              "Supported in 72 countries and jurisdictions"],
        ["KYC Renewals",              "'One field, one-time' — pre-filled data, automated notifications"],
        ["Document Submission",       "Single unified checklist: Account Opening + KYC + Product docs"],
        ["Digital Servicing Hub",     "Centralises client queries, updates, and document submissions"],
        ["ERP Integration (Integrator)", "Implementation time reduced from 7 weeks to under 1 day"],
    ]
)

heading(doc, "2.2  Documentation 2.0", 2)
body(doc,
     "As part of the CitiDirect onboarding experience, Citi introduced Documentation 2.0 — "
     "a restructuring of all onboarding documents designed to:")
bullet(doc, "Eliminate local country-specific terms wherever possible")
bullet(doc, "Centralise essential legal terms into a simplified, global structure")
bullet(doc, "Reduce document complexity and client friction during cross-border onboarding")
add_horizontal_rule(doc)

# ── SECTION 3 ────────────────────────────────────────────────────────────────
heading(doc, "3.  AML/KYC Document Submission Requirements", 1)
body(doc,
     "Citi's document requirements vary by jurisdiction and client entity type, but "
     "typically include the following categories:")

heading(doc, "3.1  Corporate Entity Documents", 2)
bullet(doc, "Certificate of Incorporation")
bullet(doc, "Articles of Association / Constitution")
bullet(doc, "Board resolutions authorising account opening")
bullet(doc, "Register of directors and shareholders")

heading(doc, "3.2  Beneficial Ownership", 2)
bullet(doc, "Identification of all beneficial owners above applicable thresholds")
bullet(doc, "Personal identification for directors, shareholders, and account operators")
bullet(doc, "In many jurisdictions: formal identification of persons operating the account")

heading(doc, "3.3  Business Purpose & AML", 2)
bullet(doc, "Documentation explaining nature and purpose of the banking relationship")
bullet(doc, "Source of funds declaration")
bullet(doc, "Anticipated transaction volumes and counterparties")

doc.add_paragraph()
callout(doc,
        "⚠  Critical Compliance Point: Account openings cannot be completed until ALL "
        "AML/KYC requirements are fully satisfied — with no exceptions. This creates a "
        "high-stakes verification chokepoint that is now directly targeted by AI-generated "
        "document fraud.",
        bg="FFE0E0", border="CC0000")

heading(doc, "3.4  SWIFT KYC Registry", 2)
body(doc,
     "Citi is a contributor and active user of the SWIFT KYC Registry — an inter-bank "
     "information-exchange platform enabling financial institutions to share verified KYC "
     "data centrally. This increases transparency and simplifies correspondent banking "
     "relationships by eliminating redundant document requests across institutions.")
add_horizontal_rule(doc)

# ── SECTION 4 ────────────────────────────────────────────────────────────────
heading(doc, "4.  Fenergo Platform — Transfer Agency (2025)", 1)
body(doc,
     "In 2025, Citi's Global Transfer Agency business deployed Fenergo's Client Lifecycle "
     "Management platform for regulated funds across Europe. Key capabilities include:")
bullet(doc, "Customised, policy-driven risk assessment for AML and KYC checks")
bullet(doc, "Automated data validations reducing manual review workload")
bullet(doc, "Real-time reporting via API connectivity")
bullet(doc, "More seamless investor onboarding and ongoing due diligence")
add_horizontal_rule(doc)

# ── SECTION 5 ────────────────────────────────────────────────────────────────
heading(doc, "5.  Citi's AML Control Lifecycle", 1)
body(doc,
     "Citi structures its AML compliance programme across three sequential phases:")

styled_table(doc,
    headers=["Phase", "Key Activities"],
    rows=[
        ["1. Prevention",
         "OneKYC policy enforcement; customer risk scoring; CitiKYC data repository; "
         "Beneficial Ownership Rule compliance; SWIFT KYC Registry participation"],
        ["2. Detection",
         "AI/ML-powered transaction monitoring; anomaly detection; behavioural analytics; "
         "real-time risk scoring in Treasury & Trade Solutions; NLP screening of unstructured data"],
        ["3. Reporting",
         "Suspicious Activity Report (SAR) filing; regulatory reporting; FinCEN/FCA/local "
         "regulator liaison; SAR tagging with alert codes (e.g. FIN-2024-DEEPFAKEFRAUD)"],
    ]
)
add_horizontal_rule(doc)

# ── SECTION 6 ────────────────────────────────────────────────────────────────
heading(doc, "6.  Citibank's AI & Technology Strategy", 1)

heading(doc, "6.1  Scale of Investment", 2)
stat_box(doc, [
    ("$12B",  "Technology investment\nin 2024 alone"),
    ("$30B+", "Total tech investment\nover 3 years"),
    ("$2.4B", "Tech spend in\nQ1 2025"),
    ("2,000+","Legacy apps\ndecommissioned"),
])

heading(doc, "6.2  Google Cloud Strategic Partnership (October 2024)", 2)
body(doc,
     "Citi signed a multi-year strategic agreement with Google Cloud to modernise its "
     "technology infrastructure and accelerate AI capabilities:")
bullet(doc, "Migration of multiple workloads and applications to Google Cloud's secure, scalable infrastructure")
bullet(doc, "High-performance computing enabling millions of financial calculations daily in Citi's Markets business")
bullet(doc, "Co-engineering partnership — not a simple vendor contract — designed to modernise core banking infrastructure")
bullet(doc, "Enhanced AI/ML model deployment for fraud prevention and compliance automation")

heading(doc, "6.3  Internal AI Tool Deployments", 2)
styled_table(doc,
    headers=["Tool", "Purpose"],
    rows=[
        ["Citi Stylus",      "Document intelligence — automated extraction from regulatory and client documents"],
        ["Citi Assist",      "Knowledge management assistant for compliance and operations teams"],
        ["AskWealth",        "Generative AI assistant for wealth advisory teams — market insights and research"],
        ["Advisor Insights", "ML-based markets dashboard for wealth advisors (pilot phase)"],
        ["AI Coding Tools",  "Deployed to 30,000 developers; ~220,000 automated code reviews completed"],
    ]
)
add_horizontal_rule(doc)

# ── SECTION 7 ────────────────────────────────────────────────────────────────
heading(doc, "7.  The Threat: AI-Generated Content in KYC Workflows", 1)
body(doc,
     "The same generative AI tools that power legitimate productivity gains are being "
     "weaponised to create synthetic identities and fraudulent documents at unprecedented "
     "scale — directly targeting the KYC onboarding chokepoint.")

heading(doc, "7.1  Scale of the Problem (2024–2025)", 2)
styled_table(doc,
    headers=["Metric", "Figure", "Source"],
    rows=[
        ["Deepfake fraud attempts, US (Q1 2025)",        "+1,100% YoY",           "FinCEN / Veriff"],
        ["Synthetic-ID document fraud (Q1 2025)",        "+300% YoY",             "BankInfoSecurity"],
        ["Deepfake files in circulation",                "500K (2023) → 8M (2025)","SQ Magazine"],
        ["Deepfake fraud losses, H1 2025",               "$410M",                 "DuckDuckGoose"],
        ["Cumulative deepfake losses since 2019",        "~$900M",                "DuckDuckGoose"],
        ["Average loss per financial sector company",    "$600,000+",             "Regula Survey 2024"],
        ["Financial firms losing $1M+ to deepfakes",    "23%",                   "Regula Survey 2024"],
        ["Banks experiencing increased fraud (2024)",   "50%",                   "Themis Study"],
        ["Synthetic identities undetected at onboarding","95%",                  "Themis Study"],
        ["Global AML/KYC penalties, 2024",              "$4.5 billion",          "Multiple regulators"],
        ["Projected US AI fraud losses by 2027",         "$40 billion",           "Deloitte"],
        ["Deepfake detection market growth (2023–2026)", "3× expansion projected","Industry analysts"],
    ]
)

heading(doc, "7.2  Primary Attack Vectors", 2)

body(doc, "Synthetic Identity Fraud at Onboarding", bold=True)
bullet(doc, "GenAI creates realistic fake or altered government IDs, utility bills, and bank statements")
bullet(doc, "LLMs fabricate complete personal histories — employment records, addresses, financial behaviour — giving synthetic IDs the depth KYC processes expect")
bullet(doc, "Fraudsters bypass liveness checks via third-party webcam plugins or faked 'technical glitches' during video verification")

doc.add_paragraph()
body(doc, "Deepfake Video Call Fraud", bold=True)
bullet(doc,
       "February 2024, Hong Kong (Arup): An employee was directed to transfer HK$200M "
       "(~$25.6M USD) after a multi-participant video call where every 'executive' was "
       "a real-time deepfake. All 15 transactions were authorised before the fraud was discovered.",
       bold_prefix="Case Study — ")

doc.add_paragraph()
body(doc, "AI-Cloned Voice Fraud at Call Centres", bold=True)
bullet(doc, "Attackers impersonate customers using voice-cloned audio to trigger account resets or wire transfers")
bullet(doc, "35% of UK businesses were directly targeted by AI-enabled voice-cloning scams in 2024/25")

doc.add_paragraph()
body(doc, "AI-Generated Document Packages in KYC Submissions", bold=True)
bullet(doc, "Entire document packages — IDs, proof of address, corporate records — fabricated with generative AI, passing visual inspection and many automated checks")
bullet(doc, "LLMs generate consistent synthetic personal histories that align across all submitted documents")

doc.add_paragraph()
callout(doc,
        "\"Only 0.1% of people asked to identify deepfakes correctly identified all "
        "deepfakes and real stimuli.\" Human review is effectively useless as a "
        "standalone defence against modern AI-generated content.",
        bg="E5F2FF", border="0066CC")
add_horizontal_rule(doc)

# ── SECTION 8 ────────────────────────────────────────────────────────────────
heading(doc, "8.  Regulatory Imperatives", 1)

heading(doc, "8.1  FinCEN Deepfake Alert — FIN-2024-DEEPFAKEFRAUD (November 13, 2024)", 2)
body(doc,
     "The US Financial Crimes Enforcement Network issued its landmark formal alert "
     "requiring financial institutions to:")
bullet(doc, "Identify and guard against fraud using GenAI-created deepfake media in client intake")
bullet(doc, "Watch for red flags: deepfake-flagged photos/videos, AI-generated text in customer profiles, geographic/device inconsistencies with submitted documents")
bullet(doc, "File Suspicious Activity Reports referencing FIN-2024-DEEPFAKEFRAUD in SAR field 2")
bullet(doc, "The Treasury Department formally recognised that GenAI tools are being used to create fraudulent identity documents circumventing standard verification")

heading(doc, "8.2  Global Regulatory Summary", 2)
styled_table(doc,
    headers=["Regulatory Body", "Key 2024–2025 Action"],
    rows=[
        ["FinCEN (US)",         "FIN-2024-DEEPFAKEFRAUD alert (Nov 2024); Beneficial Ownership Rule (Jan 2024)"],
        ["FATF",               "Explicit AI/deepfake identity guidance; name-matching alone deemed insufficient; Travel Rule (Rec. 16) revision"],
        ["EU",                 "EU AI Act: penalties up to €35M or 7% of global turnover; AMLA launch; AML Regulation harmonising KYC standards across member states"],
        ["FCA (UK)",           "£176M in fines in 2024 (3× year-on-year); 'failure to prevent fraud' law enacted"],
        ["NYDFS",              "Deepfake detection required as part of baseline cyber programmes"],
        ["MAS (Singapore)",    "Best practices for deepfake mitigation in financial services published Sept 2025"],
        ["OCC (US)",           "Guidelines demanding transparency and explainability in AI-driven KYC decisions"],
    ]
)

heading(doc, "8.3  Enforcement Trend", 2)
body(doc,
     "Global regulators levied approximately 139 financial penalties in H1 2025 alone, "
     "totalling $1.23 billion — a 417% increase vs the same period in 2024. The FCA "
     "levied £176M in fines in all of 2024 (approximately 3× year-on-year). These "
     "figures underscore that the cost of non-compliance now vastly exceeds the cost "
     "of implementing robust AI-detection controls.")

callout(doc,
        "TD Bank case study: Over $670M was laundered through TD Bank accounts — 'not "
        "because controls were absent, but because they were built for a world of forged "
        "documents and stolen IDs, not one of scalable synthetic identities and "
        "deepfaked video verification.'",
        bg="FFE0E0", border="CC0000")
add_horizontal_rule(doc)

# ── SECTION 9 ────────────────────────────────────────────────────────────────
heading(doc, "9.  Industry Response: What Leading Institutions Are Doing", 1)
styled_table(doc,
    headers=["Approach", "Description"],
    rows=[
        ["Perpetual KYC (pKYC)",
         "Continuous automated monitoring replacing static one-time checks. Triggers alerts on "
         "sudden changes in risk profile, cross-border transaction spikes, or ownership changes."],
        ["Agentic AI KYC Factories",
         "One global bank deployed a 10-agent-squad AI architecture covering the full KYC "
         "workflow — from initial trigger to final decision memo — autonomously."],
        ["Liveness Detection",
         "Multi-frame biometric analysis distinguishing live persons from replayed or "
         "AI-generated video during video verification calls."],
        ["Document Forensics",
         "Pixel-level analysis detecting generation artefacts, inconsistent fonts, metadata "
         "anomalies, and compression signatures in submitted documents."],
        ["Multimodal Fusion",
         "Combining image, audio, text, and behavioural signals for ensemble fraud scoring "
         "that is far more robust than any single modality."],
        ["Voice Biometrics",
         "Frequency-domain analysis and micro-pattern detection to identify AI-cloned "
         "voice audio used in call-centre impersonation attacks."],
    ]
)
callout(doc,
        "Banks assign 10–15% of all full-time staff to KYC/AML, yet financial institutions "
        "detect only ~2% of global financial crime flows (Interpol). The imperative for "
        "AI-augmented detection is clear — current investment is not delivering adequate results.",
        bg="E5F2FF", border="002266")
add_horizontal_rule(doc)

# ── SECTION 10 ───────────────────────────────────────────────────────────────
heading(doc, "10.  Citibank's Specific Vulnerabilities & Strategic Opportunity", 1)

heading(doc, "10.1  Known Gap — NY AG Lawsuit (2024)", 2)
body(doc,
     "In 2024, New York Attorney General Letitia James sued Citibank for failing to:")
bullet(doc, "Implement strong enough protections to stop AI-powered account takeovers")
bullet(doc, "Flag suspicious signals: unrecognised devices, new login locations, bulk transfers consolidating funds before large outbound wires")
bullet(doc, "Reimburse victims of electronic fraud, as required under applicable consumer protection laws")
body(doc,
     "This demonstrates that even the most technologically advanced banks have material "
     "gaps in their fraud defences — specifically around detecting AI-generated or synthetic "
     "content submitted during client intake.")

heading(doc, "10.2  Strategic Integration Opportunity", 2)
body(doc,
     "Citi's own strategic priorities create a natural and immediate integration surface "
     "for an advanced synthetic media detection layer:")
bullet(doc, "Google Cloud AI partnership provides scalable inference infrastructure for real-time ML model serving")
bullet(doc, "Citi Stylus (document intelligence) is architecturally adjacent to document forensics — a detection layer can be inserted into the same pipeline")
bullet(doc, "CitiDirect® portal's single document submission checklist is the optimal injection point for automated AI-content screening")
bullet(doc, "OneKYC's centralised CitiKYC repository enables global deployment of detection models with consistent risk scoring")
bullet(doc, "Existing SAR filing workflows can be extended to automatically tag FIN-2024-DEEPFAKEFRAUD cases surfaced by the detection system")
add_horizontal_rule(doc)

# ── SECTION 11 ───────────────────────────────────────────────────────────────
heading(doc, "11.  Proposed Solution: AI-Powered Synthetic Media Detection in KYC", 1)
body(doc,
     "The solution is a multi-modal AI detection layer — TrustGuard — embedded directly "
     "into Citi's CitiDirect® KYC onboarding workflow, screening all submitted content "
     "before it reaches human reviewers.")

styled_table(doc,
    headers=["Detection Modality", "What It Catches", "KYC Application"],
    rows=[
        ["Document Forensics (PDF/Image)",
         "AI-generated IDs, utility bills, bank statements; pixel anomalies, metadata inconsistencies",
         "Screens all uploaded identity and address documents at submission"],
        ["Image / Selfie Analysis",
         "Deepfake faces, AI-generated profile photos, GAN artefacts",
         "Validates selfies and ID photos submitted during onboarding liveness checks"],
        ["Audio Analysis",
         "AI-cloned voice patterns, frequency anomalies, temporal artefacts",
         "Screens voice recordings in call-centre and voice-KYC workflows"],
        ["Text / Profile Analysis",
         "LLM-generated personal histories, synthetic financial narratives",
         "Flags AI-written customer profiles, business descriptions, and supporting narratives"],
        ["Behavioural / Metadata Signals",
         "Device fingerprint inconsistencies, geographic mismatches, session anomalies",
         "Cross-references device and location data with submitted document claims"],
    ]
)

heading(doc, "11.1  Architecture Overview", 2)
bullet(doc, "FastAPI microservice backend — lightweight, containerised (Docker), horizontally scalable on Google Cloud")
bullet(doc, "REST API endpoints per modality: /detect/document, /detect/image, /detect/audio, /detect/text")
bullet(doc, "Ensemble risk scorer combining outputs from all modalities into a single confidence score (0.0–1.0)")
bullet(doc, "Integration via CitiDirect® API gateway — zero disruption to existing client-facing workflow")
bullet(doc, "Explainable AI output: every flag includes the specific artefact or anomaly detected (audit-ready for regulators)")
bullet(doc, "Automatic SAR tagging pipeline for cases exceeding configurable risk thresholds")

heading(doc, "11.2  Build vs Buy Analysis", 2)
styled_table(doc,
    headers=["Dimension", "Build (Custom)", "Buy (Vendor)"],
    rows=[
        ["Cost (Year 1)",           "Lower TCO at scale",         "High licensing fees"],
        ["Data Privacy",            "All data stays on-prem/Citi Cloud", "Data leaves Citi's perimeter"],
        ["Customisation",           "Full control of models and thresholds", "Limited to vendor roadmap"],
        ["Regulatory Explainability", "Full transparency into model decisions", "Black-box risk"],
        ["Integration",             "Native to CitiDirect® architecture", "Requires adapters and middleware"],
        ["Recommendation",          "✓ BUILD on Google Cloud + open-source models", ""],
    ]
)
add_horizontal_rule(doc)

# ── SOURCES ──────────────────────────────────────────────────────────────────
heading(doc, "Sources & References", 1)
sources = [
    ("Citi Digital Onboarding",                  "https://www.citibank.com/tts/solutions/digital-channels-data/digital-onboarding/"),
    ("Citi KYC — Digital Account Guide",          "https://www.citibank.com/tts/sa/digital-account-guide/account-opening/know-your-customer.html"),
    ("CitiDirect® Platform Enhancements 2025",    "https://www.citigroup.com/global/news/press-release/2025/citi-global-roll-out-enhancements-citidirect-commercial-banking-platform"),
    ("Citi Adopts Fenergo Platform (2025)",        "https://www.citigroup.com/global/news/press-release/2025/citi-adopts-fenergo-platform-to-digitize-select-transfer-agency-services-for-funds-in-europe"),
    ("Citi & Google Cloud Strategic Agreement",   "https://www.citigroup.com/global/news/press-release/2024/citi-and-google-cloud-announce-strategic-agreement"),
    ("Citi Gen AI Summit 2025 Takeaways",         "https://www.citi.com/ventures/perspectives/pressrelease/evolution-of-gen-ai-at-citi.html"),
    ("FinCEN FIN-2024-DEEPFAKEFRAUD Alert",       "https://www.fincen.gov/news/news-releases/fincen-issues-alert-fraud-schemes-involving-deepfake-media-targeting-financial"),
    ("McKinsey: Agentic AI in Banking KYC/AML",  "https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/how-agentic-ai-can-change-the-way-banks-fight-financial-crime"),
    ("Veriff: Deepfakes in Financial Services",   "https://www.veriff.com/identity-verification/the-growing-threat-of-deepfakes-in-financial-services-and-why-a-trust-infrastructure-is-the-future"),
    ("DuckDuckGoose: $193M Deepfake Question",    "https://www.duckduckgoose.ai/blog/deepfakes-in-financial-services-2025"),
    ("Themis: Banks Fear Deepfake Spikes 2025",   "https://www.bottomline.com/resources/blog/themis-study-banks-fear-deepfake-and-synthetic-identity-spikes-2025"),
    ("BankInfoSecurity: AI Tools & Synthetic IDs","https://www.bankinfosecurity.com/ai-tools-synthetic-ids-are-fracturing-kyc-programs-a-30401"),
    ("NY AG Sues Citibank (2024)",                "https://ag.ny.gov/press-release/2024/attorney-general-james-sues-citibank-failing-protect-and-reimburse-victims"),
    ("Citi AML Programme",                        "https://www.citigroup.com/global/investors/corporate-governance/anti-money-laundering"),
    ("Regula Survey: Deepfake Impact on IDV",     "https://regulaforensics.com/blog/impact-of-deepfakes-on-idv-regula-survey/"),
    ("SilentEight: JPMorgan, Citi, Wells Fargo AI AML", "https://www.silenteight.com/blog/jpmorgan-citi-and-wells-fargo-are-transforming-aml-thanks-to-ai-tools"),
]
for title, url in sources:
    p = doc.add_paragraph(style="List Bullet")
    run_t = p.add_run(f"{title}: ")
    run_t.font.bold = True
    run_t.font.size = Pt(9)
    run_t.font.name = "Calibri"
    run_u = p.add_run(url)
    run_u.font.size      = Pt(9)
    run_u.font.color.rgb = CITI_BLUE
    run_u.font.name      = "Calibri"

# ── SAVE ─────────────────────────────────────────────────────────────────────
output_path = "/home/user/Hackathon_MVP/docs/Citibank_KYC_Research_Report.docx"
doc.save(output_path)
print(f"Saved: {output_path}")
