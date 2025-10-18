"""Histogram-based mappings: linear stretch, equalization and LUT application.

All mapping algorithms are implemented manually without cv.LUT or cv.equalizeHist.
"""
from __future__ import annotations

import numpy as np
from typing import Tuple


def apply_lut(img: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Apply LUT to image and return new array.

    Supports 2D grayscale and 3D color images. The lut is expected to be
    a 1D array of length M, or for color images a (C, M) array.
    """
    if img.ndim == 2:
        out = np.empty_like(img)
        for i, v in enumerate(img.ravel()):
            out.ravel()[i] = np.uint8(lut[int(v)])
        return out
    elif img.ndim == 3:
        H, W, C = img.shape
        out = np.empty_like(img)
        if lut.ndim == 1:
            # same lut for all channels
            for ch in range(C):
                for idx, v in enumerate(img[..., ch].ravel()):
                    out[..., ch].ravel()[idx] = np.uint8(lut[int(v)])
        else:
            for ch in range(C):
                for idx, v in enumerate(img[..., ch].ravel()):
                    out[..., ch].ravel()[idx] = np.uint8(lut[ch, int(v)])
        return out
    else:
        raise ValueError("Unsupported image ndim")


def stretch_linear_from_hist(h: np.ndarray, levels: int = 256, clip_frac: float | None = None) -> np.ndarray:
    """Create a LUT performing linear contrast stretch.

    If clip_frac is None do non-clipping: find first/last non-zero bins as min/max.
    If clip_frac is a float e.g. 0.05, then remove up to clip_frac fraction of
    pixels from both ends cumulatively (total clipped <= clip_frac).

    Returns integer LUT of length `levels`.
    """
    if h.ndim != 1:
        raise ValueError("stretch_linear_from_hist expects 1D histogram")
    total = int(h.sum())
    L = h.shape[0]

    if total == 0:
        return np.arange(L, dtype=np.uint8)

    if clip_frac is None:
        # find min non-zero and max non-zero
        nz = np.nonzero(h)[0]
        if nz.size == 0:
            zmin, zmax = 0, L - 1
        else:
            zmin, zmax = int(nz[0]), int(nz[-1])
    else:
        # clip up to clip_frac fraction of pixels total
        clip_total = int(total * clip_frac + 0.5)
        # split clipping to low and high roughly equally
        clip_low = clip_total // 2
        clip_high = clip_total - clip_low

        # find zmin where cumulative > clip_low
        cum = np.cumsum(h)
        zmin = int(np.searchsorted(cum, clip_low))
        # for high, find from top
        cum_rev = np.cumsum(h[::-1])
        zmax = L - 1 - int(np.searchsorted(cum_rev, clip_high))
        if zmax < zmin:
            zmin, zmax = 0, L - 1

    # avoid division by zero
    if zmax == zmin:
        lut = np.clip(np.arange(L), 0, L - 1).astype(np.uint8)
        return lut

    lut = np.zeros((L,), dtype=np.uint8)
    for i in range(L):
        if i <= zmin:
            v = 0
        elif i >= zmax:
            v = L - 1
        else:
            v = round((i - zmin) / (zmax - zmin) * (L - 1))
        lut[i] = np.uint8(v)
    return lut


def equalize_selective_from_hist(h: np.ndarray, levels: int = 256) -> np.ndarray:
    """Build selective equalization LUT from histogram h according to formula:

    D[i] = (h0+...+hi) / sum
    LUT'[i] = ((D[i] - D0) / (1 - D0)) * (M-1)

    where D0 is first non-zero value of D.
    """
    if h.ndim != 1:
        raise ValueError("equalize_selective_from_hist expects 1D histogram")
    total = int(h.sum())
    L = h.shape[0]
    if total == 0:
        return np.arange(L, dtype=np.uint8)

    cum = np.cumsum(h).astype(np.float64) / float(total)
    # find D0: first cum > 0
    nz = np.nonzero(cum > 0)[0]
    D0 = float(cum[nz[0]]) if nz.size > 0 else 0.0

    lut = np.zeros((L,), dtype=np.uint8)
    denom = 1.0 - D0 if (1.0 - D0) > 0 else 1.0
    for i in range(L):
        val = (cum[i] - D0) / denom
        val = max(0.0, min(1.0, val))
        lut[i] = np.uint8(round(val * (levels - 1)))
    return lut
