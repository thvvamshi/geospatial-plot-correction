from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon

from bhume import load, patch_for_plot
from bhume.geo import open_imagery

VILLAGE_DIR = "data/vadnerbhairav"

OUTPUT_DIR = Path("outputs/debug")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

village = load(VILLAGE_DIR)

plot_id = "1007"

geom = village.plot(plot_id)

with open_imagery(village.imagery_path) as src:

    patch = patch_for_plot(
        src,
        geom,
        pad_m=50
    )

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.imshow(patch.image)

    ax.set_title(f"Plot {plot_id}")
    ax.axis("off")

    plt.savefig(
        OUTPUT_DIR / f"plot_{plot_id}_debug.png",
        bbox_inches="tight"
    )

    plt.close()

print("Saved debug image.")