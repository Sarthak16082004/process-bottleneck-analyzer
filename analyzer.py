import pandas as pd
import numpy as np


def detect_bottlenecks(activity_stats, top_n=3):
    """Identify top N bottleneck activities based on avg waiting time."""
    ranked = activity_stats.sort_values('avg_waiting_hrs', ascending=False).reset_index(drop=True)
    bottlenecks = ranked.head(top_n).copy()
    bottlenecks['rank'] = range(1, len(bottlenecks) + 1)
    bottlenecks['severity'] = bottlenecks['avg_waiting_hrs'].apply(classify_severity)
    return bottlenecks


def classify_severity(avg_hrs):
    if avg_hrs >= 5:
        return 'Critical'
    elif avg_hrs >= 2:
        return 'High'
    elif avg_hrs >= 0.5:
        return 'Medium'
    else:
        return 'Low'


def detect_inconsistent_steps(activity_stats, threshold_multiplier=1.5):
    """Steps with high std deviation — inconsistent performance."""
    median_std = activity_stats['std_waiting_hrs'].median()
    inconsistent = activity_stats[
        activity_stats['std_waiting_hrs'] > median_std * threshold_multiplier
    ].copy()
    inconsistent = inconsistent.sort_values('std_waiting_hrs', ascending=False)
    return inconsistent


def detect_single_resource_risk(df):
    """Steps handled by only one resource — single point of failure."""
    if 'resource' not in df.columns:
        return pd.DataFrame()
    resource_counts = df.groupby('activity')['resource'].nunique().reset_index()
    resource_counts.columns = ['activity', 'unique_resources']
    risky = resource_counts[resource_counts['unique_resources'] == 1]
    return risky


def full_analysis(kpi_results):
    """Run all analysis and return structured findings."""
    activity_stats = kpi_results['activity_stats']
    df = kpi_results['df_with_waiting']

    findings = {
        'bottlenecks': detect_bottlenecks(activity_stats),
        'inconsistent_steps': detect_inconsistent_steps(activity_stats),
        'single_resource_risk': detect_single_resource_risk(df),
        'activity_stats': activity_stats,
    }
    return findings
