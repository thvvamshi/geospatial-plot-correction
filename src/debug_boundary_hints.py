from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PIL import Image
import rasterio
from rasterio.windows import from_bounds

from bhume import load
from bhume.geo import geom_to_imagery_crs

VILLAGE_DIR = "data/vadnerbhairav"
PLOT_ID = "1007"

OUTPUT_DIR = Path("outputs/debug")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

village = load(VILLAGE_DIR)

geom = village.plot(PLOT_ID)

with rasterio.open(village.boundaries_path) as src:

    g = geom_to_imagery_crs(src, geom)

    minx, miny, maxx, maxy = g.bounds

    pad = 50

    window = from_bounds(
        minx - pad,
        miny - pad,
        maxx + pad,
        maxy + pad,
        transform=src.transform
    )

    arr = src.read(1, window=window)

    arr = arr.astype("float32")

    arr -= arr.min()

    if arr.max() > 0:
        arr /= arr.max()

    arr = (arr * 255).astype("uint8")

    Image.fromarray(arr).save(
        OUTPUT_DIR / f"{PLOT_ID}_boundary_hint.png"
    )

print("Saved boundary hint patch")