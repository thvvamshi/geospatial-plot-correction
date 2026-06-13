from confidence import compute_confidence

examples = [

    # excellent
    {
        "shift": 10,
        "ratio": 1.02,
        "gap": 1.5
    },

    # good
    {
        "shift": 20,
        "ratio": 0.95,
        "gap": 0.8
    },

    # medium
    {
        "shift": 35,
        "ratio": 1.10,
        "gap": 0.3
    },

    # weak
    {
        "shift": 55,
        "ratio": 1.30,
        "gap": 0.1
    },

    # terrible
    {
        "shift": 90,
        "ratio": 2.50,
        "gap": 0.01
    }
]

for row in examples:

    conf = compute_confidence(
        shift_distance=row["shift"],
        area_ratio=row["ratio"],
        confidence_gap=row["gap"]
    )

    print(
        f"shift={row['shift']:>3}m | "
        f"ratio={row['ratio']:.2f} | "
        f"gap={row['gap']:.2f} | "
        f"confidence={conf:.3f}"
    )