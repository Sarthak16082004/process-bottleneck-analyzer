import streamlit as st
import pandas as pd
import os

from processor import load_and_validate, calculate_kpis
from analyzer import full_analysis
from suggester import generate_suggestions
from visualizer import (
    plot_bottleneck_bar,
    plot_heatmap,
    plot_cycle_time_distribution,
    plot_resource_workload,
)
from reporter import export_summary_csv

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Process Bottleneck Analyzer",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;700&display=swap');

:root {
    --bg: #0d0d1a;
    --surface: #13132a;
    --surface2: #1a1a35;
    --accent: #e94560;
    --accent2: #f5a623;
    --blue: #4a90e2;
    --green: #2ecc71;
    --text: #e8e8f0;
    --muted: #7878a0;
    --border: #2a2a4a;
}

html, body, .stApp {
    background-color: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Headers */
h1, h2, h3, h4 { font-family: 'Space Mono', monospace !important; }
h1 { color: var(--accent) !important; letter-spacing: -1px; }
h2 { color: var(--text) !important; font-size: 1.1rem !important; }
h3 { color: var(--accent2) !important; font-size: 1rem !important; }

/* KPI Cards */
.kpi-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-top: 3px solid var(--accent);
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
    transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); border-top-color: var(--accent2); }
.kpi-number {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1.1;
}
.kpi-label {
    font-size: 0.75rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

/* Bottleneck badge */
.badge-critical { background: #e94560; color: white; border-radius: 4px; padding: 2px 8px; font-size: 0.72rem; font-weight: 700; }
.badge-high     { background: #f5a623; color: #1a1a2e; border-radius: 4px; padding: 2px 8px; font-size: 0.72rem; font-weight: 700; }
.badge-medium   { background: #4a90e2; color: white; border-radius: 4px; padding: 2px 8px; font-size: 0.72rem; font-weight: 700; }
.badge-low      { background: #2ecc71; color: #1a1a2e; border-radius: 4px; padding: 2px 8px; font-size: 0.72rem; font-weight: 700; }

/* Suggestion cards */
.suggestion-card {
    background: var(--surface2);
    border-left: 4px solid var(--accent);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.suggestion-card.high   { border-left-color: var(--accent2); }
.suggestion-card.medium { border-left-color: var(--blue); }
.suggestion-card.low    { border-left-color: var(--green); }
.suggestion-title { font-weight: 700; color: var(--text); font-size: 0.92rem; margin-bottom: 4px; }
.suggestion-issue { color: var(--muted); font-size: 0.82rem; margin-bottom: 6px; }
.suggestion-text  { color: var(--text); font-size: 0.88rem; line-height: 1.5; }

/* Dataframe */
.stDataFrame { background: var(--surface) !important; }

/* Upload area */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 10px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; gap: 4px; }
.stTabs [data-baseweb="tab"] {
    background: var(--surface2) !important;
    color: var(--muted) !important;
    border-radius: 6px 6px 0 0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.82rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
}

/* Buttons */
.stDownloadButton button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.82rem !important;
    padding: 8px 20px !important;
}
.stDownloadButton button:hover { background: #c73050 !important; }

div[data-testid="metric-container"] {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Process Bottleneck\n### Analyzer")
    st.markdown("---")
    st.markdown("**Upload your event log to begin analysis.**")
    st.markdown("""
    **Required CSV columns:**
    - `case_id` — unique process ID
    - `activity` — step name
    - `timestamp` — date & time
    - `resource` *(optional)*
    """)
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "📂 Upload CSV / Excel",
        type=["csv", "xlsx", "xls"],
        help="Your process event log file"
    )

    st.markdown("---")
    use_sample = st.button("▶ Use Sample Dataset", use_container_width=True)
    st.markdown("---")
    st.caption("Built for Process Excellence Specialist Role · v1.0")


# ─── Load Data ─────────────────────────────────────────────────────────────────
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


# ─── Hero / Landing ────────────────────────────────────────────────────────────
if df is None:
    st.markdown("""
    <div style='text-align:center; padding: 60px 20px;'>
        <h1 style='font-size: 2.8rem; margin-bottom: 8px;'>⚙ Process Bottleneck Analyzer</h1>
        <p style='color: #7878a0; font-size: 1.1rem; max-width: 560px; margin: 0 auto 30px;'>
            Upload a process event log and instantly discover bottlenecks, KPIs, 
            delay heatmaps, and actionable improvement suggestions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='kpi-card'>
            <div class='kpi-number'>📤</div>
            <div class='kpi-label'>1. Upload your CSV log file from the sidebar</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='kpi-card'>
            <div class='kpi-number'>🔍</div>
            <div class='kpi-label'>2. Automatic KPI & bottleneck analysis runs instantly</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='kpi-card'>
            <div class='kpi-number'>💡</div>
            <div class='kpi-label'>3. Get improvement suggestions and download report</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br><p style='text-align:center; color:#7878a0;'>← Or click <b>Use Sample Dataset</b> in the sidebar to try it out immediately</p>", unsafe_allow_html=True)
    st.stop()


# ─── Analysis ──────────────────────────────────────────────────────────────────
with st.spinner("🔍 Running analysis..."):
    kpi_results = calculate_kpis(df)
    findings = full_analysis(kpi_results)
    suggestions = generate_suggestions(findings, kpi_results['summary'])

summary = kpi_results['summary']
case_stats = kpi_results['case_stats']
activity_stats = kpi_results['activity_stats']
df_waiting = kpi_results['df_with_waiting']

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"# ⚙ Process Bottleneck Analyzer")
st.markdown(f"<p style='color:#7878a0; font-size:0.9rem; margin-top:-10px;'>📁 Source: <b>{source_label}</b> &nbsp;|&nbsp; {summary['total_cases']} cases &nbsp;|&nbsp; {summary['unique_activities']} activities &nbsp;|&nbsp; {summary['total_activities_logged']} log entries</p>", unsafe_allow_html=True)
st.markdown("---")

# ─── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown("### 📊 Key Performance Indicators")
k1, k2, k3, k4, k5, k6 = st.columns(6)

def kpi_card(col, number, label):
    col.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-number'>{number}</div>
        <div class='kpi-label'>{label}</div>
    </div>""", unsafe_allow_html=True)

kpi_card(k1, summary['total_cases'], "Total Cases")
kpi_card(k2, f"{summary['avg_cycle_time_hrs']}h", "Avg Cycle Time")
kpi_card(k3, f"{summary['max_cycle_time_hrs']}h", "Max Cycle Time")
kpi_card(k4, f"{summary['min_cycle_time_hrs']}h", "Min Cycle Time")
kpi_card(k5, f"{summary['avg_waiting_time_hrs']}h", "Avg Waiting Time")
kpi_card(k6, summary['unique_activities'], "Process Steps")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔴 Bottlenecks", "🔥 Heatmap", "📈 Charts", "💡 Suggestions", "📋 Raw Data"
])

# ── Tab 1: Bottlenecks ─────────────────────────────────────────────────────────
with tab1:
    st.markdown("### 🔴 Top Bottleneck Activities")

    bottlenecks = findings['bottlenecks']
    if not bottlenecks.empty:
        for _, row in bottlenecks.iterrows():
            sev = row.get('severity', 'Low').lower()
            badge_class = f"badge-{sev}"
            st.markdown(f"""
            <div class='suggestion-card {"" if sev == "critical" else sev}'>
                <div class='suggestion-title'>
                    #{int(row.get('rank',0))} &nbsp; {row['activity']} &nbsp;
                    <span class='{badge_class}'>{row.get('severity','')}</span>
                </div>
                <div class='suggestion-issue'>
                    Avg Wait: <b>{row['avg_waiting_hrs']:.2f} hrs</b> &nbsp;|&nbsp;
                    Max: <b>{row['max_waiting_hrs']:.2f} hrs</b> &nbsp;|&nbsp;
                    Std Dev: <b>{row['std_waiting_hrs']:.2f} hrs</b> &nbsp;|&nbsp;
                    Frequency: <b>{int(row['frequency'])} occurrences</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 All Activities — Waiting Time Ranking")
    buf = plot_bottleneck_bar(activity_stats)
    st.image(buf, use_container_width=True)

    st.markdown("---")
    st.markdown("### ⚠️ Inconsistent Steps (High Variability)")
    inconsistent = findings['inconsistent_steps']
    if inconsistent.empty:
        st.success("✅ No highly inconsistent steps detected.")
    else:
        st.dataframe(
            inconsistent[['activity', 'avg_waiting_hrs', 'std_waiting_hrs', 'max_waiting_hrs']].round(2),
            use_container_width=True
        )

    if not findings['single_resource_risk'].empty:
        st.markdown("---")
        st.markdown("### 🔺 Single Resource Risk (Points of Failure)")
        st.dataframe(findings['single_resource_risk'], use_container_width=True)


# ── Tab 2: Heatmap ─────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🔥 Delay Heatmap — Waiting Time per Case × Activity")
    st.caption("Darker = longer wait. Use this to spot which cases are worst affected at which steps.")
    buf = plot_heatmap(df_waiting)
    st.image(buf, use_container_width=True)


# ── Tab 3: Charts ──────────────────────────────────────────────────────────────
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📊 Cycle Time Distribution")
        buf = plot_cycle_time_distribution(case_stats)
        st.image(buf, use_container_width=True)
    with c2:
        st.markdown("### 👤 Resource Workload")
        buf = plot_resource_workload(df_waiting)
        if buf:
            st.image(buf, use_container_width=True)
        else:
            st.info("No resource column found in your data.")

    st.markdown("---")
    st.markdown("### 📋 Case-Level Summary")
    display_cases = case_stats.copy().reset_index()
    display_cases['cycle_time_hrs'] = display_cases['cycle_time_hrs'].round(2)
    st.dataframe(display_cases, use_container_width=True)


# ── Tab 4: Suggestions ─────────────────────────────────────────────────────────
with tab4:
    st.markdown("### 💡 Improvement Suggestions")
    st.caption("Based on bottleneck analysis, inconsistency detection, and resource risk assessment.")

    sev_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    suggestions_sorted = sorted(suggestions, key=lambda x: sev_order.get(x['severity'], 4))

    for s in suggestions_sorted:
        sev_lower = s['severity'].lower()
        card_class = 'suggestion-card' if sev_lower == 'critical' else f'suggestion-card {sev_lower}'
        st.markdown(f"""
        <div class='{card_class}'>
            <div class='suggestion-title'>{s['activity']} — {s['type']}</div>
            <div class='suggestion-issue'>{s['issue']}</div>
            <div class='suggestion-text'>{s['suggestion']}</div>
        </div>
        """, unsafe_allow_html=True)


# ── Tab 5: Raw Data ────────────────────────────────────────────────────────────
with tab5:
    st.markdown("### 📋 Raw Event Log")
    st.dataframe(df, use_container_width=True, height=400)
    st.markdown("### 📊 Activity Statistics Table")
    st.dataframe(activity_stats.round(2), use_container_width=True)


# ─── Export ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📥 Export Report")
csv_data = export_summary_csv(kpi_results, findings, suggestions)
st.download_button(
    label="⬇ Download Full Analysis Report (CSV)",
    data=csv_data,
    file_name="bottleneck_analysis_report.csv",
    mime="text/csv",
    use_container_width=False
)
