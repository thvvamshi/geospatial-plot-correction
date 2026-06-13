from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bhume import load

village = load("data/vadnerbhairav")

print("=" * 80)
print("COLUMNS")
print("=" * 80)

for col in village.plots.columns:
    print(col)

print("\n" + "=" * 80)
print("SAMPLE ROWS")
print("=" * 80)

print(village.plots.head(3))

print("\n" + "=" * 80)
print("INFO")
print("=" * 80)

print(village.plots.info())