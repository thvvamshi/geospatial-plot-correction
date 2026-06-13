from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import cv2
import numpy as np
import rasterio

from rasterio.windows import from_bounds

from shapely.affinity import translate
from shapely.geometry import LineString

from bhume import load
from bhume.geo import geom_to_imagery_crs

VILLAGE_DIR = "data/vadnerbhairav"


# ============================================================
# Read Boundary Patch
# ============================================================

def get_boundary_patch(src, geom, pad=50):

    geom_img = geom_to_imagery_crs(src, geom)

    minx, miny, maxx, maxy = geom_img.bounds

    window = from_bounds(
        minx - pad,
        miny - pad,
        maxx + pad,
        maxy + pad,
        transform=src.transform
    )

    boundary_img = src.read(
        1,
        window=window
    )

    transform = src.window_transform(
        window
    )

    return (
        boundary_img,
        transform,
        geom_img
    )


# ============================================================
# Boundary Sampling
# ============================================================

def sample_polygon_boundary(
    poly,
    n_points=200
):

    if poly.geom_type == "MultiPolygon":

        poly = max(
            poly.geoms,
            key=lambda g: g.area
        )

    boundary = LineString(
        poly.exterior.coords
    )

    distances = np.linspace(
        0,
        boundary.length,
        n_points
    )

    return [
        boundary.interpolate(d)
        for d in distances
    ]


# ============================================================
# Convert Sampled Points -> Pixels
# ============================================================

def sampled_points_to_pixels(
    geom,
    transform,
    n_points=200
):

    points = sample_polygon_boundary(
        geom,
        n_points=n_points
    )

    pixels = []

    for p in points:

        col, row = ~transform * (
            p.x,
            p.y
        )

        pixels.append(
            (
                float(row),
                float(col)
            )
        )

    return np.array(
        pixels,
        dtype=np.float32
    )


# ============================================================
# Distance Transform
# ============================================================

def build_distance_map(
    boundary_img
):

    binary = (
        boundary_img > 0
    ).astype(np.uint8)

    inverted = 1 - binary

    return cv2.distanceTransform(
        inverted,
        cv2.DIST_L2,
        5
    )


# ============================================================
# Fast Shift Scoring
# ============================================================

def score_shift_pixels(
    distance_map,
    base_pixels,
    dx,
    dy
):

    shifted = base_pixels.copy()

    shifted[:, 1] += dx
    shifted[:, 0] += dy

    rows = shifted[:, 0].astype(int)
    cols = shifted[:, 1].astype(int)

    h, w = distance_map.shape

    mask = (
        (rows >= 0)
        &
        (rows < h)
        &
        (cols >= 0)
        &
        (cols < w)
    )

    if mask.sum() == 0:
        return -999999

    distances = distance_map[
        rows[mask],
        cols[mask]
    ]

    return -float(
        np.mean(
            distances
        )
    )


# ============================================================
# Coarse-to-Fine Search
# ============================================================

def find_best_shift(
    boundary_img,
    geom_img,
    transform
):

    distance_map = build_distance_map(
        boundary_img
    )

    base_pixels = sampled_points_to_pixels(
        geom_img,
        transform
    )

    best_score = -999999
    best_dx = 0
    best_dy = 0

    # ========================================================
    # Stage 1
    # ========================================================

    for dx in range(-40, 41, 8):

        for dy in range(-40, 41, 8):

            score = score_shift_pixels(
                distance_map,
                base_pixels,
                dx,
                dy
            )

            if score > best_score:

                best_score = score
                best_dx = dx
                best_dy = dy

    # ========================================================
    # Stage 2
    # ========================================================

    final_score = best_score
    final_dx = best_dx
    final_dy = best_dy

    second_best = -999999

    for dx in range(
        best_dx - 8,
        best_dx + 9,
        2
    ):

        for dy in range(
            best_dy - 8,
            best_dy + 9,
            2
        ):

            score = score_shift_pixels(
                distance_map,
                base_pixels,
                dx,
                dy
            )

            if score > final_score:

                second_best = final_score

                final_score = score
                final_dx = dx
                final_dy = dy

            elif score > second_best:

                second_best = score

    return (
        final_dx,
        final_dy,
        final_score,
        second_best
    )


# ============================================================
# Public API
# ============================================================

def align_plot(
    boundary_img,
    geom_img,
    transform
):

    (
        dx,
        dy,
        best_score,
        second_best
    ) = find_best_shift(
        boundary_img,
        geom_img,
        transform
    )

    shifted_geom = translate(
        geom_img,
        xoff=dx,
        yoff=dy
    )

    shift_distance = np.sqrt(
        dx * dx +
        dy * dy
    )

    return {

        "dx": dx,
        "dy": dy,

        "shift_distance":
        float(shift_distance),

        "best_score":
        float(best_score),

        "second_best":
        float(second_best),

        "confidence_gap":
        float(
            best_score -
            second_best
        ),

        "shifted_geom":
        shifted_geom
    }


# ============================================================
# Debug
# ============================================================

if __name__ == "__main__":

    village = load(
        VILLAGE_DIR
    )

    test_plots = [
        "1007",
        "1008",
        "1009",
        "1010",
        "1011"
    ]

    with rasterio.open(
        village.boundaries_path
    ) as src:

        for plot_id in test_plots:

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

            print(
                f"{plot_id:>6} | "
                f"dx={result['dx']:>4} | "
                f"dy={result['dy']:>4} | "
                f"shift={result['shift_distance']:.1f}m | "
                f"score={result['best_score']:.3f}"
            )