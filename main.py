"""
Dart Game Pro v2.0 — Entry Point

Launch the Streamlit app:
    streamlit run main.py

Run tests:
    pytest tests/ -v
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.streamlit_app import main

if __name__ == "__main__":
    main()
