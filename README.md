# BhuMe - Land Parcel Boundary Alignment System

## Overview

This project addresses the BhuMe Boundary Alignment Challenge, where official land parcel boundaries are misaligned with actual field boundaries visible in satellite imagery. The objective is to estimate the true on-ground parcel location, assign a calibrated confidence score, and flag parcels that cannot be reliably corrected.

The solution combines image-based boundary alignment, geometric consistency checks, and confidence calibration to generate corrected parcel boundaries while maintaining reliable uncertainty estimates.

---

## Problem Statement

Official cadastral boundaries often exhibit systematic spatial offsets due to historical georeferencing processes. These offsets can range from a few meters to several tens of meters.

Given:

* Official plot boundaries (`input.geojson`)
* Satellite imagery (`imagery.tif`)
* Auto-detected boundary hints (`boundaries.tif`)
* Example aligned truths (`example_truths.geojson`)

The task is to:

1. Estimate the true field boundary location.
2. Produce corrected geometries where confidence is sufficient.
3. Flag uncertain plots.
4. Generate calibrated confidence scores that correlate with alignment quality.

---

## Solution Approach

### 1. Boundary-Based Alignment

For each parcel:

* Extract a localized boundary-hint patch.
* Rasterize the parcel geometry.
* Search neighboring translations around the original location.
* Evaluate alignment quality against detected field boundaries.
* Select the best-scoring spatial shift.

This enables recovery of local positional errors beyond a simple global offset.

---

### 2. Area Consistency Analysis

The solution compares:

* Recorded area
* Map area
* Potential kharaba area

to compute an area ratio.

Plots are classified into:

| Class      | Description               |
| ---------- | ------------------------- |
| placement  | Area appears consistent   |
| uncertain  | Moderate area discrepancy |
| area_error | Significant mismatch      |
| unknown    | Missing information       |

Highly unreliable plots are conservatively flagged.

---

### 3. Confidence Calibration

Confidence is derived from three signals:

#### Shift Quality

Measures how reasonable the required geometric movement is.

#### Area Consistency

Rewards parcels whose geometry agrees with land records.

#### Alignment Separation

Measures the difference between the best and second-best alignment candidates.

Confidence Formula:

```python
confidence =
    0.30 * shift_score +
    0.10 * area_score +
    0.60 * gap_score
```

This weighting emphasizes alignment certainty while preserving sensitivity to geometry quality.

---

### 4. Decision Logic

A parcel is marked:

```python
corrected
```

when:

```python
confidence >= 0.70
```

Otherwise:

```python
flagged
```

This conservative strategy prioritizes reliability over aggressive corrections.

---

## Project Structure

```text
src/
│
├── alignment.py
├── confidence.py
├── predictor.py
├── generate_predictions.py
├── evaluate_alignment.py
└── evaluate_calibration.py
```

### Core Modules

#### alignment.py

Responsible for:

* Boundary extraction
* Search window generation
* Candidate evaluation
* Best-shift selection

#### confidence.py

Computes calibrated confidence scores from alignment metrics.

#### generate_predictions.py

Main prediction pipeline.

Generates:

```text
outputs/predictions/
├── vadnerbhairav_predictions.geojson
└── malatavadi_predictions.geojson
```

#### evaluate_alignment.py

Evaluates correction quality against public truths.

Reports:

* IoU
* Shift distance
* Alignment metrics

#### evaluate_calibration.py

Evaluates confidence quality.

Reports:

* Confidence-IoU correlation
* Calibration ranking performance

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

## Running the Pipeline

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

## Output Format

The system generates GeoJSON files containing:

```json
{
  "plot_number": "...",
  "status": "corrected | flagged",
  "confidence": 0.84,
  "geometry": { ... }
}
```

These outputs conform to the competition prediction contract.

---

## Key Design Principles

* Conservative corrections over aggressive movement
* Confidence scores represent actual reliability
* Local alignment instead of global shifting
* Explicit handling of uncertain plots
* Calibration-aware prediction generation

---

## Technologies Used

* Python 3.12
* GeoPandas
* Rasterio
* Shapely
* NumPy
* OpenCV
* Pandas

---

## Future Improvements

* Multi-scale alignment search
* Edge-aware boundary matching
* Shape similarity constraints
* Learned confidence calibration
* Ensemble alignment strategies

---

## Author

Vamshi Kumar

BhuMe Boundary Alignment Challenge Submission
