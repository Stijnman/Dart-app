"""
Dart Game Pro v2.4 — Main Entry Point
Refactored: Direct Streamlit entry, no subprocess, proper error handling, v2.4.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """Main entry point."""
    try:
        # Initialize databases
        from core.database import init_db, migrate_db
        from core.database_v2 import init_db_v2, migrate_db_v2

        print("🎯 Dart Game Pro v2.4")
        print("Initializing databases...")

        init_db()
        migrate_db()
        init_db_v2()
        migrate_db_v2()

        print("✅ Databases ready!")
        print("Starting Streamlit app...")

        # Import and run the Streamlit app directly
        # This avoids the subprocess fragility of v2.3
        import streamlit.web.bootstrap as bootstrap
        from streamlit.web.bootstrap import run

        streamlit_app_path = str(PROJECT_ROOT / "ui" / "streamlit_app.py")

        # Run Streamlit
        sys.argv = ["streamlit", "run", streamlit_app_path, "--server.headless", "true"]
        bootstrap.run(
            main_script_path=streamlit_app_path,
            command_line="",
            args=[],
            flag_options={},
        )

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
