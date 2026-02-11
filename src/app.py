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
import pandas as pd

from quadrant import build_quadrant_figure_plotly
from sankey import build_sankey_figure

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
    if uploaded.name.lower().endswith(".csv"):
        encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]
        raw = uploaded.read()
        df = None
        for enc in encodings:
            try:
                df = pd.read_csv(io.BytesIO(raw), encoding=enc)
                break
            except Exception:
                continue
        if df is None:
            df = pd.read_csv(io.BytesIO(raw))
    else:
        df = pd.read_excel(uploaded)
except Exception as e:
    st.error(f"Could not read file: {e}")
    st.stop()

st.subheader("Data preview")
st.dataframe(df.head(20), width="stretch")

run = st.button("Run analysis")
if not run:
    st.stop()

with st.spinner("Running analysis…"):
    try:
        if analysis == "Quadrants":
            fig = build_quadrant_figure_plotly(df)
            st.subheader("Quadrant plot")
            st.plotly_chart(fig, width="stretch")
            try:
                png_buf = io.BytesIO()
                fig.write_image(png_buf, format="png", width=1200, height=600)
                png_buf.seek(0)
                st.download_button("Download PNG", data=png_buf, file_name="authors_quadrant.png", mime="image/png", key="quadrant_png")
            except Exception:
                st.caption("PNG download requires the kaleido package: pip install kaleido")
        else:
            fig = build_sankey_figure(df)
            st.subheader("Sankey diagram")
            st.plotly_chart(fig, width="stretch")
            try:
                png_buf = io.BytesIO()
                fig.write_image(png_buf, format="png", width=1200, height=800)
                png_buf.seek(0)
                st.download_button("Download PNG", data=png_buf, file_name="sankey_diagram.png", mime="image/png", key="sankey_png")
            except Exception:
                st.warning("PNG download requires the **kaleido** package. Install with: `pip install kaleido`")
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        raise
