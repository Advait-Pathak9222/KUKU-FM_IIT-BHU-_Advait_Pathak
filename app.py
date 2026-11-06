"""
Root launcher for NyayaMitra Streamlit Dashboard.
Run using:
    streamlit run app.py
"""
import sys
from pathlib import Path

# Ensure root is on PYTHONPATH
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Execute frontend app
from frontend.app import *
