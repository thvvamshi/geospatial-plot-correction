from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import geopandas as gpd
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
VILLAGE_NAME = "vadnerbhairav"


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
        plots["recorded_area_sqm"].fillna(0)
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
            plots.iterrows()
        ):

            try:

                area_ratio = row["area_ratio"]

                area_class = classify_area(
                    area_ratio
                )

                original_geom = village.plot(
                    plot_id
                )

                # ====================================================
                # Conservative Flagging
                # ====================================================

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

                        "method_note":
                        area_class,

                        "geometry":
                        original_geom

                    })

                    continue

                # ====================================================
                # Alignment
                # ====================================================

                (
                    boundary_img,
                    transform,
                    geom_img
                ) = get_boundary_patch(
                    src,
                    original_geom
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
                    if confidence >= 0.60
                    else "flagged"
                )

                geometry = (
                    result["shifted_geom"]
                    if status == "corrected"
                    else original_geom
                )

                predictions.append({

                    "plot_number":
                    str(plot_id),

                    "status":
                    status,

                    "confidence":
                    round(
                        float(confidence),
                        3
                    ),

                    "method_note":
                    (
                        f"{area_class}; "
                        f"shift="
                        f"{result['shift_distance']:.1f}m"
                    ),

                    "geometry":
                    geometry

                })

                if idx % 250 == 0:

                    print(
                        f"{idx:>4} | "
                        f"{plot_id} | "
                        f"{status} | "
                        f"shift="
                        f"{result['shift_distance']:.1f}m | "
                        f"conf={confidence:.3f}"
                    )

            except Exception as e:

                print(
                    f"FAILED {plot_id}: {e}"
                )

    # ============================================================
    # Fix Invalid Geometries
    # ============================================================

    for row in predictions:

        try:

            if row["geometry"] is not None:

                row["geometry"] = (
                    row["geometry"]
                    .buffer(0)
                )

        except Exception:

            pass

    # ============================================================
    # Sort Output
    # ============================================================

    predictions = sorted(

        predictions,

        key=lambda x:
        x["plot_number"]

    )

    # ============================================================
    # Summary
    # ============================================================

    corrected = sum(

        p["status"] == "corrected"

        for p in predictions

    )

    flagged = sum(

        p["status"] == "flagged"

        for p in predictions

    )

    confs = [

        p["confidence"]

        for p in predictions

        if p["confidence"] is not None

    ]

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(
        f"Total Predictions: "
        f"{len(predictions)}"
    )

    print(
        f"Corrected: "
        f"{corrected}"
    )

    print(
        f"Flagged: "
        f"{flagged}"
    )

    if confs:

        print(
            f"Average Confidence: "
            f"{sum(confs)/len(confs):.3f}"
        )

        print(
            f"Min Confidence: "
            f"{min(confs):.3f}"
        )

        print(
            f"Max Confidence: "
            f"{max(confs):.3f}"
        )

    # ============================================================
    # GeoDataFrame
    # ============================================================

    gdf = gpd.GeoDataFrame(

        predictions,

        geometry="geometry",

        crs="EPSG:4326"

    )

    # ============================================================
    # Save GeoJSON
    # ============================================================

    output_dir = Path(
        "outputs/predictions"
    )

    output_dir.mkdir(

        parents=True,

        exist_ok=True

    )

    output_file = (

        output_dir

        /

        f"{VILLAGE_NAME}_predictions.geojson"

    )

    gdf.to_file(

        output_file,

        driver="GeoJSON"

    )

    print()
    print("=" * 60)
    print(
        f"Generated "
        f"{len(gdf)} predictions"
    )
    print(
        f"Saved: "
        f"{output_file}"
    )
    print("=" * 60)