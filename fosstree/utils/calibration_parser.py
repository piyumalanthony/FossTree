"""Shared parser for MCMCTree calibration strings."""

from __future__ import annotations

import re
from typing import Optional

from fosstree.models import (
    CalibrationBase,
    BoundsCalibration,
    LowerCalibration,
    UpperCalibration,
    GammaCalibration,
    SkewNormalCalibration,
    SkewTCalibration,
    Skew2NormalsCalibration,
)

# Regex: TYPE(comma-separated floats)
_CAL_PATTERN = re.compile(r"(S2N|SN|ST|B|L|U|G)\(\s*([^)]+)\s*\)")

# (constructor_class, min_params, max_params)
_CAL_CONSTRUCTORS: dict[str, tuple[type, int, int]] = {
    "B":   (BoundsCalibration,        2, 4),
    "L":   (LowerCalibration,         1, 4),
    "U":   (UpperCalibration,         1, 2),
    "G":   (GammaCalibration,         2, 2),
    "SN":  (SkewNormalCalibration,    3, 3),
    "ST":  (SkewTCalibration,         4, 4),
    "S2N": (Skew2NormalsCalibration,  7, 7),
}


def parse_calibration(text: str) -> Optional[CalibrationBase]:
    """Parse an MCMCTree calibration string into a Calibration object.

    Supports: B(), L(), U(), G(), SN(), ST(), S2N()

    Args:
        text: Calibration string, e.g. "B(0.06,0.08,0.001,0.025)"

    Returns:
        A CalibrationBase subclass instance, or None if parsing fails.
    """
    text = text.strip()
    m = _CAL_PATTERN.match(text)
    if not m:
        return None

    cal_type = m.group(1)
    try:
        params = [float(x.strip()) for x in m.group(2).split(",")]
    except ValueError:
        return None

    cls, min_params, max_params = _CAL_CONSTRUCTORS[cal_type]
    if not (min_params <= len(params) <= max_params):
        return None

    return cls(*params)
