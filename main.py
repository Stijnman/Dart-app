"""
Dart Game Pro v2.2 — Entry Point

Launch: streamlit run main.py
"""

import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import init_db, init_db_v2

if __name__ == "__main__":
    # Initialize databases
    init_db()
    init_db_v2()
    
    # Launch UI using Streamlit
    streamlit_app_path = os.path.join(os.path.dirname(__file__), "ui/streamlit_app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", streamlit_app_path])
