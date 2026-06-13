from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import inspect
from bhume import geo

print("\n=== _to_imagery_crs ===\n")
print(inspect.getsource(geo._to_imagery_crs))

print("\n=== _to_lonlat_crs ===\n")
print(inspect.getsource(geo._to_lonlat_crs))