"""
Test script for generate_writeups. Run from project root:
  python test_writeups.py
Prints the full writeups result to the terminal.
"""
import os
import sys

# Run from project root so src and myenv are available
_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(_root)
sys.path.insert(0, os.path.join(_root, "src"))

import pandas as pd
from writeups_generation import generate_writeups


def make_sample_df():
    """Minimal sample dataframe for testing writeups."""
    return pd.DataFrame({
        "Authors": ["Contributor A", "Contributor B", "Contributor C"],
        "Reach": [1200, 800, 500],
        "Sentiment Score": [0.6, -0.2, 0.1],
        "Financial Performance & Economic Outlook": [0.8, 0.3, 0.5],
        "Sustainability & Social Impact": [0.2, 0.7, 0.4],
        "Coverage_Level": ["High", "Medium", "Low"],
    })


def main():
    print("Building sample dataframe...")
    df = make_sample_df()
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print()

    print("Calling generate_writeups (this may take 15–30 seconds)...")
    try:
        result = generate_writeups(df, max_sample_rows=10)
        result = (result or "").strip()
        print()
        print("=" * 60)
        print("WRITEUPS RESULT")
        print("=" * 60)
        print(result if result else "(empty)")
        print("=" * 60)
        print(f"Length: {len(result)} chars")
    except ValueError as e:
        print("Error (config):", e)
        sys.exit(1)
    except Exception as e:
        print("Error:", type(e).__name__, e)
        sys.exit(1)


if __name__ == "__main__":
    main()
