import os
import sys
from pathlib import Path

# config.py reads the database URL when it's first imported, so this has to run
# before any test module imports acp_app. An in-memory SQLite DB is enough for
# tests that don't touch tables.
os.environ.setdefault('TEST_DATABASE_URL', 'sqlite://')

# The Aspen API tests reuse mfgkit's fake IP21 connection (tests/test_aspen.py)
# from the sibling mfgkit checkout
_mfgkit = Path(__file__).resolve().parents[2] / 'mfgkit'
for path in (_mfgkit, _mfgkit / 'tests'):
    if path.is_dir() and str(path) not in sys.path:
        sys.path.append(str(path))
