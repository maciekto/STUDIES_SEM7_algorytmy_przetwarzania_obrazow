from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class ScaleMode:
    ACTUAL_SIZE = "actual"
    FIT_TO_WINDOW = "fit"
    FILL = "fill"  # opcjonalnie

class ImageView(QLabel):
    def __init__(self):
        super().__init__()
        self.setBackgroundRole(self.backgroundRole())
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setScaledContents(False)
        self._pix: QPixmap | None = None
        self._mode = ScaleMode.FIT_TO_WINDOW
        self._zoom = 1.0

    def set_pixmap(self, pix: QPixmap):
        self._pix = pix
        self._zoom = 1.0
        self.update_view()

    def set_mode(self, mode: str):
        self._mode = mode
        self.update_view()

    def wheelEvent(self, e):
        if self._mode == ScaleMode.ACTUAL_SIZE:
            step = 1.1 if e.angleDelta().y() > 0 else 1/1.1
            self._zoom = max(0.1, min(8.0, self._zoom * step))
            self.update_view()

    def resizeEvent(self, _):
        self.update_view()

    def update_view(self):
        if not self._pix:
            self.clear()
            return
        if self._mode == ScaleMode.ACTUAL_SIZE:
            w = round(self._pix.width() * self._zoom)
            h = round(self._pix.height() * self._zoom)
            self.setPixmap(self._pix.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation))
        elif self._mode == ScaleMode.FIT_TO_WINDOW:
            self.setPixmap(self._pix.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation))
        else:  # FILL
            self.setPixmap(self._pix.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation))
