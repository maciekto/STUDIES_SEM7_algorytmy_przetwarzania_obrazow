"""Simple image input/output helpers based on OpenCV.

This module exposes two small functions:
- load(path) -> numpy.ndarray: loads an image from disk
- save(img, path) -> None: writes a numpy array image to disk

Note: this application opens images strictly in grayscale (as requested by the
user). The loader therefore reads images using OpenCV's IMREAD_GRAYSCALE mode
and always returns a 2D uint8 numpy array (H x W).
"""

from pathlib import Path
import cv2
import numpy as np

# Supported file extensions (used only for a friendly error message)
SUPPORTED = {".bmp", ".tif", ".tiff", ".png", ".jpg", ".jpeg"}


def load(path: str) -> np.ndarray:
    """Load an image from `path` and return a grayscale NumPy array.

    The function enforces a small set of extensions and uses OpenCV to read
    the image in grayscale. The returned array has shape (H, W) and dtype
    uint8.
    """
    p = Path(path)
    if p.suffix.lower() not in SUPPORTED:
        raise ValueError(f"Unsupported format: {p.suffix}")
    # Always load as grayscale (single channel). This ensures the rest of the
    # application works with a predictable array shape.
    img = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise IOError(f"Cannot read image: {path}")
    return img


def save(img: np.ndarray, path: str) -> None:
    """Write the NumPy image `img` to disk at `path` using OpenCV.

    `img` can be a grayscale (H x W) or color array; OpenCV will handle the
    format based on array shape and extension.
    """
    p = Path(path)
    ok = cv2.imwrite(str(p), img)
    if not ok:
        raise IOError(f"Cannot write image: {path}")
