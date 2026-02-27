import streamlit as st
import pandas as pd
import os

from processor import load_and_validate, calculate_kpis
from analyzer import full_analysis
from suggester import generate_suggestions
from ai_suggester import get_ai_suggestions
from visualizer import (
    plot_bottleneck_bar,
    plot_heatmap,
    plot_cycle_time_distribution,
    plot_resource_workload,
)
from reporter import export_summary_csv

st.set_page_config(
    page_title="Process Bottleneck Analyzer — AI Powered",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;700&display=swap');
:root {
    --bg: #0d0d1a; --surface: #13132a; --surface2: #1a1a35;
    --accent: #e94560; --accent2: #f5a623; --blue: #4a90e2;
    --green: #2ecc71; --purple: #a855f7; --text: #e8e8f0;
    --muted: #7878a0; --border: #2a2a4a;
}
html, body, .stApp { background-color: var(--bg) !important; font-family: 'DM Sans', sans-serif; color: var(--text); }
section[data-testid="stSidebar"] { background-color: var(--surface) !important; border-right: 1px solid var(--border); }
section[data-testid="stSidebar"] * { color: var(--text) !important; }
h1,h2,h3,h4 { font-family: 'Space Mono', monospace !important; }
h1 { color: var(--accent) !important; }
h3 { color: var(--accent2) !important; font-size: 1rem !important; }
.kpi-card { background: var(--surface2); border: 1px solid var(--border); border-top: 3px solid var(--accent); border-radius: 10px; padding: 18px 20px; text-align: center; }
.kpi-number { font-family: 'Space Mono', monospace; font-size: 2rem; font-weight: 700; color: var(--accent); }
.kpi-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
.badge-critical { background:#e94560; color:white; border-radius:4px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
.badge-high     { background:#f5a623; color:#1a1a2e; border-radius:4px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
.badge-medium   { background:#4a90e2; color:white; border-radius:4px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
.badge-low      { background:#2ecc71; color:#1a1a2e; border-radius:4px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
.badge-quickwin { background:#a855f7; color:white; border-radius:4px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
.badge-strategic{ background:#0f3460; color:white; border-radius:4px; padding:1px 7px; font-size:0.72rem; font-weight:700; border:1px solid #4a90e2; }
.scard { background:var(--surface2); border-left:4px solid var(--accent); border-radius:8px; padding:14px 18px; margin-bottom:12px; }
.scard.high    { border-left-color:var(--accent2); }
.scard.medium  { border-left-color:var(--blue); }
.scard.low     { border-left-color:var(--green); }
.scard.ai      { border-left-color:var(--purple); }
.stitle  { font-weight:700; color:var(--text); font-size:0.92rem; margin-bottom:4px; }
.sissue  { color:var(--muted); font-size:0.82rem; margin-bottom:6px; }
.stext   { color:var(--text); font-size:0.88rem; line-height:1.5; }
.simpact { color:#2ecc71; font-size:0.8rem; margin-top:6px; }
.lean-tag { display:inline-block; background:#0f3460; color:#4a90e2; border-radius:3px; padding:1px 7px; font-size:0.73rem; margin-top:5px; font-family:'Space Mono',monospace; }
.ai-badge { display:inline-block; background:linear-gradient(135deg,#a855f7,#4a90e2); color:white; border-radius:5px; padding:3px 10px; font-size:0.75rem; font-weight:700; font-family:'Space Mono',monospace; letter-spacing:1px; }
.exec-box { background:linear-gradient(135deg,#1a1a35,#0f1a35); border:1px solid #a855f730; border-left:4px solid #a855f7; border-radius:10px; padding:20px 24px; margin-bottom:20px; }
.exec-box p { color:var(--text); font-size:0.95rem; line-height:1.7; margin:0; }
[data-testid="stFileUploader"] { background:var(--surface) !important; border:2px dashed var(--border) !important; border-radius:10px !important; }
.stTabs [data-baseweb="tab-list"] { background:var(--surface) !important; }
.stTabs [data-baseweb="tab"] { background:var(--surface2) !important; color:var(--muted) !important; border-radius:6px 6px 0 0 !important; font-family:'Space Mono',monospace !important; font-size:0.82rem !important; }
.stTabs [aria-selected="true"] { background:var(--accent) !important; color:white !important; }
.stDownloadButton button { background:var(--accent) !important; color:white !important; border:none !important; border-radius:6px !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Process Bottleneck\n### Analyzer")
    st.markdown("<span class='ai-badge'>✦ AI POWERED</span>", unsafe_allow_html=True)
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Upload CSV / Excel", type=["csv","xlsx","xls"])
    st.markdown("---")
    use_sample = st.button("▶ Use Sample Dataset", use_container_width=True)
    st.markdown("---")
    st.caption("v2.0 · AI-Powered · Process Excellence")

# ── Load Data ────────────────────────────────────────────────────────────────
df = None
source_label = ""

if use_sample:
    sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "sample_log.csv")
    df = load_and_validate(sample_path)
    source_label = "Sample Dataset (Order Processing)"
    st.sidebar.success("✅ Sample data loaded!")
elif uploaded_file is not None:
    try:
        df = load_and_validate(uploaded_file)
        source_label = uploaded_file.name
        st.sidebar.success(f"✅ Loaded: {uploaded_file.name}")
    except ValueError as e:
        st.sidebar.error(str(e))

# ── Landing Page ─────────────────────────────────────────────────────────────
if df is None:
    st.markdown("""
    <div style='text-align:center;padding:60px 20px;'>
        <h1 style='font-size:2.8rem;margin-bottom:8px;'>⚙ Process Bottleneck Analyzer</h1>
        <div style='margin-bottom:16px;'><span class='ai-badge'>✦ AI POWERED BY CLAUDE</span></div>
        <p style='color:#7878a0;font-size:1.1rem;max-width:560px;margin:0 auto 30px;'>
            Upload a process event log and get intelligent bottleneck detection,
            KPI analysis, and AI-generated improvement suggestions.
        </p>
    </div>
    """, unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    for col,icon,label in zip([c1,c2,c3],["📤","🔍","🤖"],["Upload your CSV event log","Auto KPI & bottleneck analysis","Claude AI suggestions"]):
        col.markdown(f"<div class='kpi-card'><div class='kpi-number'>{icon}</div><div class='kpi-label'>{label}</div></div>", unsafe_allow_html=True)
    st.markdown("<br><p style='text-align:center;color:#7878a0;'>← Click <b>Use Sample Dataset</b> in sidebar to try instantly</p>", unsafe_allow_html=True)
    st.stop()

# ── Analysis ─────────────────────────────────────────────────────────────────
with st.spinner("🔍 Running analysis..."):
    kpi_results    = calculate_kpis(df)
    findings       = full_analysis(kpi_results)
    rule_suggestions = generate_suggestions(findings, kpi_results['summary'])

summary        = kpi_results['summary']
case_stats     = kpi_results['case_stats']
activity_stats = kpi_results['activity_stats']
df_waiting     = kpi_results['df_with_waiting']

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# ⚙ Process Bottleneck Analyzer")
st.markdown(f"<p style='color:#7878a0;font-size:0.9rem;margin-top:-10px;'>📁 {source_label} &nbsp;|&nbsp; {summary['total_cases']} cases &nbsp;|&nbsp; {summary['unique_activities']} activities</p>", unsafe_allow_html=True)
st.markdown("---")

# ── KPI Cards ────────────────────────────────────────────────────────────────
st.markdown("### 📊 Key Performance Indicators")
k1,k2,k3,k4,k5,k6 = st.columns(6)
def kpi_card(col, number, label):
    col.markdown(f"<div class='kpi-card'><div class='kpi-number'>{number}</div><div class='kpi-label'>{label}</div></div>", unsafe_allow_html=True)

kpi_card(k1, summary['total_cases'],               "Total Cases")
kpi_card(k2, f"{summary['avg_cycle_time_hrs']}h",  "Avg Cycle Time")
kpi_card(k3, f"{summary['max_cycle_time_hrs']}h",  "Max Cycle Time")
kpi_card(k4, f"{summary['min_cycle_time_hrs']}h",  "Min Cycle Time")
kpi_card(k5, f"{summary['avg_waiting_time_hrs']}h","Avg Waiting")
kpi_card(k6, summary['unique_activities'],          "Process Steps")
st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
    "🔴 Bottlenecks","🔥 Heatmap","📈 Charts","🤖 AI Suggestions","⚙️ Rule Suggestions","📋 Raw Data"
])

# Tab 1 — Bottlenecks
with tab1:
    st.markdown("### 🔴 Top Bottleneck Activities")
    for _, row in findings['bottlenecks'].iterrows():
        sev = row.get('severity','Low').lower()
        st.markdown(f"""
        <div class='scard {"" if sev=="critical" else sev}'>
            <div class='stitle'>#{int(row.get('rank',0))} &nbsp; {row['activity']} &nbsp; <span class='badge-{sev}'>{row.get('severity','')}</span></div>
            <div class='sissue'>Avg Wait: <b>{row['avg_waiting_hrs']:.2f}h</b> &nbsp;|&nbsp; Max: <b>{row['max_waiting_hrs']:.2f}h</b> &nbsp;|&nbsp; Std Dev: <b>{row['std_waiting_hrs']:.2f}h</b> &nbsp;|&nbsp; Freq: <b>{int(row['frequency'])}</b></div>
        </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📊 All Activities — Waiting Time")
    st.image(plot_bottleneck_bar(activity_stats), use_container_width=True)
    if not findings['inconsistent_steps'].empty:
        st.markdown("### ⚠️ Inconsistent Steps")
        st.dataframe(findings['inconsistent_steps'][['activity','avg_waiting_hrs','std_waiting_hrs','max_waiting_hrs']].round(2), use_container_width=True)
    if not findings['single_resource_risk'].empty:
        st.markdown("### 🔺 Single Resource Risk")
        st.dataframe(findings['single_resource_risk'], use_container_width=True)

# Tab 2 — Heatmap
with tab2:
    st.markdown("### 🔥 Delay Heatmap")
    st.image(plot_heatmap(df_waiting), use_container_width=True)

# Tab 3 — Charts
with tab3:
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("### 📊 Cycle Time Distribution")
        st.image(plot_cycle_time_distribution(case_stats), use_container_width=True)
    with c2:
        st.markdown("### 👤 Resource Workload")
        buf = plot_resource_workload(df_waiting)
        if buf:
            st.image(buf, use_container_width=True)
        else:
            st.info("No resource column found.")
    st.markdown("---")
    st.markdown("### 📋 Case-Level Summary")
    d = case_stats.copy().reset_index()
    d['cycle_time_hrs'] = d['cycle_time_hrs'].round(2)
    st.dataframe(d, use_container_width=True)

# Tab 4 — AI Suggestions
with tab4:
    st.markdown("### 🤖 AI-Powered Suggestions")
    st.markdown("<span class='ai-badge'>✦ POWERED BY CLAUDE AI</span>", unsafe_allow_html=True)
    st.markdown("")

    if st.button("✦ Generate AI Suggestions", use_container_width=False):
        with st.spinner("🤖 Claude AI is analyzing your process..."):
            try:
                ai_result = get_ai_suggestions(kpi_results, findings)
                st.session_state['ai_result'] = ai_result
                st.success("✅ AI analysis complete!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    if 'ai_result' in st.session_state:
        ai_result = st.session_state['ai_result']

        if 'executive_summary' in ai_result:
            st.markdown(f"""
            <div class='exec-box'>
                <div style='font-family:Space Mono,monospace;color:#a855f7;font-size:0.78rem;letter-spacing:2px;margin-bottom:10px;'>✦ EXECUTIVE SUMMARY</div>
                <p>{ai_result['executive_summary']}</p>
            </div>""", unsafe_allow_html=True)

        sev_order = {'Critical':0,'High':1,'Medium':2,'Low':3}
        for s in sorted(ai_result.get('suggestions',[]), key=lambda x: sev_order.get(x.get('severity','Low'),4)):
            sev    = s.get('severity','Low')
            stype  = s.get('type','')
            lean   = s.get('lean_principle','')
            impact = s.get('expected_impact','')
            type_badge = ""
            if stype == "Quick Win":
                type_badge = "<span class='badge-quickwin'>⚡ Quick Win</span>"
            elif stype == "Strategic":
                type_badge = "<span class='badge-strategic'>🎯 Strategic</span>"
            st.markdown(f"""
            <div class='scard ai'>
                <div class='stitle'>{s.get('activity','')} &nbsp; <span class='badge-{sev.lower()}'>{sev}</span> &nbsp; {type_badge}</div>
                <div class='sissue'>{s.get('issue','')}</div>
                <div class='stext'>{s.get('suggestion','')}</div>
                {"<div class='simpact'>💚 " + impact + "</div>" if impact else ""}
                {"<div><span class='lean-tag'>📐 " + lean + "</span></div>" if lean else ""}
            </div>""", unsafe_allow_html=True)

# Tab 5 — Rule Suggestions
with tab5:
    st.markdown("### ⚙️ Rule-Based Suggestions")
    st.caption("Fixed logic rules — shown for comparison with AI suggestions above.")
    sev_order = {'Critical':0,'High':1,'Medium':2,'Low':3}
    for s in sorted(rule_suggestions, key=lambda x: sev_order.get(x.get('severity','Low'),4)):
        sev_l = s['severity'].lower()
        st.markdown(f"""
        <div class='scard {"" if sev_l=="critical" else sev_l}'>
            <div class='stitle'>{s['activity']} — {s['type']}</div>
            <div class='sissue'>{s['issue']}</div>
            <div class='stext'>{s['suggestion']}</div>
        </div>""", unsafe_allow_html=True)

# Tab 6 — Raw Data
with tab6:
    st.markdown("### 📋 Raw Event Log")
    st.dataframe(df, use_container_width=True, height=400)
    st.markdown("### 📊 Activity Statistics")
    st.dataframe(activity_stats.round(2), use_container_width=True)

# ── Export ───────────────────────────────────────────────────────────────────
st.markdown("---")
csv_data = export_summary_csv(kpi_results, findings, rule_suggestions)
st.download_button("⬇ Download Full Report (CSV)", data=csv_data, file_name="bottleneck_report.csv", mime="text/csv")
