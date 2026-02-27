import csv
import io


def export_summary_csv(kpi_results, findings, suggestions):
    """Generate a downloadable CSV summary report."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Summary KPIs
    writer.writerow(['=== PROCESS BOTTLENECK ANALYSIS REPORT ==='])
    writer.writerow([])
    writer.writerow(['--- SUMMARY KPIs ---'])
    writer.writerow(['Metric', 'Value'])
    for k, v in kpi_results['summary'].items():
        writer.writerow([k.replace('_', ' ').title(), v])

    writer.writerow([])
    writer.writerow(['--- TOP BOTTLENECKS ---'])
    writer.writerow(['Rank', 'Activity', 'Avg Waiting Time (hrs)', 'Max Waiting (hrs)', 'Severity'])
    for _, row in findings['bottlenecks'].iterrows():
        writer.writerow([
            row.get('rank', ''),
            row['activity'],
            round(row['avg_waiting_hrs'], 2),
            round(row['max_waiting_hrs'], 2),
            row.get('severity', '')
        ])

    writer.writerow([])
    writer.writerow(['--- ALL ACTIVITY STATS ---'])
    writer.writerow(['Activity', 'Avg Wait (hrs)', 'Max Wait (hrs)', 'Std Dev (hrs)', 'Frequency'])
    for _, row in findings['activity_stats'].iterrows():
        writer.writerow([
            row['activity'],
            round(row['avg_waiting_hrs'], 2),
            round(row['max_waiting_hrs'], 2),
            round(row['std_waiting_hrs'], 2),
            row['frequency']
        ])

    writer.writerow([])
    writer.writerow(['--- IMPROVEMENT SUGGESTIONS ---'])
    writer.writerow(['Activity', 'Type', 'Severity', 'Issue', 'Suggestion'])
    for s in suggestions:
        writer.writerow([s['activity'], s['type'], s['severity'], s['issue'], s['suggestion']])

    return output.getvalue()
