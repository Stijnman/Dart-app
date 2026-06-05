"""
Dart Game Pro v3.0 — Main Entry Point
Major release: Sublime UI overhaul, full Custom Game Mode system, rich Analytics, Practice Drills, multiplayer lobby, achievements, exports & more.
"""

import sys
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

        # Import and run the Streamlit app directly via CLI entry
        # (stable across Streamlit versions; avoids private bootstrap API changes)
        streamlit_app_path = str(PROJECT_ROOT / "ui" / "streamlit_app.py")

        # Set argv so streamlit CLI picks up our flags (headless for servers, etc.)
        sys.argv = [
            "streamlit",
            "run",
            streamlit_app_path,
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false",
        ]
        import streamlit.web.cli as stcli

        sys.exit(stcli.main())

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
