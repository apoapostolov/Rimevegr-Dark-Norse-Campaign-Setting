"""conftest.py — add scripts/ to sys.path so test files can import combat modules."""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))
