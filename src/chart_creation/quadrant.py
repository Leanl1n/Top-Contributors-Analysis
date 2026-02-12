import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from matplotlib.ticker import FuncFormatter

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


def format_reach(x, pos=None):
    """Format large numbers with K/M/B suffixes for thousands/millions/billions."""
    try:
        n = float(x)
    except Exception:
        return str(x)
    abs_n = abs(n)
    if abs_n >= 1_000_000_000:
        val = n / 1_000_000_000
        suffix = 'B'
    elif abs_n >= 1_000_000:
        val = n / 1_000_000
        suffix = 'M'
    elif abs_n >= 1_000:
        val = n / 1_000
        suffix = 'K'
    else:
        return str(int(n))
    s = f"{val:.1f}".rstrip('0').rstrip('.')
    return f"{s}{suffix}"


def prepare_quadrant_df(df):
    """Normalize and validate DataFrame for quadrant analysis. Returns (df, error_msg)."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    if 'Authors' not in df.columns and len(df.columns) > 0:
        df = df.rename(columns={df.columns[0]: 'Authors'})
    reach_col = None
    for c in df.columns:
        if 'reach' in str(c).lower():
            reach_col = c
            break
    if reach_col is None:
        return None, 'Could not find a Reach column (need a column whose name contains "reach").'
    sent_col = None
    for c in df.columns:
        if 'sentiment' in str(c).lower():
            sent_col = c
            break
    if sent_col is None:
        return None, 'Could not find a Sentiment column (need a column whose name contains "sentiment").'
    df['Reach'] = (
        df[reach_col].astype(str)
        .str.replace(r'[^0-9]', '', regex=True)
        .replace('', '0')
        .astype(int)
    )
    df['Sentiment Score'] = pd.to_numeric(df[sent_col], errors='coerce').fillna(0)
    return df, None


def build_quadrant_figure(df):
    """Build quadrant analysis figure (matplotlib). Returns a matplotlib Figure."""
    df, err = prepare_quadrant_df(df)
    if err:
        raise ValueError(err)
    authors = df['Authors'].astype(str).tolist()
    reach = df['Reach'].tolist()
    sentiment = df['Sentiment Score'].tolist()
    mean_reach = np.mean(reach)
    mean_sentiment = np.mean(sentiment)

    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_alpha(0)
    ax = plt.gca()
    ax.patch.set_alpha(0)

    quadrant_labels = []
    for r, s in zip(reach, sentiment):
        if r >= mean_reach and s >= mean_sentiment:
            quadrant_labels.append('KEY ALLIES')
        elif r < mean_reach and s >= mean_sentiment:
            quadrant_labels.append('POTENTIAL ADVOCATES')
        elif r >= mean_reach and s < mean_sentiment:
            quadrant_labels.append('HIGH-VISIBILITY NEUTRALS')
        else:
            quadrant_labels.append('LIMITED REACH NEUTRALS')

    color_map = {
        'KEY ALLIES': 'green',
        'POTENTIAL ADVOCATES': 'blue',
        'HIGH-VISIBILITY NEUTRALS': 'red',
        'LIMITED REACH NEUTRALS': 'gray'
    }
    plt.axvline(mean_reach, linestyle='--', linewidth=1)
    plt.axhline(mean_sentiment, linestyle='--', linewidth=1)
    for label, color in color_map.items():
        xs = [r for r, q in zip(reach, quadrant_labels) if q == label]
        ys = [s for s, q in zip(sentiment, quadrant_labels) if q == label]
        if xs:
            plt.scatter(xs, ys, s=40, c=color, label=label, edgecolors='k', linewidths=0.3)
    x_offset = (max(reach) - min(reach)) * 0.01 if reach else 0
    y_range = (max(sentiment) - min(sentiment)) if sentiment else 1
    y_offset = y_range * 0.02 if y_range else 0.5
    for i, name in enumerate(authors):
        plt.text(reach[i] + x_offset, sentiment[i] + y_offset, name, fontsize=6)
    plt.legend(title='Quadrants')
    ax.xaxis.set_major_formatter(FuncFormatter(format_reach))
    plt.xlabel("Reach")
    plt.ylabel("Sentiment Score")
    plt.tight_layout()
    return fig


def build_quadrant_figure_plotly(df):
    """Build interactive quadrant figure (Plotly). Returns a plotly Figure."""
    if not PLOTLY_AVAILABLE:
        raise ImportError("plotly is required. Install with: pip install plotly")
    df, err = prepare_quadrant_df(df)
    if err:
        raise ValueError(err)
    authors = df['Authors'].astype(str).tolist()
    reach = df['Reach'].tolist()
    sentiment = df['Sentiment Score'].tolist()
    mean_reach = np.mean(reach)
    mean_sentiment = np.mean(sentiment)

    quadrant_labels = []
    for r, s in zip(reach, sentiment):
        if r >= mean_reach and s >= mean_sentiment:
            quadrant_labels.append('KEY ALLIES')
        elif r < mean_reach and s >= mean_sentiment:
            quadrant_labels.append('POTENTIAL ADVOCATES')
        elif r >= mean_reach and s < mean_sentiment:
            quadrant_labels.append('HIGH-VISIBILITY NEUTRALS')
        else:
            quadrant_labels.append('LIMITED REACH NEUTRALS')

    color_map = {
        'KEY ALLIES': 'green',
        'POTENTIAL ADVOCATES': 'blue',
        'HIGH-VISIBILITY NEUTRALS': 'red',
        'LIMITED REACH NEUTRALS': 'gray'
    }

    fig = go.Figure()
    for label, color in color_map.items():
        mask = [q == label for q in quadrant_labels]
        if not any(mask):
            continue
        r_list = [r for r, m in zip(reach, mask) if m]
        s_list = [s for s, m in zip(sentiment, mask) if m]
        names = [a for a, m in zip(authors, mask) if m]
        fig.add_trace(go.Scatter(
            x=r_list,
            y=s_list,
            mode='markers+text',
            text=names,
            textposition='top center',
            textfont=dict(size=9, color='black'),
            name=label,
            marker=dict(size=10, color=color, line=dict(width=0.5, color='black')),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Reach: %{x:,.0f}<br>"
                "Sentiment: %{y:.2f}<br>"
                "Quadrant: " + label + "<extra></extra>"
            ),
            hoverlabel=dict(font_size=12),
        ))

    fig.add_vline(x=mean_reach, line_dash="dash", line_width=1, opacity=0.7)
    fig.add_hline(y=mean_sentiment, line_dash="dash", line_width=1, opacity=0.7)

    fig.update_layout(
        xaxis_title="Reach",
        yaxis_title="Sentiment Score",
        legend_title="Quadrants",
        showlegend=True,
        hovermode='closest',
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=600,
        margin=dict(t=40, b=40, l=60, r=80),
        xaxis=dict(tickformat=',.0f'),
    )
    return fig


if __name__ == '__main__':
    import sys
    _src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _src not in sys.path:
        sys.path.insert(0, _src)
    from helper import read_file
    csv_path = os.path.join(os.path.dirname(__file__), 'authors_quadrant.csv')
    if not os.path.isfile(csv_path):
        csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'quadrant_analysis_sample_files', 'quadrant_sample.csv')
    df = read_file(csv_path)
    fig = build_quadrant_figure(df)
    plt.savefig('authors_quadrant.png', dpi=300, transparent=True, bbox_inches='tight')
    plt.show()
