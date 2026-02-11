"""
Entry point: run the Streamlit app.
Usage: python main.py
"""
import os
import sys

if __name__ == "__main__":
    root = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(root, "src", "app.py")
    if not os.path.isfile(app_path):
        sys.exit(f"App not found: {app_path}")
    os.chdir(root)
    from streamlit.web import cli as st_cli
    st_cli.main_run(["src/app.py"])
