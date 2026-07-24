"""
Dart Game Pro v3.1 — Main Entry Point
Real-time WS multiplayer + ELO + custom online, PWA/mobile, AI coach, streaming. Sublime v3.0 base preserved + enhanced.

Supports two execution modes:
1. `python main.py`         — local launcher: init databases, then start Streamlit.
2. `streamlit run main.py`  — cloud/hosted mode (e.g. Streamlit Community Cloud):
   already inside a Streamlit runtime, so just init databases and run the app inline.
"""

import sys
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def _init_databases():
    """Initialize and migrate all databases."""
    from core.database import init_db, migrate_db
    from core.database_v2 import init_db_v2, migrate_db_v2

    print("🎯 Dart Game Pro v3.1")
    print("Initializing databases...")

    init_db()
    migrate_db()
    init_db_v2()
    migrate_db_v2()

    print("✅ Databases ready!")


def _running_inside_streamlit() -> bool:
    """Detect whether this script is already being executed by `streamlit run`."""
    try:
        from streamlit.runtime import exists as _runtime_exists
        return _runtime_exists()
    except Exception:
        return False


def _run_app_inline():
    """Run the Streamlit app inline (used when executed via `streamlit run main.py`)."""
    _init_databases()
    import runpy
    runpy.run_path(str(PROJECT_ROOT / "ui" / "streamlit_app.py"), run_name="__main__")


def main():
    """Local launcher entry point (python main.py)."""
    try:
        _init_databases()
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


if _running_inside_streamlit():
    # Executed via `streamlit run main.py` (e.g. Streamlit Community Cloud)
    _run_app_inline()
elif __name__ == "__main__":
    main()
