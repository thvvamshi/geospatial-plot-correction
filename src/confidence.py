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

    try:

        if np.isnan(area_ratio):
            return 0.5

    except Exception:
        pass

    return float(
        np.exp(
            -abs(
                area_ratio - 1.0
            )
        )
    )


def gap_confidence(
    confidence_gap
):

    return float(
        sigmoid(
            confidence_gap * 40
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

    # Threesold val
    confidence = (

        # 0.50 * shift_score +

        # 0.10 * area_score +

        # 0.40 * gap_score

        0.30 * shift_score +

        0.10 * area_score +

        0.60 * gap_score

    )

    # Penalize ambiguous alignments

    if confidence_gap < 0.01:

        confidence *= 0.70

    elif confidence_gap < 0.02:

        confidence *= 0.85

    return round(

        float(

            max(
                0.0,
                min(
                    confidence,
                    1.0
                )
            )
        ),
        3
    )