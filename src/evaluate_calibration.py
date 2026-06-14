from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import geopandas as gpd

from bhume import load


# ============================================================
# Village Inference
# ============================================================

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


# ============================================================
# Prediction File Resolver
# ============================================================

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

        print()
        print("=" * 60)
        print("CALIBRATION REPORT")
        print("=" * 60)

        print(
            "\nNo prediction files found."
        )

        print(
            "\nGenerate predictions first:"
        )

        print(
            "python src/generate_predictions.py"
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


# ============================================================
# IoU
# ============================================================

def iou(poly1, poly2):

    inter = (
        poly1
        .intersection(poly2)
        .area
    )

    union = (
        poly1
        .union(poly2)
        .area
    )

    if union == 0:

        return 0.0

    return inter / union


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    prediction_file = (
        get_prediction_file()
    )

    village = load(
        infer_village(
            prediction_file
        )
    )

    truths = (
        village
        .example_truths
        .copy()
    )

    truths.index = (
        truths.index
        .astype(str)
    )

    predictions = gpd.read_file(
        prediction_file
    )

    predictions["plot_number"] = (
        predictions["plot_number"]
        .astype(str)
    )

    predictions = predictions.set_index(
        "plot_number"
    )

    results = []

    print()
    print("=" * 60)
    print("CALIBRATION REPORT")
    print("=" * 60)

    print(
        f"\nPrediction File:\n"
        f"{prediction_file}\n"
    )

    for plot_id in truths.index:

        if plot_id not in predictions.index:

            print(
                f"Missing prediction: "
                f"{plot_id}"
            )

            continue

        pred_row = predictions.loc[
            plot_id
        ]

        confidence = pred_row[
            "confidence"
        ]

        if pd.isna(
            confidence
        ):

            continue

        pred_geom = pred_row[
            "geometry"
        ]

        truth_geom = truths.loc[
            plot_id,
            "geometry"
        ]

        plot_iou = iou(
            pred_geom,
            truth_geom
        )

        results.append({

            "plot_number":
            plot_id,

            "confidence":
            float(confidence),

            "iou":
            float(plot_iou)

        })

        print(
            f"{plot_id:>6} | "
            f"IoU={plot_iou:.3f} | "
            f"Conf={confidence:.3f}"
        )

    if len(results) == 0:

        print(
            "\nNo overlapping truth "
            "and prediction records."
        )

        sys.exit(0)

    df = pd.DataFrame(
        results
    )

    print()
    print("SORTED BY CONFIDENCE")
    print(
        df.sort_values(
            "confidence",
            ascending=False
        )
    )
    print()

    print()
    print("=" * 60)

    mean_iou = df[
        "iou"
    ].mean()

    mean_conf = df[
        "confidence"
    ].mean()

    if len(df) >= 2:

        correlation = np.corrcoef(
            df["confidence"],
            df["iou"]
        )[0, 1]

    else:

        correlation = np.nan

    print(
        f"Truth Plots: "
        f"{len(df)}"
    )

    print(
        f"Mean IoU: "
        f"{mean_iou:.3f}"
    )

    print(
        f"Mean Confidence: "
        f"{mean_conf:.3f}"
    )

    print(
        f"Correlation: "
        f"{correlation:.3f}"
    )

    print()

    if np.isnan(
        correlation
    ):

        rating = "INSUFFICIENT_DATA"

    elif correlation >= 0.80:

        rating = "EXCELLENT"

    elif correlation >= 0.60:

        rating = "GOOD"

    elif correlation >= 0.40:

        rating = "MODERATE"

    else:

        rating = "POOR"

    print(
        f"Calibration: "
        f"{rating}"
    )

    print("=" * 60)

    # ========================================================
    # Save Results
    # ========================================================

    output_dir = Path(
        "outputs/debug"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir /
        "calibration_results.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print()

    print(
        f"Saved: {output_file}"
    )