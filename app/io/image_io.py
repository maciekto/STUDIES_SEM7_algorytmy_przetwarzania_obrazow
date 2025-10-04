"""Funkcje ładujące pliki i zapisujące je

Ten moduł eksportuje dwie funkcje:
- load(path) -> numpy.ndarray: wczytuje zdjęcie z dysku
- save(img, path) -> None: zapisuje numpy tablcję zdjęcia na dysku

Zawsze otwiera aplikację w skali szarości. Potem czyta zdjęcia za pomocą OpenCV's IMREAD_GRAYSCALE
i zawsze zwraca 2D uint8 numpy tablicę H x W
"""

from pathlib import Path
import cv2
import numpy as np


SUPPORTED = {".bmp", ".tif", ".tiff", ".png", ".jpg", ".jpeg"}


def load(path: str) -> np.ndarray:
    """Ładowanie zdjęcia z dysku i w skali szarości do tablicy NumPy."""
    p = Path(path)

    # Sprawdzenie czy rozszerzenie zdjęcia jest wspierane
    if p.suffix.lower() not in SUPPORTED:
        raise ValueError(f"Unsupported format: {p.suffix}")

    # Wczytanie img jako cv2 z ustawieniem skali szarości
    img = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise IOError(f"Cannot read image: {path}")
    return img


def save(img: np.ndarray, path: str) -> None:
    """Zapisanie zdjęcia `img` na dysk używając OpenCV za pomocą ścieżki
    `img` może być w skali szarości (H x W) albo tablicą kolorów, OpenCV
    wspiera format w zalezności od tablicy
    """
    p = Path(path)
    ok = cv2.imwrite(str(p), img)
    if not ok:
        raise IOError(f"Cannot write image: {path}")
