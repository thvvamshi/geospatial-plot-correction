from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import geopandas as gpd
import pandas as pd

from bhume import load


VILLAGE_DIR = "data/vadnerbhairav"


# ============================================================
# Prediction File Resolver
# ============================================================

def get_prediction_file():

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
            "Run predictor.py first."
        )

        sys.exit(0)

    return files[0]


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

    village = load(
        VILLAGE_DIR
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

    prediction_file = (
        get_prediction_file()
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

    rows = []

    print()
    print("=" * 100)
    print("FAILURE ANALYSIS")
    print("=" * 100)

    for plot_id in truths.index:

        if plot_id not in predictions.index:

            continue

        pred = predictions.loc[
            plot_id
        ]

        confidence = pred.get(
            "confidence",
            None
        )

        if pd.isna(
            confidence
        ):

            continue

        pred_geom = pred[
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

        rows.append({

            "plot_number":
            plot_id,

            "iou":
            round(
                plot_iou,
                3
            ),

            "confidence":
            round(
                float(confidence),
                3
            ),

            "shift_distance":
            round(
                float(
                    pred.get(
                        "shift_distance",
                        0
                    )
                ),
                2
            ),

            "best_score":
            round(
                float(
                    pred.get(
                        "best_score",
                        0
                    )
                ),
                3
            ),

            "second_best":
            round(
                float(
                    pred.get(
                        "second_best",
                        0
                    )
                ),
                3
            ),

            "confidence_gap":
            round(
                float(
                    pred.get(
                        "confidence_gap",
                        0
                    )
                ),
                3
            )

        })

    df = pd.DataFrame(
        rows
    )

    df = df.sort_values(
        "confidence",
        ascending=False
    )

    print(
        df.to_string(
            index=False
        )
    )

    print()
    print("=" * 100)

    print(
        "\nHIGH CONFIDENCE FAILURES\n"
    )

    failures = df[

        (df["confidence"] >= 0.60)

        &

        (df["iou"] < 0.20)

    ]

    if len(failures) == 0:

        print(
            "No high-confidence failures."
        )

    else:

        print(
            failures.to_string(
                index=False
            )
        )

    print()

    print(
        "\nBEST PREDICTIONS\n"
    )

    best = df.sort_values(
        "iou",
        ascending=False
    )

    print(
        best.head(
            10
        ).to_string(
            index=False
        )
    )

    output_dir = Path(
        "outputs/debug"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir /
        "failure_analysis.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print()
    print(
        f"Saved: {output_file}"
    )