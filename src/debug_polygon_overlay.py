from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import rasterio
from rasterio.windows import from_bounds
from shapely.geometry import Polygon, MultiPolygon

from bhume import load
from bhume.geo import geom_to_imagery_crs

VILLAGE_DIR = "data/vadnerbhairav"
PLOT_ID = "1007"

OUTPUT_DIR = Path("outputs/debug")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

village = load(VILLAGE_DIR)

geom = village.plot(PLOT_ID)

with rasterio.open(village.boundaries_path) as src:

    geom_img = geom_to_imagery_crs(src, geom)

    minx, miny, maxx, maxy = geom_img.bounds

    PAD = 50

    window = from_bounds(
        minx - PAD,
        miny - PAD,
        maxx + PAD,
        maxy + PAD,
        transform=src.transform
    )

    arr = src.read(1, window=window)

    transform = src.window_transform(window)

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.imshow(arr, cmap="gray")

    def draw_poly(poly):
        x, y = poly.exterior.xy

        px = []
        py = []

        for xx, yy in zip(x, y):
            col, row = ~transform * (xx, yy)
            px.append(col)
            py.append(row)

        ax.plot(px, py, linewidth=2)

    if geom_img.geom_type == "Polygon":
        draw_poly(geom_img)

    elif geom_img.geom_type == "MultiPolygon":
        for p in geom_img.geoms:
            draw_poly(p)

    ax.set_title(f"Plot {PLOT_ID}")
    ax.axis("off")

    plt.savefig(
        OUTPUT_DIR / f"{PLOT_ID}_polygon_overlay.png",
        bbox_inches="tight"
    )

    plt.close()

print("Saved overlay")