from pathlib import Path
import cv2
import numpy as np

SUPPORTED = {".bmp", ".tif", ".tiff", ".png", ".jpg", ".jpeg"}

def load(path: str) -> np.ndarray:
    p = Path(path)
    if p.suffix.lower() not in SUPPORTED:
        raise ValueError(f"Unsupported format: {p.suffix}")
    img = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise IOError(f"Cannot read image: {path}")
    return img  # BGR or BGRA or grayscale

def save(img: np.ndarray, path: str) -> None:
    p = Path(path)
    ok = cv2.imwrite(str(p), img)
    if not ok:
        raise IOError(f"Cannot write image: {path}")
