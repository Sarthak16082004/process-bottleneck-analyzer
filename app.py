import streamlit as st
import pandas as pd
import os

from processor import load_and_validate, calculate_kpis
from analyzer import full_analysis
from ai_suggester import generate_ai_suggestions, fallback_suggestions
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
    --purple: #9b59b6;
    --text: #e8e8f0;
    --muted: #7878a0;
    --border: #2a2a4a;
}
html, body, .stApp { background-color: var(--bg) !important; font-family: 'DM Sans', sans-serif; color: var(--text); }
section[data-testid="stSidebar"] { background-color: var(--surface) !important; border-right: 1px solid var(--border); }
section[data-testid="stSidebar"] * { color: var(--text) !important; }
h1, h2, h3, h4 { font-family: 'Space Mono', monospace !important; }
h1 { color: var(--accent) !important; letter-spacing: -1px; }
h2 { color: var(--text) !important; font-size: 1.1rem !important; }
h3 { color: var(--accent2) !important; font-size: 1rem !important; }

.kpi-card {
    background: var(--surface2); border: 1px solid var(--border);
    border-top: 3px solid var(--accent); border-radius: 10px;
    padding: 18px 20px; text-align: center; transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); border-top-color: var(--accent2); }
.kpi-number { font-family: 'Space Mono', monospace; font-size: 2rem; font-weight: 700; color: var(--accent); line-height: 1.1; }
.kpi-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

