from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import rasterio

from bhume import load
from bhume.geo import geom_to_imagery_crs

VILLAGE_DIR = "data/vadnerbhairav"

village = load(VILLAGE_DIR)

plot_id = str(village.plots.index[0])

geom = village.plot(plot_id)

print("\nORIGINAL GEOMETRY")
print("--------------------------------")
print("Bounds:")
print(geom.bounds)

with rasterio.open(village.boundaries_path) as src:

    geom_img = geom_to_imagery_crs(
        src,
        geom
    )

    print("\nIMAGERY GEOMETRY")
    print("--------------------------------")
    print("Bounds:")
    print(geom_img.bounds)

    print("\nRASTER CRS")
    print("--------------------------------")
    print(src.crs)

print()