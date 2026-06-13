import numpy as np

def sigmoid(x):
    return 1 / (
        1 + np.exp(-x)
    )


def shift_confidence(
    shift_distance
):
    return float(
        np.exp(
            -shift_distance / 35
        )
    )


def area_confidence(
    area_ratio
):

    if area_ratio is None:
        return 0.5

    return float(
        max(
            0,
            1 - abs(area_ratio - 1.0)
        )
    )


def gap_confidence(
    confidence_gap
):
   
    return float(
        sigmoid(
            confidence_gap * 5
        )
    )


def compute_confidence(
    shift_distance,
    area_ratio,
    confidence_gap
):

    shift_score = shift_confidence(
        shift_distance
    )

    area_score = area_confidence(
        area_ratio
    )

    gap_score = gap_confidence(
        confidence_gap
    )

    confidence = (
        0.75 * shift_score +
        0.15 * area_score +
        0.10 * gap_score
    )

    return round(
        float(
            max(
                0,
                min(confidence, 1)
            )
        ),
        3
    )