.ai-badge { display: inline-block; background: linear-gradient(135deg, #9b59b6, #4a90e2); color: white; border-radius: 20px; padding: 3px 12px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.5px; margin-left: 8px; }
.rule-badge { display: inline-block; background: #2a2a4a; color: #7878a0; border-radius: 20px; padding: 3px 12px; font-size: 0.72rem; font-weight: 700; margin-left: 8px; }

.ai-panel { background: linear-gradient(135deg, rgba(155,89,182,0.08), rgba(74,144,226,0.08)); border: 1px solid rgba(155,89,182,0.3); border-radius: 12px; padding: 16px 20px; margin-bottom: 16px; }
.ai-panel-header { font-family: 'Space Mono', monospace; font-size: 0.78rem; color: #9b59b6; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }

.badge-critical { background: #e94560; color: white; border-radius: 4px; padding: 2px 8px; font-size: 0.72rem; font-weight: 700; }
.badge-high     { background: #f5a623; color: #1a1a2e; border-radius: 4px; padding: 2px 8px; font-size: 0.72rem; font-weight: 700; }
.badge-medium   { background: #4a90e2; color: white; border-radius: 4px; padding: 2px 8px; font-size: 0.72rem; font-weight: 700; }
.badge-low      { background: #2ecc71; color: #1a1a2e; border-radius: 4px; padding: 2px 8px; font-size: 0.72rem; font-weight: 700; }

.suggestion-card { background: var(--surface2); border-left: 4px solid var(--accent); border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; }
.suggestion-card.high     { border-left-color: var(--accent2); }
.suggestion-card.medium   { border-left-color: var(--blue); }
.suggestion-card.low      { border-left-color: var(--green); }
.suggestion-card.quickwin { border-left-color: var(--green); border-style: dashed; }
.suggestion-card.strategic{ border-left-color: var(--purple); }
.suggestion-title { font-weight: 700; color: var(--text); font-size: 0.92rem; margin-bottom: 4px; }
.suggestion-issue { color: var(--muted); font-size: 0.82rem; margin-bottom: 6px; }
.suggestion-text  { color: var(--text); font-size: 0.88rem; line-height: 1.6; }

[data-testid="stFileUploader"] { background: var(--surface) !important; border: 2px dashed var(--border) !important; border-radius: 10px !important; }
.stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; gap: 4px; }
.stTabs [data-baseweb="tab"] { background: var(--surface2) !important; color: var(--muted) !important; border-radius: 6px 6px 0 0 !important; font-family: 'Space Mono', monospace !important; font-size: 0.82rem !important; }
.stTabs [aria-selected="true"] { background: var(--accent) !important; color: white !important; }
.stDownloadButton button, .stButton button { background: var(--accent) !important; color: white !important; border: none !important; border-radius: 6px !important; font-family: 'Space Mono', monospace !important; font-size: 0.82rem !important; }
.stTextInput input { background: var(--surface2) !important; border: 1px solid var(--border) !important; color: var(--text) !important; border-radius: 6px !important; font-family: 'Space Mono', monospace !important; font-size: 0.82rem !important; }
div[data-testid="metric-container"] { background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 12px; }
</style>
""", unsafe_allow_html=True)


# ─── Session State ─────────────────────────────────────────────────────────────
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'ai_suggestions' not in st.session_state:
    st.session_state.ai_suggestions = None
if 'ai_error' not in st.session_state:
    st.session_state.ai_error = None
if 'use_ai' not in st.session_state:
    st.session_state.use_ai = False
if 'last_file' not in st.session_state:
    st.session_state.last_file = None


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Process Bottleneck\n### Analyzer")
    st.markdown("---")
    st.markdown("**Required CSV columns:**")
    st.markdown("- `case_id` · `activity` · `timestamp`\n- `resource` *(optional)*")
    st.markdown("---")

    uploaded_file = st.file_uploader("📂 Upload CSV / Excel", type=["csv", "xlsx", "xls"])
    st.markdown("---")
    use_sample = st.button("▶ Use Sample Dataset", use_container_width=True)
    st.markdown("---")

    st.markdown("### 🤖 AI Suggestions")
    st.markdown("<small style='color:#7878a0'>Powered by Claude AI (claude-opus-4-6)</small>", unsafe_allow_html=True)

    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your key at console.anthropic.com",
        value=st.session_state.api_key
    )
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
        st.session_state.ai_suggestions = None

    use_ai_toggle = st.toggle("Enable AI Suggestions", value=st.session_state.use_ai)
    if use_ai_toggle != st.session_state.use_ai:
        st.session_state.use_ai = use_ai_toggle
        st.session_state.ai_suggestions = None

    if use_ai_toggle and not st.session_state.api_key:
        st.warning("⚠️ Enter API key above.")

    st.markdown("---")
    st.caption("v2.0 · AI-Powered · Process Excellence")


# ─── Load Data ─────────────────────────────────────────────────────────────────
df = None
source_label = ""

if use_sample:
    sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "sample_log.csv")
    df = load_and_validate(sample_path)
    source_label = "Sample Dataset (Order Processing)"
    if st.session_state.last_file != "sample":
        st.session_state.ai_suggestions = None
        st.session_state.last_file = "sample"
    st.sidebar.success("✅ Sample data loaded!")

elif uploaded_file is not None:
    try:
        df = load_and_validate(uploaded_file)
        source_label = uploaded_file.name
        if st.session_state.last_file != uploaded_file.name:
            st.session_state.ai_suggestions = None
            st.session_state.last_file = uploaded_file.name
        st.sidebar.success(f"✅ Loaded: {uploaded_file.name}")
    except ValueError as e:
        st.sidebar.error(str(e))


# ─── Landing ───────────────────────────────────────────────────────────────────
if df is None:
    st.markdown("""
    <div style='text-align:center;padding:60px 20px;'>
        <h1 style='font-size:2.8rem;margin-bottom:8px;'>⚙ Process Bottleneck Analyzer</h1>
        <p style='color:#7878a0;font-size:1.05rem;max-width:580px;margin:0 auto 8px;'>
            Upload a process event log and instantly discover bottlenecks, KPIs, delay heatmaps, and improvement suggestions.
        </p>
        <p style='color:#9b59b6;font-size:0.9rem;'>✨ Now powered by Claude AI for intelligent, domain-aware recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, icon, label in [
        (c1, "📤", "Upload your CSV log file from the sidebar"),
        (c2, "🔍", "Automatic KPI & bottleneck analysis runs instantly"),
        (c3, "🤖", "Claude AI generates domain-specific improvement suggestions"),
    ]:
        col.markdown(f"<div class='kpi-card'><div class='kpi-number'>{icon}</div><div class='kpi-label'>{label}</div></div>", unsafe_allow_html=True)
    st.markdown("<br><p style='text-align:center;color:#7878a0;'>← Click <b>Use Sample Dataset</b> in the sidebar to try immediately</p>", unsafe_allow_html=True)
    st.stop()


# ─── Core Analysis ─────────────────────────────────────────────────────────────
with st.spinner("🔍 Running analysis..."):
    kpi_results = calculate_kpis(df)
    findings = full_analysis(kpi_results)

summary    = kpi_results['summary']
case_stats = kpi_results['case_stats']
activity_stats = kpi_results['activity_stats']
df_waiting = kpi_results['df_with_waiting']


# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown("# ⚙ Process Bottleneck Analyzer")
ai_status = '<span class="ai-badge">🤖 AI ACTIVE</span>' if (st.session_state.use_ai and st.session_state.api_key) else '<span class="rule-badge">Rule-based mode</span>'
st.markdown(
    f"<p style='color:#7878a0;font-size:0.9rem;margin-top:-10px;'>"
    f"📁 <b>{source_label}</b> &nbsp;|&nbsp; {summary['total_cases']} cases "
    f"&nbsp;|&nbsp; {summary['unique_activities']} activities "
    f"&nbsp;|&nbsp; {summary['total_activities_logged']} events &nbsp;|&nbsp; {ai_status}</p>",
    unsafe_allow_html=True
)
st.markdown("---")


# ─── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown("### 📊 Key Performance Indicators")
cols = st.columns(6)
for col, num, lbl in zip(cols, [
    summary['total_cases'],
    f"{summary['avg_cycle_time_hrs']}h",
    f"{summary['max_cycle_time_hrs']}h",
    f"{summary['min_cycle_time_hrs']}h",
    f"{summary['avg_waiting_time_hrs']}h",
    summary['unique_activities'],
], ["Total Cases", "Avg Cycle Time", "Max Cycle Time", "Min Cycle Time", "Avg Waiting Time", "Process Steps"]):
    col.markdown(f"<div class='kpi-card'><div class='kpi-number'>{num}</div><div class='kpi-label'>{lbl}</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔴 Bottlenecks", "🔥 Heatmap", "📈 Charts", "🤖 AI Suggestions", "📋 Raw Data"
])

# ── Tab 1 ──────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### 🔴 Top Bottleneck Activities")
    for _, row in findings['bottlenecks'].iterrows():
        sev = row.get('severity', 'Low').lower()
        st.markdown(f"""
        <div class='suggestion-card {"" if sev=="critical" else sev}'>
            <div class='suggestion-title'>
                #{int(row.get('rank',0))} &nbsp; {row['activity']} &nbsp;
                <span class='badge-{sev}'>{row.get('severity','')}</span>
            </div>
            <div class='suggestion-issue'>
                Avg Wait: <b>{row['avg_waiting_hrs']:.2f} hrs</b> &nbsp;|&nbsp;
                Max: <b>{row['max_waiting_hrs']:.2f} hrs</b> &nbsp;|&nbsp;
                Std Dev: <b>{row['std_waiting_hrs']:.2f} hrs</b> &nbsp;|&nbsp;
                Frequency: <b>{int(row['frequency'])}</b>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 All Activities — Waiting Time Ranking")
    st.image(plot_bottleneck_bar(activity_stats), use_container_width=True)

    incon = findings['inconsistent_steps']
    st.markdown("---")
    st.markdown("### ⚠️ Inconsistent Steps")
    if incon.empty:
        st.success("✅ No highly inconsistent steps detected.")
    else:
        st.dataframe(incon[['activity','avg_waiting_hrs','std_waiting_hrs','max_waiting_hrs']].round(2), use_container_width=True)

    if not findings['single_resource_risk'].empty:
        st.markdown("---")
        st.markdown("### 🔺 Single Resource Risk")
        st.dataframe(findings['single_resource_risk'], use_container_width=True)

# ── Tab 2 ──────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🔥 Delay Heatmap — Waiting Time per Case × Activity")
    st.caption("Darker = longer wait.")
    st.image(plot_heatmap(df_waiting), use_container_width=True)

# ── Tab 3 ──────────────────────────────────────────────────────────────────────
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📊 Cycle Time Distribution")
        st.image(plot_cycle_time_distribution(case_stats), use_container_width=True)
    with c2:
        st.markdown("### 👤 Resource Workload")
        buf = plot_resource_workload(df_waiting)
        st.image(buf, use_container_width=True) if buf else st.info("No resource column found.")
    st.markdown("---")
    st.markdown("### 📋 Case-Level Summary")
    d = case_stats.copy().reset_index()
    d['cycle_time_hrs'] = d['cycle_time_hrs'].round(2)
    st.dataframe(d, use_container_width=True)

# ── Tab 4: AI Suggestions ──────────────────────────────────────────────────────
with tab4:
    st.markdown("### 🤖 AI-Powered Process Improvement Suggestions")

    def render_suggestions(suggestions_list):
        sev_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        sorted_s = sorted(suggestions_list, key=lambda x: sev_order.get(x['severity'], 4))
        for s in sorted_s:
            sev_lower = s['severity'].lower()
            t_lower = s['type'].lower().replace(' ', '')
            card_cls = 'suggestion-card'
            if t_lower == 'quickwin':
                card_cls += ' quickwin'
            elif t_lower == 'strategicrecommendation':
                card_cls += ' strategic'
            elif sev_lower in ['high','medium','low']:
                card_cls += f' {sev_lower}'
            ai_tag = '<span class="ai-badge">🤖 AI</span>' if s.get('ai_generated') else '<span class="rule-badge">Rule-based</span>'
            st.markdown(f"""
            <div class='{card_cls}'>
                <div class='suggestion-title'>
                    {s['activity']} &nbsp;
                    <span class='badge-{sev_lower}'>{s['severity']}</span>
                    &nbsp;<span style='color:#7878a0;font-size:0.78rem;'>{s['type']}</span>
                    {ai_tag}
                </div>
                <div class='suggestion-issue'>{s['issue']}</div>
                <div class='suggestion-text'>{s['suggestion']}</div>
            </div>""", unsafe_allow_html=True)

    if st.session_state.use_ai and st.session_state.api_key:
        st.markdown("""
        <div class='ai-panel'>
            <div class='ai-panel-header'>✦ Claude AI Analysis Mode Active</div>
            Claude analyzes your specific process, infers the industry domain, and generates
            tailored recommendations using Lean, Six Sigma and process excellence methodologies.
        </div>""", unsafe_allow_html=True)

        if st.button("🤖 Generate AI Suggestions", use_container_width=False):
            with st.spinner("🤖 Claude AI is thinking about your process..."):
                suggs, err = generate_ai_suggestions(findings, summary, api_key=st.session_state.api_key)
                st.session_state.ai_suggestions = suggs
                st.session_state.ai_error = err

        if st.session_state.ai_error:
            if st.session_state.ai_error == "invalid_key":
                st.error("❌ Invalid API key. Please check your Anthropic API key.")
            else:
                st.warning(f"⚠️ AI call failed ({st.session_state.ai_error}). Showing rule-based suggestions.")
                render_suggestions(fallback_suggestions(findings, summary))

        elif st.session_state.ai_suggestions:
            st.success(f"✅ Claude AI generated {len(st.session_state.ai_suggestions)} intelligent suggestions.")
            st.markdown("<br>", unsafe_allow_html=True)
            render_suggestions(st.session_state.ai_suggestions)

        else:
            st.info("👆 Click the button above to generate AI suggestions for your process.")

    else:
        if not st.session_state.use_ai:
            st.info("💡 **AI mode is off.** Enable it in the sidebar with your Anthropic API key to get intelligent suggestions from Claude.")
        else:
            st.warning("⚠️ **API key missing.** Enter your Anthropic API key in the sidebar.")

        st.markdown("#### 📋 Rule-Based Suggestions")
        st.caption("Enable AI in the sidebar for much smarter, context-aware recommendations.")
        render_suggestions(fallback_suggestions(findings, summary))

    st.markdown("---")
    with st.expander("🔑 How to get a free Anthropic API Key"):
        st.markdown("""
1. Go to **[console.anthropic.com](https://console.anthropic.com)**
2. Sign up / Log in with your email
3. Click **API Keys** in the left menu → **Create Key**
4. Copy the key (it starts with `sk-ant-...`)
5. Paste it in the **sidebar** under AI Suggestions
6. Toggle **Enable AI Suggestions** ON
7. Come back to this tab and click **Generate AI Suggestions**
        """)

# ── Tab 5 ──────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown("### 📋 Raw Event Log")
    st.dataframe(df, use_container_width=True, height=400)
    st.markdown("### 📊 Activity Statistics Table")
    st.dataframe(activity_stats.round(2), use_container_width=True)


# ─── Export ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📥 Export Report")
export_suggs = st.session_state.ai_suggestions if st.session_state.ai_suggestions else fallback_suggestions(findings, summary)
csv_data = export_summary_csv(kpi_results, findings, export_suggs)
st.download_button(
    label="⬇ Download Full Analysis Report (CSV)",
    data=csv_data,
    file_name="bottleneck_analysis_report.csv",
    mime="text/csv",
)
