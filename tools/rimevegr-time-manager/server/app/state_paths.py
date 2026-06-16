from __future__ import annotations

from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
SERVER_DIR = APP_DIR.parent
TOOL_DIR = SERVER_DIR.parent
PROJECT_DIR = TOOL_DIR.parent.parent
DATA_DIR = PROJECT_DIR / "data"
SCRIPTS_DIR = PROJECT_DIR / "scripts"
STATE_DIR = TOOL_DIR / "state"
SNAPSHOTS_DIR = STATE_DIR / "snapshots"
TRANSACTIONS_DIR = STATE_DIR / "transactions"
EXPORTS_DIR = STATE_DIR / "exports"
