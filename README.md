# Top Contributors Analysis

Streamlit app to run **Quadrant Analysis** (Authors × Reach × Sentiment) and **Sankey Diagram** (Authors × theme contributions). Upload CSV or Excel, pick an analysis, view interactive charts, and download PNGs.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Then open the URL shown (e.g. http://localhost:8501).

## Data

- **Quadrants:** CSV/Excel with columns for **Authors**, **Reach**, and **Sentiment** (names can contain those words).
- **Sankey:** CSV/Excel with **Authors** and numeric theme columns (e.g. the four research themes, or any numeric columns).

Sample files are in `data/` (quadrant and sankey subfolders).

## Project structure

```
Top_Contributors/
  README.md
  requirements.txt
  main.py              # Entry point: runs Streamlit app
  data/                 # Sample data (optional)
  src/
    __init__.py
    app.py              # Streamlit UI
    quadrant.py         # Quadrant analysis (matplotlib + Plotly)
    sankey.py           # Sankey diagram (Plotly)
```
