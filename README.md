# ⚙ Process Bottleneck Analyzer

A data analytics tool built for the **Process Excellence Specialist** role.
Upload any process event log (CSV/Excel) and instantly identify bottlenecks, KPIs, delay patterns, and receive improvement suggestions.

---

## 🚀 How to Run (Step by Step)

### Step 1 — Install Python
Download Python 3.10 or 3.11 from https://python.org
> ✅ During installation, check **"Add Python to PATH"**

### Step 2 — Download / Clone this Project
Put the project folder anywhere on your computer (e.g. `C:\projects\process-bottleneck-analyzer`)

### Step 3 — Open Terminal / Command Prompt
- Windows: Press `Win + R`, type `cmd`, press Enter
- Or open VS Code → Terminal → New Terminal

### Step 4 — Navigate to the Project Folder
```bash
cd path/to/process-bottleneck-analyzer
```

### Step 5 — Install Dependencies
```bash
pip install -r requirements.txt
```
> This installs: streamlit, pandas, matplotlib, seaborn, openpyxl, numpy

### Step 6 — Run the App
```bash
streamlit run app.py
```

> The app will automatically open in your browser at `http://localhost:8501`

---

## 📂 Input File Format

Your CSV must contain these columns:

| Column | Required | Description | Example |
|---|---|---|---|
| case_id | ✅ Yes | Unique process ID | ORDER_001 |
| activity | ✅ Yes | Process step name | "Invoice Approval" |
| timestamp | ✅ Yes | Date and time | 2024-01-15 10:30:00 |
| resource | ❌ Optional | Who handled it | Agent_A |

A sample file is included at: `sample_data/sample_log.csv`

---

## 🔍 Features

- **KPI Dashboard** — Cycle Time, Lead Time, Waiting Time, Throughput
- **Bottleneck Detection** — Top bottleneck activities ranked by delay
- **Delay Heatmap** — See which cases/steps have worst delays
- **Inconsistency Detection** — Steps with high performance variance
- **Resource Risk Analysis** — Single points of failure
- **Improvement Suggestions** — Rule-based actionable recommendations
- **Export Report** — Download full analysis as CSV

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend/UI | Streamlit |
| Data Processing | Python + Pandas |
| Visualization | Matplotlib + Seaborn |
| Export | CSV (built-in) |

---

## 📁 Project Structure

```
process-bottleneck-analyzer/
├── app.py           ← Main Streamlit application
├── processor.py     ← Data loading & KPI calculation
├── analyzer.py      ← Bottleneck detection logic
├── visualizer.py    ← Chart generation
├── suggester.py     ← Improvement suggestion engine
├── reporter.py      ← CSV report export
├── requirements.txt ← Python dependencies
├── README.md        ← This file
└── sample_data/
    └── sample_log.csv ← Test dataset
```

---

Built as a portfolio project for Process Excellence Specialist role interview.
