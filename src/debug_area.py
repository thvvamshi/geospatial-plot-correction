# src/debug_area.py

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bhume import load

village = load("data/vadnerbhairav")

cols = [
    "plot_number",
    "map_area_sqm",
    "recorded_area_sqm",
    "recorded_area_ha",
    "pot_kharaba_ha"
]

print(village.plots[cols].head(20))