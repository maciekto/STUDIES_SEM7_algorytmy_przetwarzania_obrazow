"""Funkcje ładujące pliki i zapisujące je.

Ten moduł eksportuje dwie funkcje:
- load(path) -> numpy.ndarray: wczytuje zdjęcie z dysku
- save(img, path) -> None: zapisuje numpy tablicę zdjęcia na dysku

Uwaga: wcześniej aplikacja zawsze wczytywała obrazy jako skala szarości.
W tej wersji wspieramy wczytywanie kolorowych obrazów. Funkcja load używa
OpenCV z flagą IMREAD_UNCHANGED aby zachować liczbę kanałów zgodnie z
plikiem na dysku: 1 (grayscale), 3 (BGR) lub 4 (BGRA). Zwracana tablica
to NumPy ndarray dtype uint8.
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

    # Wczytanie obrazu bez konwersji kanałów — zachowujemy oryginalną
    # liczbę kanałów (mono, BGR lub BGRA). To pozwala obsługiwać obrazy
    # kolorowe i rysować histogramy per-kanał.
    img = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
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
