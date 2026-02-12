import pandas as pd
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

from collections import defaultdict

AUTHOR_COL = "Authors"
THEME_COLS = [
    "Financial Performance & Economic Outlook",
    "Digitalization & Innovation",
    "Sustainability & Social Impact",
    "Corporate Reputation & Leadership",
]


def _detect_theme_columns(df):
    """Return list of theme-like columns (Authors excluded). Prefer THEME_COLS if present."""
    df.columns = [str(c).strip() for c in df.columns]
    author_col = None
    for c in df.columns:
        if str(c).strip().lower() == 'authors':
            author_col = c
            break
    if author_col is None and len(df.columns) > 0:
        author_col = df.columns[0]
    found = [c for c in THEME_COLS if c in df.columns]
    if found:
        return author_col, found
    theme_cols = []
    for c in df.columns:
        if c == author_col:
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            theme_cols.append(c)
    return author_col, theme_cols if theme_cols else list(df.columns.drop(author_col))


def build_sankey_figure(df):
    """
    Build Sankey diagram from a DataFrame with Authors and theme contribution columns.
    Returns a plotly Figure.
    """
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    author_col, theme_cols = _detect_theme_columns(df)
    if not theme_cols:
        raise ValueError(
            "Need an 'Authors' column and at least one numeric theme column."
        )
    if author_col not in df.columns:
        df = df.rename(columns={df.columns[0]: author_col})
    for tc in theme_cols:
        if tc in df.columns:
            df[tc] = pd.to_numeric(df[tc], errors='coerce').fillna(0)

    grouped = df.groupby(author_col)[theme_cols].sum()
    author_sums = grouped.sum(axis=1)
    authors = author_sums.sort_values(ascending=False).index.tolist()
    themes = theme_cols.copy()
    nodes = authors + themes
    node_index = {name: i for i, name in enumerate(nodes)}

    sources = []
    targets = []
    values = []
    for _, row in df.iterrows():
        author = row[author_col]
        for theme in theme_cols:
            count = row[theme]
            if count > 0:
                sources.append(node_index[author])
                targets.append(node_index[theme])
                values.append(count)

    total_flow = sum(values) if values else 0
    source_totals = defaultdict(int)
    for s, v in zip(sources, values):
        source_totals[s] += v
    link_percent_source = []
    link_percent_total = []
    link_labels = []
    for s, v in zip(sources, values):
        p_src = (v / source_totals[s] * 100) if source_totals[s] else 0
        p_tot = (v / total_flow * 100) if total_flow else 0
        link_percent_source.append(p_src)
        link_percent_total.append(p_tot)
        link_labels.append(f"{v} ({p_src:.1f}%)")

    theme_colors = ["#FF5733", "#33A1FF", "#8E44AD", "#27AE60"]
    author_color = "#4C72B0"
    node_colors = [author_color] * len(authors) + theme_colors[: len(themes)]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=25,
            thickness=25,
            line=dict(color="black", width=0.5),
            label=nodes,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            label=link_labels,
            color="rgba(0, 0, 0, 0.3)",
            customdata=[[ps, pt] for ps, pt in zip(link_percent_source, link_percent_total)],
            hovertemplate=(
                "Value: %{value}<br>Percent of source: %{customdata[0]:.1f}%<br>"
                "Percent of total: %{customdata[1]:.1f}%<extra></extra>"
            )
        )
    )])
    fig.update_layout(
        font_size=14,
        height=800,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="black", size=14)
    )

    theme_totals = df[theme_cols].sum()
    author_totals = author_sums.to_dict()
    overall_total = total_flow if total_flow else theme_totals.sum()
    node_labels = []
    for author in authors:
        val = author_totals.get(author, 0)
        pct = (val / overall_total * 100) if overall_total else 0
        node_labels.append(f"{author}\n{val} ({pct:.1f}%)")
    for theme in themes:
        val = int(theme_totals.get(theme, 0))
        pct = (val / overall_total * 100) if overall_total else 0
        node_labels.append(f"{theme}\n{val} ({pct:.1f}%)")
    fig.data[0].node.label = node_labels
    return fig


if __name__ == '__main__':
    import os
    import sys
    _src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _src not in sys.path:
        sys.path.insert(0, _src)
    from helper import read_file
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sankey_diagram_sample_files', 'authors_themes.csv')
    if not os.path.isfile(path):
        path = path.replace('.csv', '.xlsx')
    df = read_file(path)
    fig = build_sankey_figure(df)
    fig.write_image("sankey_diagram.png", width=1200, height=800)
    print("Saved sankey_diagram.png")
