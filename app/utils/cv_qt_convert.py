"""Utilities to convert OpenCV (NumPy) images to Qt QPixmap objects.

Qt (QImage/QPixmap) is used for display in PyQt widgets. OpenCV stores
images as NumPy arrays in BGR(A) order (or single-channel for grayscale). The
helpers here perform the small conversions needed so the arrays can be shown
in QLabel widgets.
"""

import cv2
import numpy as np
from PyQt6.QtGui import QImage, QPixmap


def cv_to_qpixmap(cv_img: np.ndarray) -> QPixmap:
    """Convert a NumPy/OpenCV image to QPixmap.

    Supports:
    - grayscale (2D arrays) -> QImage.Format_Grayscale8
    - 3-channel BGR -> converted to RGB and used with Format_RGB888
    - 4-channel BGRA -> converted to RGBA and used with Format_RGBA8888

    The function returns a QPixmap which can be set on a QLabel.
    """
    if cv_img is None:
        raise ValueError("cv_img is None")

    if cv_img.ndim == 2:  # grayscale
        h, w = cv_img.shape
        qimg = QImage(cv_img.data, w, h, w, QImage.Format.Format_Grayscale8)
    else:
        # 4 channels: BGRA -> RGBA
        if cv_img.shape[2] == 4:
            rgba = cv2.cvtColor(cv_img, cv2.COLOR_BGRA2RGBA)
            h, w, ch = rgba.shape
            qimg = QImage(rgba.data, w, h, ch * w, QImage.Format.Format_RGBA8888)
        else:
            # 3 channels: BGR -> RGB
            rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)

    return QPixmap.fromImage(qimg)
