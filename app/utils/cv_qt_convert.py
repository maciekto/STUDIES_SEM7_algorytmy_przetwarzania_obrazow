import cv2
import numpy as np
from PyQt6.QtGui import QImage, QPixmap

def cv_to_qpixmap(cv_img: np.ndarray) -> QPixmap:
    if cv_img is None:
        raise ValueError("cv_img is None")

    if cv_img.ndim == 2:  # grayscale
        h, w = cv_img.shape
        qimg = QImage(cv_img.data, w, h, w, QImage.Format.Format_Grayscale8)
    else:
        if cv_img.shape[2] == 4:  # BGRA -> RGBA
            rgba = cv2.cvtColor(cv_img, cv2.COLOR_BGRA2RGBA)
            h, w, ch = rgba.shape
            qimg = QImage(rgba.data, w, h, ch * w, QImage.Format.Format_RGBA8888)
        else:  # BGR -> RGB
            rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)

    return QPixmap.fromImage(qimg)
