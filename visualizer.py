import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
import io

COLORS = {
    'primary': '#1a1a2e',
    'accent': '#e94560',
    'highlight': '#0f3460',
    'gold': '#f5a623',
    'green': '#2ecc71',
    'bg': '#16213e',
    'text': '#eaeaea'
}

def _base_fig(figsize=(10, 5)):
    fig, ax = plt.subplots(figsize=figsize, facecolor=COLORS['primary'])
    ax.set_facecolor(COLORS['primary'])
    for spine in ax.spines.values():
        spine.set_color('#333355')
    ax.tick_params(colors=COLORS['text'], labelsize=9)
    ax.xaxis.label.set_color(COLORS['text'])
    ax.yaxis.label.set_color(COLORS['text'])
    ax.title.set_color(COLORS['text'])
    return fig, ax


def plot_bottleneck_bar(activity_stats):
    """Horizontal bar chart of avg waiting time per activity."""
    fig, ax = _base_fig(figsize=(10, 6))

    stats = activity_stats.sort_values('avg_waiting_hrs', ascending=True)
    colors = []
    for v in stats['avg_waiting_hrs']:
        if v >= 5:
            colors.append(COLORS['accent'])
        elif v >= 2:
            colors.append(COLORS['gold'])
        else:
            colors.append(COLORS['green'])

    bars = ax.barh(stats['activity'], stats['avg_waiting_hrs'], color=colors, height=0.55, edgecolor='none')

    # Value labels
    for bar, val in zip(bars, stats['avg_waiting_hrs']):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f'{val:.1f}h', va='center', color=COLORS['text'], fontsize=9, fontweight='bold')

    ax.set_xlabel('Average Waiting Time (Hours)', fontsize=10, labelpad=10)
    ax.set_title('⏱ Bottleneck Analysis — Avg Waiting Time Per Activity', fontsize=12, pad=15, fontweight='bold')
    ax.grid(axis='x', color='#333355', linewidth=0.5, alpha=0.7)
    ax.set_axisbelow(True)

    # Legend
    patches = [
        mpatches.Patch(color=COLORS['accent'], label='Critical (≥5h)'),
        mpatches.Patch(color=COLORS['gold'], label='High (≥2h)'),
        mpatches.Patch(color=COLORS['green'], label='Normal (<2h)'),
    ]
    ax.legend(handles=patches, loc='lower right', facecolor=COLORS['highlight'],
              labelcolor=COLORS['text'], edgecolor='none', fontsize=8)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=COLORS['primary'])
    plt.close(fig)
    buf.seek(0)
    return buf


def plot_heatmap(df_with_waiting):
    """Heatmap of waiting time per case per activity."""
    pivot = df_with_waiting.pivot_table(
        index='case_id', columns='activity', values='waiting_time_hrs', aggfunc='mean'
    ).fillna(0)

    # Keep column order from process flow
    activity_order = df_with_waiting.drop_duplicates('activity').sort_values(
        df_with_waiting.columns[df_with_waiting.columns.get_loc('timestamp')] if 'timestamp' in df_with_waiting.columns else 'activity'
    )['activity'].tolist()
    ordered_cols = [c for c in activity_order if c in pivot.columns]
    pivot = pivot[ordered_cols] if ordered_cols else pivot

    fig, ax = plt.subplots(figsize=(12, max(4, len(pivot) * 0.5 + 2)), facecolor=COLORS['primary'])
    ax.set_facecolor(COLORS['primary'])

    cmap = sns.color_palette("YlOrRd", as_cmap=True)
    sns.heatmap(pivot, ax=ax, cmap=cmap, linewidths=0.3, linecolor='#1a1a2e',
                annot=True, fmt='.1f', annot_kws={'size': 8, 'color': 'black'},
                cbar_kws={'label': 'Waiting Time (hrs)', 'shrink': 0.8})

    ax.set_title('🔥 Delay Heatmap — Waiting Time per Case per Activity (hrs)',
                 fontsize=12, pad=15, fontweight='bold', color=COLORS['text'])
    ax.tick_params(colors=COLORS['text'], labelsize=8)
    ax.set_xlabel('Activity', fontsize=10, color=COLORS['text'])
    ax.set_ylabel('Case ID', fontsize=10, color=COLORS['text'])
    plt.xticks(rotation=30, ha='right')
    plt.yticks(rotation=0)

    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(colors=COLORS['text'], labelsize=8)
    cbar.set_label('Waiting Time (hrs)', color=COLORS['text'])

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=COLORS['primary'])
    plt.close(fig)
    buf.seek(0)
    return buf


def plot_cycle_time_distribution(case_stats):
    """Histogram of cycle times across all cases."""
    fig, ax = _base_fig(figsize=(9, 4))

    data = case_stats['cycle_time_hrs']
    ax.hist(data, bins=min(10, len(data)), color=COLORS['accent'], edgecolor=COLORS['primary'],
            linewidth=0.8, alpha=0.85)
    ax.axvline(data.mean(), color=COLORS['gold'], linestyle='--', linewidth=1.5,
               label=f'Mean: {data.mean():.1f}h')
    ax.axvline(data.median(), color=COLORS['green'], linestyle='--', linewidth=1.5,
               label=f'Median: {data.median():.1f}h')

    ax.set_xlabel('Cycle Time (Hours)', fontsize=10)
    ax.set_ylabel('Number of Cases', fontsize=10)
    ax.set_title('📊 Cycle Time Distribution Across All Cases', fontsize=12, pad=15, fontweight='bold')
    ax.legend(facecolor=COLORS['highlight'], labelcolor=COLORS['text'], edgecolor='none', fontsize=9)
    ax.grid(axis='y', color='#333355', linewidth=0.5, alpha=0.6)
    ax.set_axisbelow(True)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=COLORS['primary'])
    plt.close(fig)
    buf.seek(0)
    return buf


def plot_resource_workload(df):
    """Bar chart of how many activities each resource handled."""
    if 'resource' not in df.columns:
        return None

    resource_counts = df['resource'].value_counts().reset_index()
    resource_counts.columns = ['resource', 'count']

    fig, ax = _base_fig(figsize=(8, 4))
    bar_colors = [COLORS['accent'] if i == 0 else COLORS['highlight'] for i in range(len(resource_counts))]
    bars = ax.bar(resource_counts['resource'], resource_counts['count'],
                  color=bar_colors, edgecolor='none', width=0.55)

    for bar, val in zip(bars, resource_counts['count']):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                str(val), ha='center', va='bottom', color=COLORS['text'], fontsize=9, fontweight='bold')

    ax.set_xlabel('Resource / Agent', fontsize=10)
    ax.set_ylabel('Tasks Handled', fontsize=10)
    ax.set_title('👤 Resource Workload Distribution', fontsize=12, pad=15, fontweight='bold')
    ax.grid(axis='y', color='#333355', linewidth=0.5, alpha=0.6)
    ax.set_axisbelow(True)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=COLORS['primary'])
    plt.close(fig)
    buf.seek(0)
    return buf
