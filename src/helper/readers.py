"""
CSV and Excel file readers for uploaded data and local paths.
"""
import io
from pathlib import Path
from typing import Union

import pandas as pd

# Encodings to try for CSV (in order)
CSV_ENCODINGS = ["utf-8", "utf-8-sig", "cp1252", "latin1"]


def read_csv(file_or_bytes: Union[bytes, io.BytesIO]) -> pd.DataFrame:
    """
    Read a CSV from raw bytes or a file-like object.
    Tries multiple encodings; falls back to default if none succeed.
    """
    if isinstance(file_or_bytes, bytes):
        file_or_bytes = io.BytesIO(file_or_bytes)
    df = None
    raw = file_or_bytes.read()
    file_or_bytes.seek(0)
    for enc in CSV_ENCODINGS:
        try:
            df = pd.read_csv(io.BytesIO(raw), encoding=enc)
            break
        except Exception:
            continue
    if df is None:
        df = pd.read_csv(io.BytesIO(raw))
    return df


def read_excel(file_or_path) -> pd.DataFrame:
    """
    Read an Excel file (.xlsx). Accepts file-like object or path.
    """
    return pd.read_excel(file_or_path)


def read_file(path: Union[str, Path]) -> pd.DataFrame:
    """
    Read a local file by path. Dispatches to read_csv or read_excel by extension.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return read_csv(path.read_bytes())
    if suffix in (".xlsx", ".xls"):
        return read_excel(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def read_uploaded_file(uploaded) -> pd.DataFrame:
    """
    Read an uploaded file (Streamlit UploadedFile or similar).
    Dispatches to read_csv or read_excel by filename extension.
    """
    name = (uploaded.name or "").lower()
    if name.endswith(".csv"):
        raw = uploaded.read()
        uploaded.seek(0)
        return read_csv(raw)
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return read_excel(uploaded)
    raise ValueError(f"Unsupported file type: {uploaded.name}")
