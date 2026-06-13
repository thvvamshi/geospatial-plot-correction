from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from collections import Counter

import pandas as pd
import rasterio

from bhume import load

from alignment import (
    get_boundary_patch,
    align_plot
)

from confidence import (
    compute_confidence
)

VILLAGE_DIR = "data/vadnerbhairav"
SAMPLE_SIZE = 500


# ============================================================
# Area Classification
# ============================================================

def classify_area(area_ratio):

    if pd.isna(area_ratio):
        return "unknown"

    if 0.8 <= area_ratio <= 1.2:
        return "placement"

    if area_ratio < 0.5 or area_ratio > 2.0:
        return "area_error"

    return "uncertain"


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    village = load(VILLAGE_DIR)

    plots = village.plots.copy()

    plots["pot_kharaba_sqm"] = (
        plots["pot_kharaba_ha"]
        .fillna(0)
        * 10000
    )

    plots["expected_area_sqm"] = (
        plots["recorded_area_sqm"]
        .fillna(0)
        +
        plots["pot_kharaba_sqm"]
    )

    plots["area_ratio"] = (
        plots["map_area_sqm"]
        /
        plots["expected_area_sqm"]
        .replace(0, pd.NA)
    )

    predictions = []

    with rasterio.open(
        village.boundaries_path
    ) as src:

        for idx, (plot_id, row) in enumerate(
            plots.head(SAMPLE_SIZE).iterrows()
        ):

            try:

                area_ratio = row["area_ratio"]

                area_class = classify_area(
                    area_ratio
                )

                geom = village.plot(
                    plot_id
                )

                # ------------------------------------
                # Conservative Flagging
                # ------------------------------------

                if area_class in [
                    "area_error",
                    "uncertain",
                    "unknown"
                ]:

                    predictions.append({

                        "plot_number":
                        str(plot_id),

                        "status":
                        "flagged",

                        "confidence":
                        None,

                        "area_class":
                        area_class,

                        "shift_distance":
                        None
                    })

                    continue

                # Alignment
                (
                    boundary_img,
                    transform,
                    geom_img
                ) = get_boundary_patch(
                    src,
                    geom
                )

                result = align_plot(
                    boundary_img,
                    geom_img,
                    transform
                )

                confidence = compute_confidence(
                    shift_distance=result[
                        "shift_distance"
                    ],
                    area_ratio=float(
                        area_ratio
                    ),
                    confidence_gap=result[
                        "confidence_gap"
                    ]
                )

                status = (
                    "corrected"
                    if confidence >= 0.55
                    else "flagged"
                )

                predictions.append({

                    "plot_number":
                    str(plot_id),

                    "status":
                    status,

                    "confidence":
                    confidence,

                    "area_class":
                    area_class,

                    "shift_distance":
                    result[
                        "shift_distance"
                    ]
                })

                if idx % 100 == 0:

                    print(
                        f"{plot_id} | "
                        f"{area_class} | "
                        f"shift={result['shift_distance']:.1f}m | "
                        f"conf={confidence:.3f} | "
                        f"{status}"
                    )

            except Exception as e:

                predictions.append({

                    "plot_number":
                    str(plot_id),

                    "status":
                    "flagged",

                    "confidence":
                    None,

                    "area_class":
                    "error",

                    "shift_distance":
                    None
                })

    # Summary
    counts = Counter(
        p["status"]
        for p in predictions
    )

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(
        f"Total plots: {len(predictions)}"
    )

    print(
        f"Corrected: {counts['corrected']}"
    )

    print(
        f"Flagged: {counts['flagged']}"
    )

    print()
    print("AREA CLASSES")

    area_counts = Counter(
        p["area_class"]
        for p in predictions
    )

    for k, v in sorted(
        area_counts.items()
    ):

        print(
            f"{k:<15} {v}"
        )

    confs = [

        p["confidence"]

        for p in predictions

        if p["confidence"] is not None
    ]

    if confs:

        print()
        print("CONFIDENCE")

        print(
            f"min={min(confs):.3f}"
        )

        print(
            f"max={max(confs):.3f}"
        )

        print(
            f"mean={sum(confs)/len(confs):.3f}"
        )

        # Confidence Buckets
        bins = [
            0.0,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
            1.0
        ]

        conf_df = pd.DataFrame({

            "confidence":
            confs

        })

        print()
        print("CONFIDENCE BUCKETS")

        bucket_counts = (
            pd.cut(
                conf_df["confidence"],
                bins=bins
            )
            .value_counts()
            .sort_index()
        )

        print(bucket_counts)

        print()
        print(
            f"Average Confidence: "
            f"{conf_df['confidence'].mean():.3f}"
        )

        print(
            f"Median Confidence: "
            f"{conf_df['confidence'].median():.3f}"
        )