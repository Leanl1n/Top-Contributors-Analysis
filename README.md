# Top Contributors Analysis

Streamlit app for **Quadrant Analysis** (Authors × Reach × Sentiment) and **Sankey Diagram** (Authors × theme contributions). Upload a CSV or Excel file, pick an analysis type, then run analysis to view an interactive chart and AI-generated writeups.

## Features

- **Quadrant chart** — Plot authors by Reach and Sentiment (Key Allies, Potential Advocates, High-Visibility Neutrals, Limited Reach Neutrals).
- **Sankey diagram** — Flow of author contributions across themes (e.g. Financial Performance, Sustainability, etc.).
- **Writeups** — DeepSeek-generated analysis text; prompts are in JSON (separate prompt for quadrant vs sankey).

## Setup

```bash
pip install -r requirements.txt
```

For writeups generation, set your DeepSeek API key:

- In a `myenv/.env` file: `DEEPSEEK_API_KEY=your_key`
- Or as an environment variable: `DEEPSEEK_API_KEY`

## Run

```bash
python main.py
```

Then open the URL shown in the terminal (e.g. http://localhost:8501).

## Data

- **Quadrants:** CSV or Excel with columns for **Authors**, **Reach**, and **Sentiment** (column names can contain those words).
- **Sankey:** CSV or Excel with **Authors** and numeric theme columns (e.g. the four research themes, or any numeric columns).

Sample data can be placed in `data/` (e.g. quadrant and sankey subfolders).

## Writeups prompts

Prompts for the AI writeups live in **`src/writeups_generation/prompts.json`**:

- **`sankey`** — Thematic coverage, main contributors, and “worth mentioning” (themes, articles, examples).
- **`quadrant`** — Reach/sentiment summary, quadrant placement, implications, and “worth mentioning.”

Edit the JSON to change the instructions for each analysis type.

## Project structure

```
Top-Contributors-Analysis/
  README.md
  requirements.txt
  main.py                    # Entry point: runs Streamlit app
  test_writeups.py           # Test script: run writeups from sample data (prints to terminal)
  src/
    app.py                   # Streamlit UI
    chart_creation/          # Quadrant and Sankey charts
      __init__.py
      quadrant.py
      sankey.py
    helper/
      __init__.py
      readers.py             # CSV/Excel file reading
    service/
      __init__.py
      deepseek.py            # DeepSeek API client
    writeups_generation/     # AI writeups from dataframe
      __init__.py
      chat_completion.py     # generate_writeups(), loads prompts.json
      prompts.json           # sankey and quadrant prompts
```

## Test writeups (terminal)

To test the writeups pipeline without the UI:

```bash
python test_writeups.py
```

Uses a small sample dataframe and prints the generated writeups to the terminal. Requires `DEEPSEEK_API_KEY` (e.g. via `myenv/.env`).
