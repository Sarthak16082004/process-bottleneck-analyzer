import json
import requests

# ============================================================
#   PASTE YOUR ANTHROPIC API KEY BELOW (replace the value)
# ============================================================
ANTHROPIC_API_KEY = "your-api-key-here"
# ============================================================


def get_ai_suggestions(kpi_results, findings) -> dict:
    """Call Claude AI API and return suggestions + executive summary."""

    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "your-api-key-here":
        raise ValueError(
            "API key not set! Open ai_suggester.py and paste your key into ANTHROPIC_API_KEY at the top of the file."
        )

    summary         = kpi_results['summary']
    activity_stats  = kpi_results['activity_stats']
    bottlenecks     = findings['bottlenecks']
    inconsistent    = findings['inconsistent_steps']
    single_resource = findings['single_resource_risk']

    activity_data = [
        {
            "activity":        row['activity'],
            "avg_waiting_hrs": round(row['avg_waiting_hrs'], 2),
            "max_waiting_hrs": round(row['max_waiting_hrs'], 2),
            "std_dev_hrs":     round(row['std_waiting_hrs'], 2),
            "frequency":       int(row['frequency'])
        }
        for _, row in activity_stats.iterrows()
    ]

    bottleneck_data = [
        {
            "rank":            int(row.get('rank', 0)),
            "activity":        row['activity'],
            "avg_waiting_hrs": round(row['avg_waiting_hrs'], 2),
            "severity":        row.get('severity', '')
        }
        for _, row in bottlenecks.iterrows()
    ]

    inconsistent_data = [
        {"activity": row['activity'], "std_dev_hrs": round(row['std_waiting_hrs'], 2)}
        for _, row in inconsistent.iterrows()
    ]

    single_risk_data = (
        [{"activity": row['activity']} for _, row in single_resource.iterrows()]
        if not single_resource.empty else []
    )

    process_context = {
        "summary_kpis":               summary,
        "all_activities":             activity_data,
        "top_bottlenecks":            bottleneck_data,
        "inconsistent_steps":         inconsistent_data,
        "single_resource_risk_steps": single_risk_data
    }

    prompt = f"""You are a world-class Process Excellence Consultant with expertise in Lean, Six Sigma, and operational efficiency.

I have run a process mining analysis on a business workflow. Here is the complete analytical data:

{json.dumps(process_context, indent=2)}

Respond ONLY with valid JSON in exactly this format (no markdown, no explanation outside JSON):

{{
  "executive_summary": "3-4 sentence expert summary of process health. Reference specific numbers.",
  "suggestions": [
    {{
      "activity": "activity name",
      "type": "Bottleneck | Inconsistency | Resource Risk | Process Design | Quick Win | Strategic",
      "severity": "Critical | High | Medium | Low",
      "issue": "One sentence describing the exact problem shown in the data.",
      "suggestion": "2-3 sentences of expert recommendation referencing actual numbers.",
      "expected_impact": "One sentence on expected improvement.",
      "lean_principle": "Relevant Lean/Six Sigma principle e.g. Eliminate Waste, Reduce Variation, DMAIC, Kaizen"
    }}
  ]
}}

Generate 5-8 suggestions. Sort by severity Critical first. Include at least one Quick Win and one Strategic suggestion."""

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Content-Type":      "application/json",
            "x-api-key":         ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01"
        },
        json={
            "model":      "claude-sonnet-4-6",
            "max_tokens": 2000,
            "messages":   [{"role": "user", "content": prompt}]
        },
        timeout=60
    )

    if response.status_code != 200:
        raise ValueError(f"API Error {response.status_code}: {response.text}")

    raw = response.json()["content"][0]["text"].strip()

    # Strip markdown fences if model wrapped in ```json ... ```
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)
