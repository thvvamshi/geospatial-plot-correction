# BhuMe – Land Parcel Boundary Alignment System

## Overview

This repository contains my solution for the BhuMe Boundary Alignment Challenge.

The objective is to improve the spatial accuracy of official land parcel boundaries by aligning them with visible field boundaries in satellite imagery while providing calibrated confidence estimates and flagging uncertain cases.

The solution combines:

* Local boundary-based alignment
* Geometric consistency validation
* Confidence calibration
* Conservative correction policies

Rather than forcing corrections on every plot, the system attempts to identify when a correction is reliable and when a parcel should remain flagged for manual review.

---

## Problem

Official cadastral boundaries are often spatially misaligned due to historical georeferencing processes and map digitization workflows.

Given:

* `input.geojson` – official parcel boundaries
* `imagery.tif` – satellite imagery
* `boundaries.tif` – detected field boundary hints
* `example_truths.geojson` – public aligned examples

The task is to:

1. Estimate the true parcel position.
2. Produce corrected boundaries.
3. Assign meaningful confidence scores.
4. Flag uncertain plots.
5. Generate contract-compliant predictions.

---

## Solution Architecture

```text
Official Parcel
       │
       ▼
Boundary Patch Extraction
       │
       ▼
Local Alignment Search
       │
       ▼
Best Candidate Selection
       │
       ▼
Confidence Estimation
       │
       ▼
Corrected / Flagged Decision
       │
       ▼
Predictions GeoJSON
```

The system is intentionally modular so alignment quality, confidence estimation, and evaluation can be analyzed independently.

---

## Approach

### 1. Local Boundary Alignment

For every parcel:

* Extract a local boundary-hint raster patch.
* Rasterize the parcel geometry.
* Search neighboring translations around the original location.
* Evaluate candidate alignments against detected field boundaries.
* Select the highest-scoring candidate.

This allows the system to recover local positional errors rather than relying on a single global offset.

---

### 2. Area Consistency Validation

Parcel metadata is used to evaluate geometric plausibility.

Computed metrics include:

* Recorded area
* Map area
* Potential kharaba area
* Area ratio

Plots are categorized as:

| Class      | Meaning                 |
| ---------- | ----------------------- |
| placement  | Area appears consistent |
| uncertain  | Moderate mismatch       |
| area_error | Significant discrepancy |
| unknown    | Missing information     |

Severe inconsistencies are conservatively flagged.

---

### 3. Confidence Calibration

Confidence is designed to reflect actual reliability rather than simply alignment quality.

Three signals are used:

#### Shift Quality

Measures how reasonable the required correction distance is.

#### Area Consistency

Rewards geometrically plausible parcels.

#### Alignment Separation

Measures how strongly the best alignment candidate outperforms competing candidates.

Confidence Formula:

```python
confidence = (
    0.30 * shift_score +
    0.10 * area_score +
    0.60 * gap_score
)
```

The strongest weight is assigned to candidate separation because it proved most useful for calibration.

---

### 4. Decision Strategy

Plots are marked as:

```text
corrected
```

when:

```python
confidence >= 0.70
```

Otherwise they are:

```text
flagged
```

This prioritizes reliability over aggressive correction.

---

## Repository Structure

```text
.
├── src/
│   ├── alignment.py
│   ├── confidence.py
│   ├── predictor.py
│   ├── generate_predictions.py
│   ├── evaluate_alignment.py
│   └── evaluate_calibration.py
│
├── outputs/
│   ├── predictions/
│   └── debug/
│
├── transcripts/
│   ├── README.md
│   └── ...
│
├── CONTRACT.md
├── README.md
└── requirements.txt
```

---

## Core Components

### alignment.py

Responsible for:

* Boundary extraction
* Candidate shift generation
* Alignment scoring
* Best candidate selection

### confidence.py

Computes calibrated confidence estimates from alignment metrics.

### generate_predictions.py

Main prediction pipeline.

Produces:

```text
outputs/predictions/
├── vadnerbhairav_predictions.geojson
└── malatavadi_predictions.geojson
```

### evaluate_alignment.py

Evaluates alignment quality against public truths.

Metrics:

* IoU
* Shift distance
* Alignment statistics

### evaluate_calibration.py

Evaluates confidence quality.

Metrics:

* Confidence-IoU correlation
* Calibration ranking quality

---

## Results

### Vadnerbhairav

| Metric                      | Score  |
| --------------------------- | ------ |
| Corrected Truths            | 4 / 6  |
| Flagged Truths              | 2 / 6  |
| Median IoU                  | 0.827  |
| Official Baseline           | 0.612  |
| Improvement                 | +0.333 |
| Accurate @ IoU ≥ 0.5        | 100%   |
| Median Centroid Error       | 5.0 m  |
| Calibration Correlation (ρ) | 0.40   |

### Malatavadi

| Metric                | Score  |
| --------------------- | ------ |
| Corrected Truths      | 1 / 3  |
| Flagged Truths        | 2 / 3  |
| Median IoU            | 0.756  |
| Official Baseline     | 0.510  |
| Improvement           | +0.246 |
| Accurate @ IoU ≥ 0.5  | 100%   |
| Median Centroid Error | 4.1 m  |

---

## Running the Solution

Generate predictions:

```bash
python src/generate_predictions.py --village vadnerbhairav

python src/generate_predictions.py --village malatavadi
```

Evaluate alignment:

```bash
python src/evaluate_alignment.py vadnerbhairav

python src/evaluate_alignment.py malatavadi
```

Evaluate confidence calibration:

```bash
python src/evaluate_calibration.py outputs/predictions/vadnerbhairav_predictions.geojson

python src/evaluate_calibration.py outputs/predictions/malatavadi_predictions.geojson
```

---

## Submission Artifacts

This repository contains:

* Source code
* Prediction GeoJSON files
* AI development transcripts
* Evaluation utilities
* Engineering walkthrough materials

---

## Key Engineering Decisions

* Prioritized local alignment over global shifting
* Treated confidence as a first-class objective
* Used conservative correction thresholds
* Explicitly modeled uncertainty through flagging
* Focused on interpretability and debugging rather than model complexity

---

## Future Work

Potential improvements include:

* Multi-scale alignment search
* Edge-aware matching directly from imagery
* Shape similarity constraints
* Learned confidence calibration
* Ensemble alignment strategies
* Larger-scale calibration validation

---

## Author

**Vamshi Kumar**
