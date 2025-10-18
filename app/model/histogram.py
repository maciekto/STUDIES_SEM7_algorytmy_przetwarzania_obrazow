"""Funkcje do wygenerowania histogramu

Wszystkie obliczenia histogramu są robione za pomocą iteracji na pixelach po tablicy
numpy bez pomocy OpenCV.
"""
from __future__ import annotations

from typing import Tuple
import numpy as np


def compute_lut(img: np.ndarray, levels: int = 256) -> np.ndarray:
    """Wyliczenie histogramu dla obrazu kolorowego lub szaro-odcieniowego

    Dla szaroodcieniowego generuje tablicę histogramu 1d długości wszystkich możliwych poziomów jasności
    gdzie h[i] jest ilością pixeli o tej jasności.

    Dla obrazów kolorowych generuje tablicę histogramu 2d gdzie wierszami tej tablicy są kanały r, g, b
    a kolumnami są wartości w tych kanałach
    """
    if img.ndim == 2: # ile wymiarów ma tablica (szaro-odcieniowy - wysokość x szerokość)
        histogram_array = np.zeros((levels,), dtype=np.int64)
        # flat iteration is still explicit counting
        for pixelValue in img.ravel():
            histogram_array[int(pixelValue)] += 1
        return histogram_array
    elif img.ndim == 3:
        canals_count = img.shape[2] # img.shape zwraca tuple (wysokość, szerokość, ilość_kanałów_rgb)
        histogram_array = np.zeros((canals_count, levels), dtype=np.int64)
        # iterate per channel
        for channel in range(canals_count): # iteruję po kanałach 0,1,2
            for channel_value in img[..., channel].ravel(): # teraz wykorzystuję do wzięcia wartości w ostatnim wymiarze tablicy ..., index channel
                histogram_array[channel, int(channel_value)] += 1 # zliczam do histogramu wiersz r g lub b (channel) i channel value
        return histogram_array
    else:
        raise ValueError("Unsupported image ndim: %s" % (img.ndim,))


def compute_cumhist(h: np.ndarray) -> np.ndarray:
    """Compute cumulative histogram H from histogram h.

    If h is 1D returns 1D cumulative array. If h is 2D (C x L) returns
    cumulative along last axis for each channel.
    """
    if h.ndim == 1:
        H = np.empty_like(h, dtype=np.int64)
        s = 0
        for i in range(h.shape[0]):
            s += int(h[i])
            H[i] = s
        return H
    elif h.ndim == 2:
        C, L = h.shape
        H = np.empty_like(h, dtype=np.int64)
        for ch in range(C):
            s = 0
            for i in range(L):
                s += int(h[ch, i])
                H[ch, i] = s
        return H
    else:
        raise ValueError("Unsupported histogram shape")


def stats_from_hist(h: np.ndarray) -> Tuple[float, int, float, int]:
    """Return (mean, median, std, count) computed from histogram h.

    Works for 1D histograms. For color histograms user should compute
    statistics per channel.
    """
    if h.ndim != 1:
        raise ValueError("stats_from_hist expects 1D histogram")
    L = h.shape[0]
    count = int(h.sum())
    if count == 0:
        return 0.0, 0, 0.0, 0

    # mean
    indices = np.arange(L, dtype=np.int64)
    mean = float((indices * h).sum() / count)

    # median: find first index where cumulative >= count/2
    cum = compute_cumhist(h)
    half = (count + 1) // 2
    median = int(np.searchsorted(cum, half))

    # std
    var = float(((indices - mean) ** 2 * h).sum() / count)
    std = float(np.sqrt(var))

    return mean, median, std, count
