"""Point operations implemented via LUTs applied manually.

Functions operate on grayscale images. For color images the operation is
applied per-channel using the same LUT.
"""
from __future__ import annotations

import numpy as np


def negation_lut(levels: int = 256) -> np.ndarray:
    """Create LUT performing image negation (inversion).

    Negacja to operacja punktowa S(r) = L-1 - r, gdzie L to liczba poziomów
    (np. 256), a r to wartość piksela. Negacja odwraca jasność obrazu: ciemne
    stają się jasne i odwrotnie. Przydaje się do wizualizacji kontrastu,
    uzyskania negatywów oraz jako element algorytmów przetwarzania obrazów.
    """
    return np.array([levels - 1 - i for i in range(levels)], dtype=np.uint8)


def requantization_lut(levels: int, target_levels: int) -> np.ndarray:
    """Create LUT to reduce number of gray levels (quantization).

    Requantyzacja (redukcja poziomów) mapuje oryginalne poziomy
    (np. 0..255) do mniejszej liczby przedziałów (np. 4). Każdy piksel
    zostaje przypisany do jednego z `target_levels` koszy, a następnie
    zamapowany na reprezentatywną wartość (np. środek kosza) skalowaną
    do pełnego zakresu. Służy do redukcji rozdzielczości jasności, efektów
    posteryzacji oraz obniżenia rozmiaru słownika wartości.
    """
    if target_levels < 2:
        raise ValueError("target_levels must be >=2")
    step = levels / target_levels
    lut = np.zeros((levels,), dtype=np.uint8)
    for i in range(levels):
        bin_idx = int(i // step)
        if bin_idx >= target_levels:
            bin_idx = target_levels - 1
        # map to center of bin scaled to full range
        lut[i] = np.uint8(round((bin_idx + 0.5) * (levels - 1) / target_levels))
    return lut


def threshold_binary_lut(threshold: int, levels: int = 256) -> np.ndarray:
    """Create binary threshold LUT.

    Progowanie binarne (binary thresholding) konwertuje obraz do dwóch
    poziomów: wartości poniżej progu przyjmują wartość "0" (czarne), a
    wartości >= progu przyjmują maksymalny poziom (np. 255, białe).
    Używane do segmentacji prostych obiektów, detekcji krawędzi i jako
    etap przetwarzania przed morfologią.
    """
    lut = np.zeros((levels,), dtype=np.uint8)
    for i in range(levels):
        lut[i] = np.uint8(0 if i < threshold else levels - 1)
    return lut


def threshold_keep_levels_lut(threshold: int, low_level: int, high_level: int, levels: int = 256) -> np.ndarray:
    """Create threshold LUT that maps below/above threshold to chosen levels.

    Variant progowania, gdzie zamiast domyślnych 0/255 użytkownik może
    wybrać, jakie wartości powinny przyjąć piksele poniżej i powyżej progu:
    - jeśli p < threshold -> mapuj do low_level
    - jeśli p >= threshold -> mapuj do high_level

    Przydatne, gdy chcemy zachować obraz w skali szarości, ale zamienić
    dwa zakresy na specyficzne reprezentatywne wartości (np. maski z
    niestandardowymi etykietami).
    """
    lut = np.zeros((levels,), dtype=np.uint8)
    for i in range(levels):
        lut[i] = np.uint8(low_level if i < threshold else high_level)
    return lut
