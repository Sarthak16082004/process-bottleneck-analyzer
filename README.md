# ⚙ Process Bottleneck Analyzer — AI Powered

> An AI-powered business process analytics tool that automatically detects bottlenecks, calculates KPIs, and generates intelligent improvement suggestions using Claude AI.

---

## 🚀 Quick Start

### Step 1 — Install Python 3.10 or 3.11
Download from https://python.org
> ✅ During installation, check **"Add Python to PATH"**

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Add Your API Key
Open `ai_suggester.py` and paste your Anthropic API key:
```python
ANTHROPIC_API_KEY = "sk-ant-api03-your-key-here"
```
Get a free key at: https://console.anthropic.com

### Step 4 — Run the App
```bash
streamlit run app.py
```
Opens automatically at `http://localhost:8501`

---

## 🎯 What This Does

Upload any business process event log (CSV/Excel) and the tool will:

- **Detect bottlenecks** — ranks every process step by average waiting time
- **Calculate KPIs** — Cycle Time, Lead Time, Waiting Time, Throughput
- **Generate a delay heatmap** — shows which cases are worst affected at which steps
- **Identify inconsistent steps** — steps with high performance variance
- **Flag resource risks** — single points of failure
- **AI-powered suggestions** — Claude AI reads your process data and generates expert-level, domain-aware improvement recommendations with Lean/Six Sigma tagging
- **Export report** — download full analysis as CSV

---

## 🤖 AI Integration

This tool uses the **Anthropic Claude API** (`claude-sonnet-4-6`) to generate intelligent suggestions. Unlike rule-based systems, the AI:

- Understands the domain from your activity names (hospital, banking, HR, manufacturing etc.)
- References actual numbers from your data in every suggestion
- Applies Lean and Six Sigma principles contextually
- Classifies suggestions as Quick Win or Strategic
- Predicts expected impact of each improvement
- Writes an Executive Summary of overall process health

---

## 📂 Input File Format

Your CSV must contain these columns:

| Column | Required | Description | Example |
|---|---|---|---|
| case_id | ✅ Yes | Unique process instance ID | ORDER_001 |
| activity | ✅ Yes | Name of the process step | Invoice Approval |
| timestamp | ✅ Yes | Date and time of the step | 2024-01-15 10:30:00 |
| resource | ❌ Optional | Who performed the step | Agent_A |

Sample file included at: `sample_data/sample_log.csv`

---

## 🏭 Supported Domains (Tested)

- Order Processing / Supply Chain
- Hospital Patient Flow
- IT Helpdesk Ticket Resolution
- HR Recruitment Pipeline
- Bank Loan Approval
- E-Commerce Returns
- Manufacturing Quality Control

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| UI / Frontend | Streamlit |
| Data Processing | Python, Pandas, NumPy |
| AI / LLM | Anthropic Claude API (claude-sonnet-4-6) |
| Visualization | Matplotlib, Seaborn |
| HTTP Client | Requests |
| Export | CSV (built-in) |
| File Support | CSV, Excel (openpyxl) |

---

## 📁 Project Structure

```
process-bottleneck-analyzer/
├── app.py              ← Main Streamlit application (UI + routing)
├── processor.py        ← Data loading, validation & KPI calculation
├── analyzer.py         ← Bottleneck detection & process mining logic
├── ai_suggester.py     ← Claude AI API integration & prompt engineering
├── suggester.py        ← Rule-based fallback suggestion engine
├── visualizer.py       ← Chart generation (bar, heatmap, histogram)
├── reporter.py         ← CSV report export
├── requirements.txt    ← Python dependencies
├── README.md           ← This file
└── sample_data/
    └── sample_log.csv  ← Sample order processing event log
```

---

## 📊 Features Overview

| Feature | Description |
|---|---|
| KPI Dashboard | 6 KPI cards: Cycle Time, Lead Time, Waiting Time, Throughput |
| Bottleneck Detection | Top 3 bottlenecks ranked by avg waiting time with severity labels |
| Delay Heatmap | Case × Activity matrix showing delay concentration |
| Cycle Time Distribution | Histogram with mean and median overlays |
| Resource Workload | Bar chart of task distribution across agents/resources |
| AI Suggestions | 5-8 Claude AI generated suggestions with Lean tags + impact |
| Rule Suggestions | Backup rule-based suggestions for comparison |
| Report Export | Full CSV download with KPIs, bottlenecks, and suggestions |

---

## ⚠️ Security Note

Never commit your API key to GitHub. Before pushing:
```python
ANTHROPIC_API_KEY = "your-api-key-here"  # restore placeholder
```

---

Built as a portfolio project for **Process Excellence Specialist** role.  
Demonstrates: Process Analytics · AI/LLM Integration · Data Visualization · Python Development
