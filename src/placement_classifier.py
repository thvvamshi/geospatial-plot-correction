from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bhume import load

# Load Village
VILLAGE_DIR = "data/vadnerbhairav"

village = load(VILLAGE_DIR)

df = village.plots.copy()

# Area Features
df["pot_kharaba_sqm"] = (
    df["pot_kharaba_ha"]
    .fillna(0)
    * 10000
)

df["expected_area_sqm"] = (
    df["recorded_area_sqm"].fillna(0)
    + df["pot_kharaba_sqm"]
)

df["area_ratio"] = (
    df["map_area_sqm"]
    / df["expected_area_sqm"].replace(0, np.nan)
)

# Classification
def classify_plot(area_ratio: float) -> str:

    if pd.isna(area_ratio):
        return "unknown"

    # Strong placement candidate
    if 0.80 <= area_ratio <= 1.20:
        return "placement"

    # Strong area mismatch
    if area_ratio < 0.60 or area_ratio > 1.50:
        return "area_error"

    # Everything else
    return "uncertain"


df["classification"] = df["area_ratio"].apply(classify_plot)

# summary 
print("=" * 80)
print("AREA RATIO STATISTICS")
print("=" * 80)

print(df["area_ratio"].astype(float).describe())

print()

print("=" * 80)
print("CLASSIFICATION COUNTS")
print("=" * 80)

print(df["classification"].value_counts())

# move to top 20 area-error candidates
print()
print("=" * 80)
print("TOP 20 AREA-ERROR CANDIDATES")
print("=" * 80)

print(
    df.sort_values(
        "area_ratio",
        ascending=False
    )[[
        "plot_number",
        "map_area_sqm",
        "recorded_area_sqm",
        "pot_kharaba_sqm",
        "expected_area_sqm",
        "area_ratio",
        "classification"
    ]].head(20)
)

print()
print("=" * 80)
print("TOP 20 LOWEST AREA RATIOS")
print("=" * 80)

print(
    df.sort_values(
        "area_ratio",
        ascending=True
    )[[
        "plot_number",
        "map_area_sqm",
        "recorded_area_sqm",
        "pot_kharaba_sqm",
        "expected_area_sqm",
        "area_ratio",
        "classification"
    ]].head(20)
)
# save to CSV
OUTPUT_DIR = Path("outputs/debug")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_file = OUTPUT_DIR / "plot_area_analysis.csv"

df[[
    "plot_number",
    "map_area_sqm",
    "recorded_area_sqm",
    "pot_kharaba_sqm",
    "expected_area_sqm",
    "area_ratio",
    "classification"
]].to_csv(output_file, index=False)

print()
print(f"Saved analysis -> {output_file}")