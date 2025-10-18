"""Simple validators for image types and sizes.

Presently used to ensure point operations run on grayscale images.
"""
from __future__ import annotations

import numpy as np


def ensure_grayscale(img: np.ndarray) -> None:
    if img.ndim != 2:
        raise ValueError("Operacje punktowe dostępne tylko dla obrazów w skali szarości (mono).")
