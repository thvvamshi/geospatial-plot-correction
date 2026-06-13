from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import geopandas as gpd

prediction_file = (
    "outputs/predictions/"
    "vadnerbhairav_predictions.geojson"
)

gdf = gpd.read_file(
    prediction_file
)

print()
print("CRS")
print("--------------------------------")
print(gdf.crs)

print()
print("FIRST GEOMETRY")
print("--------------------------------")
print(gdf.geometry.iloc[0].bounds)