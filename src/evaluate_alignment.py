from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

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

from bhume.geo import _to_lonlat_crs

from shapely.ops import transform as shp_transform

village_name = (
    sys.argv[1]
    if len(sys.argv) > 1
    else "vadnerbhairav"
)

village = load(
    f"data/{village_name}"
)

# ============================================================
# IoU
# ============================================================

def iou(poly1, poly2):

    inter = poly1.intersection(
        poly2
    ).area

    union = poly1.union(
        poly2
    ).area

    if union == 0:
        return 0.0

    return inter / union


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    truth = village.example_truths

    rows = []

    with rasterio.open(
        village.boundaries_path
    ) as src:

        tf = _to_lonlat_crs(
            src
        )

        for plot_id in truth.index:

            try:

                official_geom = village.plot(
                    plot_id
                )

                (
                    boundary_img,
                    transform,
                    geom_img
                ) = get_boundary_patch(
                    src,
                    official_geom
                )

                # ----------------------------------
                # Alignment
                # ----------------------------------

                result = align_plot(
                    boundary_img,
                    geom_img,
                    transform
                )

                dx = result["dx"]
                dy = result["dy"]

                shift_distance = result[
                    "shift_distance"
                ]

                best_score = result[
                    "best_score"
                ]

                shifted_geom_img = result[
                    "shifted_geom"
                ]

                # ----------------------------------
                # Confidence
                # ----------------------------------

                confidence = compute_confidence(
                    shift_distance=shift_distance,
                    area_ratio=1.0,
                    confidence_gap=result["confidence_gap"]
                )

                # ----------------------------------
                # Convert back to EPSG:4326
                # ----------------------------------

                shifted_geom = shp_transform(
                    lambda xs, ys, z=None:
                    tf.transform(xs, ys),
                    shifted_geom_img
                )

                truth_geom = truth.loc[
                    plot_id,
                    "geometry"
                ]

                plot_iou = iou(
                    shifted_geom,
                    truth_geom
                )

                rows.append({

                    "plot_number":
                    plot_id,

                    "dx":
                    dx,

                    "dy":
                    dy,

                    "shift_distance":
                    shift_distance,

                    "alignment_score":
                    best_score,

                    "confidence_gap": result[
                    "confidence_gap"],

                    "confidence":
                    confidence,

                    "iou":
                    plot_iou

                })

                print(
                    f"{plot_id} | "
                    f"shift={shift_distance:.1f}m | "
                    f"IoU={plot_iou:.3f} | "
                    f"conf={confidence:.3f}"
                )

            except Exception as e:

                print(
                    f"FAILED {plot_id}: {e}"
                )

    # ========================================================
    # Save Results
    # ========================================================

    df = pd.DataFrame(
        rows
    )

    OUTPUT_DIR = Path(
        "outputs/debug"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    out_file = (
        OUTPUT_DIR /
        f"alignment_evaluation_{village_name}.csv"
    )

    df.to_csv(
        out_file,
        index=False
    )

    print()
    print("=" * 80)
    print(df)
    print("=" * 80)

    print()

    print(
        "Average IoU:",
        round(
            df["iou"].mean(),
            3
        )
    )

    print(
        "Average Shift:",
        round(
            df["shift_distance"].mean(),
            2
        ),
        "m"
    )

    print(
        "\nSaved:",
        out_file
    )