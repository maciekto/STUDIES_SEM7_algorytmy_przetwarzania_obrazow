"""Manual histogram drawing into an image buffer.

This module creates an RGB image representing the histogram as a bar plot
and writes simple axis labels and statistics. It does not use any plotting
library — drawing primitives are OpenCV calls which are allowed for
presentation.
"""
from __future__ import annotations

from typing import Optional, Tuple
import numpy as np
import cv2


def render_histogram(h: np.ndarray, size: Tuple[int, int] = (480, 200), title: str = "Histogram", stats: Optional[dict] = None, bar_color: Tuple[int,int,int]=(50,120,200)) -> np.ndarray:
    """Render histogram `h` into an RGB image of given `size` (w,h).

    h is 1D array of bin counts. The function normalizes bar heights to fit
    the plotting area and draws axis ticks and optional stats text.
    """
    W, H = size
    canvas = np.ones((H, W, 3), dtype=np.uint8) * 255

    # plotting area margins
    left, right, top, bottom = 40, 10, 20, 30
    plot_w = W - left - right
    plot_h = H - top - bottom

    # draw box
    cv2.rectangle(canvas, (left, top), (left + plot_w, top + plot_h), (0, 0, 0), 1)

    L = h.shape[0]
    if L == 0:
        return canvas

    max_h = int(h.max())
    # normalize heights to plot_h
    norm = (plot_h - 2) / max_h if max_h > 0 else 0.0

    # determine bar width (at least 1 px)
    bar_w = max(1, plot_w // L)

    for i in range(L):
        bin_val = int(h[i])
        bar_h = int(round(bin_val * norm))
        x1 = left + i * bar_w
        x2 = x1 + bar_w - 1
        y1 = top + plot_h - 1
        y2 = y1 - bar_h
        cv2.rectangle(canvas, (x1, y2), (x2, y1), bar_color, -1)

    # axes ticks (0, mid, max)
    cv2.putText(canvas, "0", (5, top + plot_h), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    cv2.putText(canvas, str(max_h), (5, top + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

    # x axis labels: 0, mid, L-1
    cv2.putText(canvas, "0", (left, H - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    mid_x = left + plot_w // 2
    cv2.putText(canvas, str(L // 2), (mid_x - 10, H - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    cv2.putText(canvas, str(L - 1), (left + plot_w - 20, H - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

    # title
    cv2.putText(canvas, title, (left + 5, top - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    # stats text
    if stats:
        lines = [f"mean: {stats.get('mean', 0):.2f}", f"median: {stats.get('median', 0)}", f"std: {stats.get('std', 0):.2f}", f"count: {stats.get('count', 0)}"]
        y = top
        for line in lines:
            cv2.putText(canvas, line, (left + plot_w + 5, y + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            y += 16

    return canvas
