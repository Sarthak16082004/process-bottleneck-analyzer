import json
import requests

# ─────────────────────────────────────────────────────
#  PASTE YOUR ANTHROPIC API KEY HERE
# ─────────────────────────────────────────────────────
ANTHROPIC_API_KEY = "your-api-key-here"   # <-- replace this
# ─────────────────────────────────────────────────────


def get_ai_suggestions(kpi_results, findings, api_key: str = None) -> dict:
    """
    Send process analysis data to Claude AI and get intelligent suggestions.
    Uses hardcoded key from top of file, or key passed as argument.
    Returns dict with 'suggestions' list and 'executive_summary' string.
    """

    # Use hardcoded key if no key passed from sidebar
    key_to_use = api_key if (api_key and api_key.startswith("sk-")) else ANTHROPIC_API_KEY

    if not key_to_use or key_to_use == "your-api-key-here":
        raise ValueError("No API key found. Please paste your Anthropic API key in ai_suggester.py at the top of the file.")

    summary        = kpi_results['summary']
    activity_stats = kpi_results['activity_stats']
    bottlenecks    = findings['bottlenecks']
    inconsistent   = findings['inconsistent_steps']
    single_resource= findings['single_resource_risk']

    # Build structured context
    activity_data = []
    for _, row in activity_stats.iterrows():
        activity_data.append({
            "activity":        row['activity'],
            "avg_waiting_hrs": round(row['avg_waiting_hrs'], 2),
            "max_waiting_hrs": round(row['max_waiting_hrs'], 2),
            "std_dev_hrs":     round(row['std_waiting_hrs'], 2),
            "frequency":       int(row['frequency'])
        })

    bottleneck_data = []
    for _, row in bottlenecks.iterrows():
        bottleneck_data.append({
            "rank":            int(row.get('rank', 0)),
            "activity":        row['activity'],
            "avg_waiting_hrs": round(row['avg_waiting_hrs'], 2),
            "severity":        row.get('severity', '')
        })

    inconsistent_data = []
    for _, row in inconsistent.iterrows():
        inconsistent_data.append({
            "activity":    row['activity'],
            "std_dev_hrs": round(row['std_waiting_hrs'], 2)
        })

    single_risk_data = []
    if not single_resource.empty:
        for _, row in single_resource.iterrows():
            single_risk_data.append({"activity": row['activity']})

    process_context = {
        "summary_kpis":             summary,
        "all_activities":           activity_data,
        "top_bottlenecks":          bottleneck_data,
        "inconsistent_steps":       inconsistent_data,
        "single_resource_risk_steps": single_risk_data
    }

    prompt = f"""You are a world-class Process Excellence Consultant with expertise in Lean, Six Sigma, and operational efficiency.

I have run a process mining analysis on a business workflow. Here is the complete analytical data:

{json.dumps(process_context, indent=2)}

Based on this data, provide a highly intelligent, specific, and actionable analysis. Your response must be valid JSON in exactly this structure:

{{
  "executive_summary": "A 3-4 sentence high-level narrative summary of the overall process health, key findings, and most critical issue to address first. Be specific about numbers.",
  "suggestions": [
    {{
      "activity": "name of the activity this suggestion is about",
      "type": "one of: Bottleneck | Inconsistency | Resource Risk | Process Design | Quick Win | Strategic",
      "severity": "one of: Critical | High | Medium | Low",
      "issue": "one concise sentence describing exactly what the data shows is wrong",
      "suggestion": "2-3 sentences of specific, expert-level recommendation. Reference actual numbers from the data. Include a concrete action step.",
      "expected_impact": "one sentence on what improvement to expect if this is fixed",
      "lean_principle": "which Lean/Six Sigma principle applies e.g. Eliminate Waste, Reduce Variation, Mistake-Proofing, Flow, Pull, Perfection, DMAIC, Kaizen, 5S, Value Stream Mapping"
    }}
  ]
}}

Rules:
- Generate 5 to 8 suggestions total
- Always reference specific numbers from the data
- Infer the likely industry from activity names and tailor advice accordingly
- Prioritize by severity: Critical first
- Include at least one Quick Win (immediate action) and one Strategic (long-term) suggestion
- Return ONLY valid JSON, no markdown fences, no explanation outside the JSON
"""

    headers = {
        "Content-Type":    "application/json",
        "x-api-key":       key_to_use,
        "anthropic-version": "2023-06-01"
    }

    payload = {
        "model":      "claude-sonnet-4-6",
        "max_tokens": 2000,
        "messages":   [{"role": "user", "content": prompt}]
    }

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=payload,
        timeout=60
    )

    # Raise clear error if API call failed
    if response.status_code != 200:
        raise ValueError(f"Anthropic API error {response.status_code}: {response.text}")

    body     = response.json()
    raw_text = body["content"][0]["text"].strip()

    # Strip markdown fences if present
    if "```" in raw_text:
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    result = json.loads(raw_text)
    return result
