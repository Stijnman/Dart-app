"""
Dart Game Pro v2.2 — Entry Point

Launch: streamlit run main.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import init_db, init_db_v2
from ui.streamlit_app import main

if __name__ == "__main__":
    # Initialize databases
    init_db()
    init_db_v2()
    
    # Launch UI
    main()
