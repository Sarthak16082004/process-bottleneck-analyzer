import pandas as pd
import numpy as np

def load_and_validate(file):
    """Load CSV or Excel and validate required columns."""
    try:
        if hasattr(file, 'name'):
            if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file)
        else:
            df = pd.read_csv(file)
    except Exception as e:
        raise ValueError(f"Could not read file: {e}")

    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    required = ['case_id', 'activity', 'timestamp']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Your file must have: case_id, activity, timestamp")

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['case_id', 'timestamp']).reset_index(drop=True)
    return df


def calculate_kpis(df):
    """Calculate all KPIs per case and per activity."""
    results = {}

    # Per-case metrics
    case_groups = df.groupby('case_id')
    case_stats = case_groups.agg(
        start_time=('timestamp', 'min'),
        end_time=('timestamp', 'max'),
        num_activities=('activity', 'count')
    )
    case_stats['cycle_time_hrs'] = (case_stats['end_time'] - case_stats['start_time']).dt.total_seconds() / 3600
    results['case_stats'] = case_stats

    # Per-activity waiting time (time from previous step end to this step start)
    df_sorted = df.sort_values(['case_id', 'timestamp'])
    df_sorted['prev_timestamp'] = df_sorted.groupby('case_id')['timestamp'].shift(1)
    df_sorted['waiting_time_hrs'] = (
        df_sorted['timestamp'] - df_sorted['prev_timestamp']
    ).dt.total_seconds() / 3600
    df_sorted['waiting_time_hrs'] = df_sorted['waiting_time_hrs'].fillna(0)
    results['df_with_waiting'] = df_sorted

    # Activity-level aggregation
    activity_stats = df_sorted.groupby('activity').agg(
        avg_waiting_hrs=('waiting_time_hrs', 'mean'),
        max_waiting_hrs=('waiting_time_hrs', 'max'),
        min_waiting_hrs=('waiting_time_hrs', 'min'),
        std_waiting_hrs=('waiting_time_hrs', 'std'),
        frequency=('activity', 'count')
    ).fillna(0).reset_index()

    # Preserve natural process order
    activity_order = df['activity'].unique().tolist()
    activity_stats['order'] = activity_stats['activity'].map(
        {a: i for i, a in enumerate(activity_order)}
    )
    activity_stats = activity_stats.sort_values('order').drop(columns='order')
    results['activity_stats'] = activity_stats

    # Summary KPIs
    results['summary'] = {
        'total_cases': int(case_stats.shape[0]),
        'avg_cycle_time_hrs': round(float(case_stats['cycle_time_hrs'].mean()), 2),
        'max_cycle_time_hrs': round(float(case_stats['cycle_time_hrs'].max()), 2),
        'min_cycle_time_hrs': round(float(case_stats['cycle_time_hrs'].min()), 2),
        'total_activities_logged': int(len(df)),
        'unique_activities': int(df['activity'].nunique()),
        'avg_waiting_time_hrs': round(float(df_sorted['waiting_time_hrs'].mean()), 2),
    }

    return results
