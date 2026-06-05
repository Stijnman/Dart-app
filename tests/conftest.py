"""
Pytest conftest for Dart-app.
Removes sys.path hack duplication from individual test_*.py files.
"""
import sys
import os
from pathlib import Path

# Ensure project root (parent of tests/) is on path for "from core..." imports
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
