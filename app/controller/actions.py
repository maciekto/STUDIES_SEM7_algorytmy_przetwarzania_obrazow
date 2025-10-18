"""High level actions using model functions.

These helpers operate on ImageDoc objects and return new ImageDoc results
without mutating inputs (pipeline immutability).
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
from app.model.image_store import ImageDoc
from app.model import histogram, mapping, point_ops


def compute_histogram(doc: ImageDoc) -> dict:
    h = histogram.compute_lut(doc.array)
    if h.ndim == 2:
        stats = [histogram.stats_from_hist(hc) for hc in h]
    else:
        stats = [histogram.stats_from_hist(h)]
    return {"h": h, "stats": stats}


def stretch_linear(doc: ImageDoc, clip_frac: float | None = None) -> ImageDoc:
    arr = doc.array
    if arr.ndim == 2:
        h = histogram.compute_lut(arr)
        lut = mapping.stretch_linear_from_hist(h, levels=256, clip_frac=clip_frac)
        out = mapping.apply_lut(arr, lut)
    else:
        out_ch = []
        for ch in range(arr.shape[2]):
            h = histogram.compute_lut(arr[..., ch])
            lut = mapping.stretch_linear_from_hist(h, levels=256, clip_frac=clip_frac)
            out_ch.append(mapping.apply_lut(arr[..., ch], lut))
        out = np.stack(out_ch, axis=2)
    return ImageDoc(array=out, path=None)


def equalize_selective(doc: ImageDoc) -> ImageDoc:
    arr = doc.array
    if arr.ndim == 2:
        h = histogram.compute_lut(arr)
        lut = mapping.equalize_selective_from_hist(h)
        out = mapping.apply_lut(arr, lut)
    else:
        out_ch = []
        for ch in range(arr.shape[2]):
            h = histogram.compute_lut(arr[..., ch])
            lut = mapping.equalize_selective_from_hist(h)
            out_ch.append(mapping.apply_lut(arr[..., ch], lut))
        out = np.stack(out_ch, axis=2)
    return ImageDoc(array=out, path=None)


def apply_point_lut(doc: ImageDoc, lut: np.ndarray) -> ImageDoc:
    arr = doc.array
    if arr.ndim == 2:
        out = mapping.apply_lut(arr, lut)
    else:
        out_ch = []
        for ch in range(arr.shape[2]):
            out_ch.append(mapping.apply_lut(arr[..., ch], lut))
        out = np.stack(out_ch, axis=2)
    return ImageDoc(array=out, path=None)
