"""Widget that shows a single image (QPixmap) with simple scaling modes.

ImageView is a thin QLabel subclass that keeps a QPixmap and draws it
according to the selected ScaleMode. It supports:
- ACTUAL: 1:1 drawing with mouse-wheel zoom
- FIT: scale to widget preserving aspect ratio
- FILL: scale to widget ignoring aspect ratio
"""

from PyQt6.QtWidgets import QLabel, QSizePolicy, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from app.model.image_store import ImageDoc
from typing import Optional
import numpy as np


class ScaleMode:
    ACTUAL = "actual"           # 1:1 + zoom (scroll)
    FIT = "fit"                 # fit while keeping aspect ratio
    FILL = "fill"               # fill the widget without keeping aspect


class ImageView(QLabel):
    clicked = pyqtSignal()
    closeRequested = pyqtSignal()
    def __init__(self, doc: ImageDoc):
        super().__init__()
        # Make the widget stretchable inside layouts/splitters
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(50)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._pix: Optional[QPixmap] = None
        self._doc = doc
        self._mode = ScaleMode.FIT
        self._zoom = 1.0
        # undo/redo stacks store numpy arrays (copies)
        self._undo_stack: list[np.ndarray] = []
        self._redo_stack: list[np.ndarray] = []

    @property
    def doc(self) -> ImageDoc:
        return self._doc

    def set_pixmap(self, pix: QPixmap | None):
        """Set the internal pixmap (usually created via cv_to_qpixmap)."""
        self._pix = pix
        self._zoom = 1.0
        self.update_view()

    def set_mode(self, mode: str):
        self._mode = mode
        self.update_view()

    def wheelEvent(self, e):
        # When in ACTUAL mode the wheel scales the zoom factor
        if self._mode == ScaleMode.ACTUAL and self._pix:
            step = 1.1 if e.angleDelta().y() > 0 else 1 / 1.1
            self._zoom = max(0.1, min(8.0, self._zoom * step))
            self.update_view()

    def mousePressEvent(self, e):
        # give focus to this view and emit clicked so MainWindow can track
        # which image is active when multiple views are open side-by-side.
        self.setFocus()
        self.clicked.emit()
        super().mousePressEvent(e)

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        act_close = menu.addAction("Zamknij widok")
        act = menu.exec(e.globalPos())
        if act == act_close:
            self.closeRequested.emit()

    # ---------- undo/redo support ----------
    def push_undo(self):
        # push a copy of current array to undo stack and clear redo stack
        self._undo_stack.append(np.copy(self._doc.array))
        # limit stack to reasonable size
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        prev = self._undo_stack.pop()
        # push current to redo
        self._redo_stack.append(np.copy(self._doc.array))
        self._doc.array = prev
        # update pixmap
        if self._pix:
            # regenerate pixmap from array
            from app.utils.cv_qt_convert import cv_to_qpixmap

            self.set_pixmap(cv_to_qpixmap(self._doc.array))
        else:
            self.update_view()
        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False
        nxt = self._redo_stack.pop()
        self._undo_stack.append(np.copy(self._doc.array))
        self._doc.array = nxt
        from app.utils.cv_qt_convert import cv_to_qpixmap

        self.set_pixmap(cv_to_qpixmap(self._doc.array))
        return True

    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    def resizeEvent(self, _):
        # In FIT/FILL modes we need to recalc the drawn pixmap on resize
        if self._mode in (ScaleMode.FIT, ScaleMode.FILL):
            self.update_view()

    def update_view(self):
        """Re-render the stored QPixmap according to the current mode."""
        if not self._pix:
            self.clear()
            return
        if self._mode == ScaleMode.ACTUAL:
            w = round(self._pix.width() * self._zoom)
            h = round(self._pix.height() * self._zoom)
            self.setPixmap(
                self._pix.scaled(
                    w,
                    h,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        elif self._mode == ScaleMode.FIT:
            self.setPixmap(
                self._pix.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:  # FILL
            self.setPixmap(
                self._pix.scaled(
                    self.size(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
