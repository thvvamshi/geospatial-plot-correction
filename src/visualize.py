from pathlib import Path
import sys
import random

# Add project root to import path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
from PIL import Image

from bhume import load, patch_for_plot
from bhume.geo import open_imagery

# config
VILLAGE_DIR = "data/vadnerbhairav"
NUM_SAMPLES = 20

OUTPUT_DIR = Path("outputs/plots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# load village and sample plots
village = load(VILLAGE_DIR)

print(f"Loaded village: {village.slug}")
print(f"Total plots: {len(village.plots)}")

plot_ids = random.sample(list(village.plots.index), min(NUM_SAMPLES, len(village.plots)))

# Generate and save patches for sampled plots
with open_imagery(village.imagery_path) as src:

    for plot_id in plot_ids:

        geom = village.plot(plot_id)

        try:
            patch = patch_for_plot(
                src,
                geom,
                pad_m=30
            )

            out_file = OUTPUT_DIR / f"{plot_id}.png"

            Image.fromarray(patch.image).save(out_file)

            print(f"Saved {out_file}")

        except Exception as e:
            print(f"Failed plot {plot_id}: {e}")

print("\nDone.")

plt.close("all")