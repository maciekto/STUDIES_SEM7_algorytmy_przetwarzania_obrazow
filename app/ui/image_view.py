from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from app.model.image_store import ImageDoc
from typing import Optional

class ScaleMode:
    ACTUAL = "actual"           # 1:1 + zoom (scroll)
    FIT = "fit"                 # dopasuj z zachowaniem proporcji
    FILL = "fill"               # wypełnij (bez proporcji)

class ImageView(QLabel):
    def __init__(self, doc: ImageDoc):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pix: Optional[QPixmap] = None
        self._doc = doc
        self._mode = ScaleMode.FIT
        self._zoom = 1.0

    # dostęp do dokumentu (np. przy zapisie)
    @property
    def doc(self) -> ImageDoc:
        return self._doc

    def set_pixmap(self, pix: QPixmap):
        self._pix = pix
        self._zoom = 1.0
        self.update_view()

    def set_mode(self, mode: str):
        self._mode = mode
        # FIT/FILL skalują się z rozmiarem okna, ACTUAL zostaje 1:1
        self.update_view()

    def wheelEvent(self, e):
        if self._mode == ScaleMode.ACTUAL and self._pix:
            step = 1.1 if e.angleDelta().y() > 0 else 1/1.1
            self._zoom = max(0.1, min(8.0, self._zoom * step))
            self.update_view()

    def resizeEvent(self, _):
        if self._mode in (ScaleMode.FIT, ScaleMode.FILL):
            self.update_view()

    def update_view(self):
        if not self._pix:
            self.clear()
            return
        if self._mode == ScaleMode.ACTUAL:
            w = round(self._pix.width() * self._zoom)
            h = round(self._pix.height() * self._zoom)
            self.setPixmap(self._pix.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation))
        elif self._mode == ScaleMode.FIT:
            self.setPixmap(self._pix.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation))
        else:  # FILL
            self.setPixmap(self._pix.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation))
