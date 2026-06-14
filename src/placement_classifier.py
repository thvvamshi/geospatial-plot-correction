from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bhume import load


# Village Inference
def infer_village(prediction_file):

    prediction_name = (
        prediction_file.stem.lower()
    )

    if "malatavadi" in prediction_name:
        return "data/malatavadi"

    if "vadnerbhairav" in prediction_name:
        return "data/vadnerbhairav"

    raise ValueError(
        f"Cannot infer village from "
        f"{prediction_name}"
    )


# Prediction File Resolver
def get_prediction_file():

    if len(sys.argv) > 1:

        prediction_file = Path(
            sys.argv[1]
        )

        if not prediction_file.exists():

            print(
                f"\nERROR: File not found:\n"
                f"{prediction_file}"
            )

            sys.exit(1)

        return prediction_file

    prediction_dir = Path(
        "outputs/predictions"
    )

    files = sorted(
        prediction_dir.glob(
            "*.geojson"
        )
    )

    if len(files) == 0:

        print(
            "\nNo prediction files found."
        )

        print(
            "\nGenerate predictions first:"
        )

        print(
            "python src\\predictor.py"
        )

        sys.exit(0)

    if len(files) == 1:

        return files[0]

    print("\nAvailable prediction files:\n")

    for idx, file in enumerate(files):

        print(
            f"{idx + 1}. {file.name}"
        )

    while True:

        try:

            choice = int(
                input(
                    "\nSelect file: "
                )
            )

            if (
                1 <= choice <= len(files)
            ):

                return files[
                    choice - 1
                ]

        except Exception:

            pass

        print(
            "Invalid selection."
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


# Main
if __name__ == "__main__":

    prediction_file = (
        get_prediction_file()
    )

    village = load(
        infer_village(
            prediction_file
        )
    )

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

    df["classification"] = (
        df["area_ratio"].apply(classify_plot)
    )

    # Summary
    print("=" * 80)
    print("AREA RATIO STATISTICS")
    print("=" * 80)

    print(df["area_ratio"].astype(float).describe())

    print()

    print("=" * 80)
    print("CLASSIFICATION COUNTS")
    print("=" * 80)

    print(df["classification"].value_counts())

    # Top 20 area-error candidates
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

    # Save to CSV
    OUTPUT_DIR = Path("outputs/debug")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = (
        OUTPUT_DIR / "plot_area_analysis.csv"
    )

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