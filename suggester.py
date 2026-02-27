def generate_suggestions(findings, kpi_summary):
    """Generate improvement suggestions based on analysis findings."""
    suggestions = []

    bottlenecks = findings['bottlenecks']
    inconsistent = findings['inconsistent_steps']
    single_resource = findings['single_resource_risk']
    activity_stats = findings['activity_stats']

    # Calculate median for comparison
    median_wait = activity_stats['avg_waiting_hrs'].median()

    # Bottleneck suggestions
    for _, row in bottlenecks.iterrows():
        act = row['activity']
        hrs = round(row['avg_waiting_hrs'], 2)
        sev = row['severity']

        if sev == 'Critical':
            suggestions.append({
                'activity': act,
                'severity': sev,
                'issue': f"Average wait of {hrs} hrs — critically high delay",
                'suggestion': f"🔴 CRITICAL: '{act}' is your biggest bottleneck. Immediately assign additional resources, consider parallel processing, or automate this step. Review if this step can be split into sub-tasks.",
                'type': 'Bottleneck'
            })
        elif sev == 'High':
            suggestions.append({
                'activity': act,
                'severity': sev,
                'issue': f"Average wait of {hrs} hrs — high delay",
                'suggestion': f"🟠 HIGH: '{act}' is causing significant delay. Consider adding a dedicated agent, setting SLA alerts, or reviewing the approval workflow for this step.",
                'type': 'Bottleneck'
            })
        else:
            suggestions.append({
                'activity': act,
                'severity': sev,
                'issue': f"Average wait of {hrs} hrs — moderate delay",
                'suggestion': f"🟡 MEDIUM: '{act}' has above-average wait times. Monitor closely and set performance benchmarks for this step.",
                'type': 'Bottleneck'
            })

    # Inconsistency suggestions
    for _, row in inconsistent.iterrows():
        act = row['activity']
        std = round(row['std_waiting_hrs'], 2)
        suggestions.append({
            'activity': act,
            'severity': 'Medium',
            'issue': f"High variability (std dev: {std} hrs) — inconsistent performance",
            'suggestion': f"⚠️ INCONSISTENCY: '{act}' shows unpredictable performance. Standardize the process with SOPs (Standard Operating Procedures), ensure all agents follow the same workflow.",
            'type': 'Inconsistency'
        })

    # Single resource risk
    for _, row in single_resource.iterrows():
        act = row['activity']
        suggestions.append({
            'activity': act,
            'severity': 'High',
            'issue': "Only 1 resource handles this step — single point of failure",
            'suggestion': f"🔺 RISK: '{act}' is dependent on a single resource. Cross-train at least one backup agent and document the process to reduce dependency.",
            'type': 'Resource Risk'
        })

    # Overall cycle time suggestion
    avg_ct = kpi_summary['avg_cycle_time_hrs']
    if avg_ct > 24:
        suggestions.append({
            'activity': 'Overall Process',
            'severity': 'High',
            'issue': f"Average cycle time is {avg_ct} hrs (over 24 hours)",
            'suggestion': "🕐 CYCLE TIME: Overall process exceeds 24 hours on average. Conduct an end-to-end value stream mapping exercise to eliminate non-value-adding steps.",
            'type': 'Process Health'
        })

    if not suggestions:
        suggestions.append({
            'activity': 'All Steps',
            'severity': 'Low',
            'issue': 'No major issues detected',
            'suggestion': '✅ Your process looks healthy! Continue monitoring KPIs and set up regular reviews to maintain performance.',
            'type': 'Process Health'
        })

    return suggestions
