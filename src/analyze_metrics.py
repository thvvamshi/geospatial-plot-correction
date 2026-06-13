from pathlib import Path
import pandas as pd

df = pd.read_csv(
    "outputs/debug/alignment_validation.csv"
)

print("\nALL RESULTS")
print("=" * 80)

print(
    df[[
        "plot_number",
        "shift_distance",
        "confidence",
        "iou"
    ]].sort_values(
        "shift_distance"
    )
)

df["good"] = df["iou"] >= 0.5

print("\nGOOD VS BAD")
print("=" * 80)

print(
    df.groupby("good")[
        "shift_distance"
    ].agg(
        ["count", "mean", "min", "max"]
    )
)

print("\nCORRELATION")
print("=" * 80)

print(
    df[[
        "shift_distance",
        "iou"
    ]].corr()
)