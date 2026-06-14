from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import geopandas as gpd
import pandas as pd


# Resolve Prediction File
def get_prediction_file():

    if len(sys.argv) > 1:

        prediction_file = Path(
            sys.argv[1]
        )

        if not prediction_file.exists():

            print(
                f"\nERROR: File not found\n"
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
            "\nERROR: No prediction "
            "files found."
        )

        sys.exit(1)

    if len(files) == 1:

        return files[0]

    print("\nAvailable prediction files:\n")

    for idx, file in enumerate(files):

        print(
            f"{idx + 1}. "
            f"{file.name}"
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


# Main
if __name__ == "__main__":

    prediction_file = (
        get_prediction_file()
    )

    print()
    print("=" * 60)
    print("LOADING PREDICTIONS")
    print("=" * 60)

    print(
        f"\nFile:\n"
        f"{prediction_file}\n"
    )

    gdf = gpd.read_file(
        prediction_file
    )

    # Required Columns
    required_columns = [

        "plot_number",
        "status",
        "confidence",
        "method_note",
        "geometry"

    ]

    missing_columns = [

        col

        for col in required_columns

        if col not in gdf.columns

    ]

    # Plot Number Validation
    missing_plot_number = (

        gdf["plot_number"]
        .isna()
        .sum()

    )

    # Status Validation
    valid_status = {

        "corrected",
        "flagged"

    }

    invalid_status = (

        ~gdf["status"]
        .isin(valid_status)

    ).sum()

    corrected = (

        gdf["status"]
        ==
        "corrected"

    ).sum()

    flagged = (

        gdf["status"]
        ==
        "flagged"

    ).sum()

    # Confidence Validation
    missing_confidence = 0
    invalid_confidence = 0

    for _, row in gdf.iterrows():

        status = row[
            "status"
        ]

        confidence = row[
            "confidence"
        ]

        if status == "corrected":

            if pd.isna(
                confidence
            ):

                missing_confidence += 1

            elif not (
                0 <= confidence <= 1
            ):

                invalid_confidence += 1

        elif status == "flagged":

            if (
                pd.notna(confidence)
                and
                not (
                    0 <= confidence <= 1
                )
            ):

                invalid_confidence += 1

    # Geometry Validation
    invalid_geometry = 0
    empty_geometry = 0

    for geom in gdf.geometry:

        if geom is None:

            invalid_geometry += 1
            continue

        if geom.is_empty:

            empty_geometry += 1

        if not geom.is_valid:

            invalid_geometry += 1

    # CRS Validation
    crs_ok = False

    if gdf.crs:

        crs_string = str(
            gdf.crs
        )

        if (
            "4326"
            in crs_string
        ):

            crs_ok = True

    # Confidence Stats
    confs = [

        c

        for c in gdf[
            "confidence"
        ]

        if pd.notna(c)

    ]

    # Report
    print()
    print("=" * 60)
    print("VALIDATION REPORT")
    print("=" * 60)

    print(
        f"Features: "
        f"{len(gdf)}"
    )

    print()

    print(
        f"Missing Columns: "
        f"{len(missing_columns)}"
    )

    if missing_columns:

        print()

        for col in missing_columns:

            print(
                f"  - {col}"
            )

    print()

    print(
        f"Missing plot_number: "
        f"{missing_plot_number}"
    )

    print(
        f"Invalid status: "
        f"{invalid_status}"
    )

    print()

    print(
        f"Missing confidence: "
        f"{missing_confidence}"
    )

    print(
        f"Invalid confidence: "
        f"{invalid_confidence}"
    )

    print()

    print(
        f"Invalid geometry: "
        f"{invalid_geometry}"
    )

    print(
        f"Empty geometry: "
        f"{empty_geometry}"
    )

    print()

    print(
        f"Corrected: "
        f"{corrected}"
    )

    print(
        f"Flagged: "
        f"{flagged}"
    )

    if confs:

        print()

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

    print()

    print(
        f"CRS: "
        f"{gdf.crs}"
    )

    print(
        f"EPSG:4326: "
        f"{'PASS' if crs_ok else 'FAIL'}"
    )

    # Final Verdict
    passed = (

        len(missing_columns) == 0
        and
        missing_plot_number == 0
        and
        invalid_status == 0
        and
        missing_confidence == 0
        and
        invalid_confidence == 0
        and
        invalid_geometry == 0
        and
        empty_geometry == 0
        and
        crs_ok

    )

    print()
    print("=" * 60)

    if passed:

        print(
            "PASS ✅"
        )

    else:

        print(
            "FAIL ❌"
        )

    print("=" * 60)