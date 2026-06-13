from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import rasterio
import pandas as pd

from bhume import load

from alignment import (
    get_boundary_patch,
    align_plot
)

VILLAGE_DIR = "data/vadnerbhairav"


def classify_area(area_ratio):

    if pd.isna(area_ratio):
        return "unknown"

    if 0.8 <= area_ratio <= 1.2:
        return "placement"

    if area_ratio < 0.5 or area_ratio > 2.0:
        return "area_error"

    return "uncertain"


if __name__ == "__main__":

    village = load(VILLAGE_DIR)

    plots = village.plots.copy()

    plots["pot_kharaba_sqm"] = (
        plots["pot_kharaba_ha"].fillna(0)
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

    SAMPLE_SIZE = 100

    start_time = time.time()

    processed = 0
    aligned = 0

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

                if area_class != "placement":
                    continue

                geom = village.plot(
                    plot_id
                )

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

                aligned += 1
                processed += 1

                if processed % 10 == 0:

                    elapsed = (
                        time.time()
                        - start_time
                    )

                    per_plot = (
                        elapsed / processed
                    )

                    print(
                        f"{processed:>3} plots | "
                        f"{per_plot:.2f}s/plot | "
                        f"last shift={result['shift_distance']:.1f}m"
                    )

            except Exception as e:

                print(
                    f"FAILED {plot_id}: {e}"
                )

    total_time = (
        time.time()
        - start_time
    )

    print()
    print("=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)

    print(
        f"Sample Size: {SAMPLE_SIZE}"
    )

    print(
        f"Aligned Plots: {aligned}"
    )

    print(
        f"Total Time: {total_time:.2f} sec"
    )

    if aligned > 0:

        sec_per_plot = (
            total_time / aligned
        )

        print(
            f"Seconds / Plot: "
            f"{sec_per_plot:.2f}"
        )

        estimated = (
            sec_per_plot
            * len(village.plots)
        )

        print(
            f"Estimated Full Village: "
            f"{estimated/60:.1f} min"
        )

        print(
            f"Estimated Full Village: "
            f"{estimated/3600:.2f} hr"
        )