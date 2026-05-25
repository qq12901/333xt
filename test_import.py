#!/usr/bin/env python
import sys
from pathlib import Path

print("=" * 60)
print("Testing imports")
print("=" * 60)

# Path setup
project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"Project root: {project_root}")
print(f"sys.path: {sys.path[:3]}")
print()

# Check directory structure
print("Directory structure:")
print([p.name for p in project_root.iterdir()])
print()

print("src directory contents:")
src_dir = project_root / "src"
if src_dir.exists():
    print([p.name for p in src_dir.iterdir()])
print()

# Test importing
print("Testing imports...")
print()

try:
    import src
    print("✅ src package imported")
    print(f"  src path: {src.__file__}")
except Exception as e:
    print(f"❌ src import failed: {e}")
    import traceback
    print(traceback.format_exc())

print()

try:
    from src import main
    print("✅ src.main imported")
except Exception as e:
    print(f"❌ src.main import failed: {e}")
    import traceback
    print(traceback.format_exc())

print()

try:
    from src.main import TradingSystem
    print("✅ TradingSystem imported")
except Exception as e:
    print(f"❌ TradingSystem import failed: {e}")
    import traceback
    print(traceback.format_exc())

print()

print("=" * 60)
