"""
Streamlit UI: upload CSV or Excel (.xlsx), pick Quadrants or Sankey, run and view outputs.
"""
import io
import os
import sys

# Ensure src is on path when run as streamlit run src/app.py
_src_dir = os.path.dirname(os.path.abspath(__file__))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import streamlit as st

from chart_creation import build_quadrant_figure_plotly, build_sankey_figure
from helper import read_uploaded_file
from writeups_generation import generate_writeups

st.set_page_config(page_title="Top Contributors Analysis", layout="wide")
st.title("Top Contributors Analysis")
st.caption("Upload a CSV or Excel (.xlsx) file and run Quadrant Analysis or Sankey Diagram.")

analysis = st.radio(
    "Choose analysis",
    ["Quadrants", "Sankey"],
    horizontal=True,
    help="Quadrants: Authors × Reach × Sentiment. Sankey: Authors × theme contributions.",
)

uploaded = st.file_uploader(
    "Upload data file",
    type=["csv", "xlsx"],
    help="Upload CSV or Excel (.xlsx). Quadrants: columns like Authors, Reach, Sentiment Score. "
         "Sankey: Authors and theme columns (e.g. Financial Performance & Economic Outlook, ...).",
)

if not uploaded:
    st.info("Upload a file to run the selected analysis.")
    st.stop()

try:
    df = read_uploaded_file(uploaded)
except Exception as e:
    st.error(f"Could not read file: {e}")
    st.stop()

st.subheader("Data preview")
st.dataframe(df.head(20), width="stretch")

run = st.button("Run analysis", type="primary", key="run_analysis")
if not run:
    st.stop()

# Single run: progress bar, then chart, then writeups (all in one go)
progress = st.progress(0, text="Starting…")
status = st.empty()

try:
    # Step 1: Build chart (no PNG export here - it can hang)
    progress.progress(15, text="Building chart…")
    if analysis == "Quadrants":
        fig = build_quadrant_figure_plotly(df)
    else:
        fig = build_sankey_figure(df)

    # Show chart right away (st.plotly_chart only; PNG export moved to end)
    st.subheader("Quadrant plot" if analysis == "Quadrants" else "Sankey diagram")
    st.plotly_chart(fig, width="stretch")

    # Step 2: Generate writeups (uses same df from uploaded CSV)
    progress.progress(50, text="Generating writeups…")
    analysis_type = "quadrant" if analysis == "Quadrants" else "sankey"
    writeups = generate_writeups(df, analysis_type=analysis_type)
    writeups = (writeups or "").strip()

    progress.progress(100, text="Done")
    status.empty()
    progress.empty()

    st.subheader("Sample writeups")
    if writeups:
        st.markdown(writeups)
    else:
        st.caption("(No content returned)")

    # Optional PNG download (after everything else so it doesn't block; can be slow)
    try:
        png_buf = io.BytesIO()
        fig.write_image(png_buf, format="png", width=1200, height=600 if analysis == "Quadrants" else 800)
        png_buf.seek(0)
        fname = "authors_quadrant.png" if analysis == "Quadrants" else "sankey_diagram.png"
        st.download_button("Download PNG", data=png_buf, file_name=fname, mime="image/png", key="dl_png")
    except Exception:
        st.caption("PNG download requires: pip install kaleido")

except ValueError as e:
    progress.empty()
    status.empty()
    st.error(str(e))
except Exception as e:
    progress.empty()
    status.empty()
    st.error(f"Analysis failed: {e}")
    raise
