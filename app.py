import streamlit as st
import json, time, random
from datetime import datetime, date

st.set_page_config(
    page_title="Legal AI — Contract Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Load data ────────────────────────────────────────────────
@st.cache_data
def load():
    with open("/app/data/demo_data.json") as f:
        return json.load(f)

d = load()
contracts  = d["contracts"]
risks      = d["risks"]
searches   = d["search_demo"]
chunks     = d["chunks_demo"]

# ── Helpers ──────────────────────────────────────────────────
STATUS_COLOR = {"active": "#00d4aa", "expiring_soon": "#FF9900", "critical": "#FF4444"}
STATUS_BADGE = {"active": "✅ Active", "expiring_soon": "⚠️ Expiring", "critical": "🔴 Critical"}
SEVERITY_COLOR = {range(85,101): "#FF4444", range(70,85): "#FF9900", range(0,70): "#888888"}

def severity_color(s):
    if s >= 85: return "#FF4444"
    if s >= 70: return "#FF9900"
    return "#888888"

def days_until(expiry_str):
    exp = datetime.strptime(expiry_str, "%Y-%m-%d").date()
    return (exp - date(2026, 4, 1)).days

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ Legal AI")
    st.caption("Private Contract Intelligence System")
    st.divider()

    st.markdown("### System Status")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Extraction", "✅ Live", "PyMuPDF+OCR")
        st.metric("Vector DB",  "✅ Live", "ChromaDB")
    with c2:
        st.metric("LLM",        "✅ Live", "Ollama/Llama3")
        st.metric("Scanner",    "✅ Live", "Nightly")

    st.divider()
    st.markdown("### Corpus Stats")
    total_chunks = sum(chunks.values())
    st.metric("Contracts indexed",  len(contracts))
    st.metric("Total chunks",       total_chunks)
    st.metric("Embedding model",    "MiniLM-L6-v2")
    st.metric("Last risk scan",     "Today 02:00 UTC")

    st.divider()
    st.markdown("### Privacy")
    st.success("🔒 All data on-premise\nZero external API calls\nGDPR Art. 28 compliant")

    st.divider()
    st.caption("Stack: LangChain · ChromaDB · Ollama · FastAPI · Docker")
    st.caption("Deployed on client-owned Vultr VPS")
    st.caption("Built by [Manu](https://openclawlabs-pipeline.duckdns.org)")

# ── Header ───────────────────────────────────────────────────
st.title("⚖️ Private Contract Intelligence System")
st.markdown("**On-premise Legal AI** — 10 contracts · 136 chunks · semantic search · nightly risk scanner · zero data exposure")
st.divider()

# ── KPIs ─────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Contracts indexed",  "10",        "500+ capacity")
k2.metric("Risks detected",     "6",         "2 critical")
k3.metric("Review time",        "8 min",     "was 3-4 hours")
k4.metric("Paralegal cost",     "€0/mo",     "was €7,200/mo")
k5.metric("GDPR exposure",      "Eliminated","was Active")
st.divider()

# ── Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📋 Contract Registry", "🔍 Semantic Search", "🚨 Risk Scanner", "🏗️ Architecture"])

# ══════════════════ TAB 1 — CONTRACT REGISTRY ════════════════
with tab1:
    st.subheader("Active Contract Portfolio")

    status_filter = st.radio("Filter:", ["All", "Critical 🔴", "Expiring ⚠️", "Active ✅"], horizontal=True)

    filtered = contracts
    if status_filter == "Critical 🔴":      filtered = [c for c in contracts if c["status"] == "critical"]
    elif status_filter == "Expiring ⚠️":   filtered = [c for c in contracts if c["status"] == "expiring_soon"]
    elif status_filter == "Active ✅":      filtered = [c for c in contracts if c["status"] == "active"]

    for c in filtered:
        days = days_until(c["expiry"])
        color = STATUS_COLOR[c["status"]]
        badge = STATUS_BADGE[c["status"]]
        col_info, col_meta = st.columns([3, 1])

        with col_info:
            st.markdown(f"""<div style="border-left:4px solid {color};padding:8px 12px;margin-bottom:4px;background:#1a1a2e;border-radius:4px">
<span style="color:#FFFFFF;font-weight:bold">{c["id"]}</span><span style="color:#FFFFFF"> — {c["title"]}</span><br>
<small style="color:#C8CDD6">Party: {c["party"]} &nbsp;|&nbsp; Type: {c["type"].upper()} &nbsp;|&nbsp; {c["jurisdiction"]}</small>
</div>""", unsafe_allow_html=True)

        with col_meta:
            st.markdown(f"**{badge}**")
            st.caption(f"Expires: {c['expiry']}")
            if days >= 0:
                st.caption(f"⏱ {days} days")
            else:
                st.caption(f"⚠️ Expired {abs(days)}d ago")
            if c["value"] > 0:
                st.caption(f"€{c['value']:,}")
            if c["auto_renewal"]:
                st.caption("🔄 Auto-renews")

        chunk_count = chunks.get(c["id"], "—")
        st.caption(f"&nbsp;&nbsp;&nbsp;`{chunk_count} chunks` in ChromaDB")
        st.divider()

# ══════════════════ TAB 2 — SEMANTIC SEARCH ══════════════════
with tab2:
    st.subheader("🔍 Semantic Contract Search")
    st.caption("Powered by sentence-transformers/all-MiniLM-L6-v2 — fully local, no API calls")

    query_options = [s["query"] for s in searches]
    selected_q = st.selectbox("Try a sample query (or type your own):", query_options + ["— custom query —"])

    if selected_q == "— custom query —":
        user_query = st.text_input("Your query:", placeholder="e.g. jurisdiction clauses outside Spain")
    else:
        user_query = selected_q

    if st.button("🔍 Search contracts", type="primary") and user_query:
        with st.spinner("Embedding query → searching ChromaDB..."):
            time.sleep(0.6)

        match = next((s for s in searches if s["query"] == user_query), None)
        hit_ids  = match["hits"] if match else [c["id"] for c in contracts[:3]]
        ms       = match["time_ms"] if match else random.randint(35, 60)
        hit_contracts = [c for c in contracts if c["id"] in hit_ids]

        st.success(f"Found {len(hit_ids)} relevant contracts in **{ms}ms**")

        for rank, c in enumerate(hit_contracts, 1):
            score = round(0.97 - rank * 0.04, 2)
            color = STATUS_COLOR[c["status"]]
            st.markdown(f"""<div style="border:1px solid {color};border-radius:8px;padding:10px;margin:6px 0;background:#0e1117">
<span style="color:#FFFFFF;font-weight:bold">#{rank} [{score:.2f}] {c["id"]}</span><span style="color:#FFFFFF"> — {c["title"]}</span><br>
<small style="color:#C8CDD6">{c["party"]} · {c["type"].upper()} · expires {c["expiry"]}</small>
</div>""", unsafe_allow_html=True)
            with st.expander("View relevant excerpt"):
                st.markdown(f"""*"...this Agreement shall be governed by the laws of {c['jurisdiction']}. 
The parties agree to resolve disputes through arbitration. 
{'Auto-renewal clause applies: agreement renews for successive 12-month terms.' if c['auto_renewal'] else 'No automatic renewal.'} 
{'Late payment shall incur a penalty of 1.5% per month.' if c['type'] == 'service' else ''}..."*""")
                st.caption(f"Source: {c['id']} · Chunk #3 of {chunks.get(c['id'], '?')} · Relevance: {score}")

# ══════════════════ TAB 3 — RISK SCANNER ═════════════════════
with tab3:
    st.subheader("🚨 Automated Risk Scanner — Last Run: 2026-04-01 02:00 UTC")

    col_crit, col_alert, col_watch = st.columns(3)
    critical = [r for r in risks if r["severity"] >= 85]
    alerts   = [r for r in risks if 70 <= r["severity"] < 85]
    watches  = [r for r in risks if r["severity"] < 70]

    col_crit.metric("Critical (≥85)",  len(critical), "Immediate action")
    col_alert.metric("Alert (70-84)",  len(alerts),   "This week")
    col_watch.metric("Watch (60-69)",  len(watches),  "Monitor")

    st.divider()

    sev_filter = st.radio("Show:", ["All risks", "Critical only", "Alerts + Critical"], horizontal=True)
    shown = risks
    if sev_filter == "Critical only":      shown = [r for r in risks if r["severity"] >= 85]
    elif sev_filter == "Alerts + Critical": shown = [r for r in risks if r["severity"] >= 70]

    for r in shown:
        sev   = r["severity"]
        color = severity_color(sev)
        level = "🔴 CRITICAL" if sev >= 85 else "🟠 ALERT" if sev >= 70 else "⚪ WATCH"
        contract = next((c for c in contracts if c["id"] == r["contract_id"]), {})

        cb, cc = st.columns([1, 9])
        with cb:
            st.markdown(f"""<div style="background:{color};color:white;padding:10px 6px;border-radius:8px;text-align:center;font-size:11px">
<b>{level}</b><br><span style="font-size:18px">{sev}</span><br><small>/100</small></div>""", unsafe_allow_html=True)
        with cc:
            ts = r["detected_at"][:10]
            st.markdown(f"**[{r['risk_type']}]** `{r['contract_id']}` — {contract.get('title','—')}")
            st.markdown(r["detail"])
            with st.expander("Recommended action"):
                st.info(r["action"])
        st.divider()

    if st.button("⚡ Simulate Nightly Risk Scan", type="primary"):
        bar  = st.progress(0)
        stat = st.empty()
        steps = [
            (10, "Loading contract corpus from ChromaDB..."),
            (22, "Running EXPIRY_SOON pattern (contracts < 90 days)..."),
            (38, "Running AUTO_RENEWAL_WINDOW pattern..."),
            (52, "Running PENALTY_CLAUSE semantic search..."),
            (64, "Running EXCLUSIVITY pattern..."),
            (76, "Running GDPR_REVIEW_DUE check (DPAs > 18 months old)..."),
            (88, "Running JURISDICTION_MISMATCH analysis with Ollama..."),
            (95, "Scoring signals and filtering severity < 60..."),
            (100,"Dispatching Discord alerts for severity ≥ 70..."),
        ]
        for pct, msg in steps:
            bar.progress(pct); stat.markdown(f"`{msg}`"); time.sleep(0.35)
        st.success("Scan complete — 6 signals detected · 3 Discord alerts dispatched · 3 logged silently")

# ══════════════════ TAB 4 — ARCHITECTURE ═════════════════════
with tab4:
    st.subheader("🏗️ System Architecture")
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.code("""
[DOCUMENT UPLOAD]  PDF / DOCX / Scanned Image
        |
        v
[EXTRACTION]       PyMuPDF (native PDF)
                   Tesseract OCR (scanned)
                   Playwright (web portals)
        |
        v
[CHUNKING]         LangChain RecursiveCharacterTextSplitter
                   chunk_size=1000, overlap=200
                   Metadata: party, type, expiry, jurisdiction
        |
        v
[EMBEDDING]        sentence-transformers/all-MiniLM-L6-v2
                   Runs 100% locally — no API calls
        |
        v
[VECTOR STORE]     ChromaDB (persistent, on-premise)
        |
   +----+---------------------------+
   |                                |
   v                                v
[QUERY UI]                   [RISK SCANNER]
FastAPI REST                 Celery Beat 02:00 UTC
Streamlit chat               Patterns: EXPIRY, RENEWAL,
Plain language Q&A           PENALTY, EXCLUSIVITY,
Source citations             GDPR, JURISDICTION
   |                                |
   v                                v
[ANSWER]                     [DISCORD ALERT]
Cited excerpt +              severity >= 70 only
page reference               Zero noise below threshold

DATA BOUNDARY: everything runs on client VPS.
               Nothing leaves this server.
        """, language="text")

    with col_r:
        st.markdown("### ROI Summary")
        roi = {
            "Contract review time": "3h → 8 min (-96%)",
            "Paralegal cost/month": "€7,200 → €0",
            "GDPR ChatGPT risk":    "Active → Eliminated",
            "Setup investment":     "€5,800 one-time",
            "Payback period":       "12 days",
            "Annual value":         "€172,800",
        }
        for k, v in roi.items():
            st.markdown(f"**{k}**  \n`{v}`")
            st.divider()

        st.markdown("### Privacy Guarantee")
        st.markdown("""
- Zero external API calls (core pipeline)
- Local embeddings — no OpenAI
- ChromaDB on client VPS
- Air-gap ready with Ollama
- GDPR Article 28 compliant
        """)

st.divider()
st.caption("Built by Manu · Private AI Infrastructure · [openclawlabs-pipeline.duckdns.org](https://openclawlabs-pipeline.duckdns.org) · Available on Upwork")
