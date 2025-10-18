from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from app.controller import actions
from app.ui.hist_canvas import render_histogram
from app.utils.cv_qt_convert import cv_to_qpixmap
from app.model.image_store import ImageDoc


class HistWindow(QWidget):
    """A small tool window showing histogram for an ImageDoc.

    The window contains a combo box allowing selection between combined/red/green/blue
    (if the image has channels). On selection change the histogram is recomputed
    (from precomputed channel histograms) and redrawn.
    """

    def __init__(self, parent, doc: ImageDoc):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle(f"Histogram — {doc.title}")
        self._doc = doc

        # compute hist once
        info = actions.compute_histogram(doc)
        self._h = info.get("h")
        self._stats = info.get("stats", [])

        self._combo = QComboBox(self)
        items = ["combined"]
        # if color image add channels
        if getattr(self._h, 'ndim', 1) == 2:
            items.extend(["red", "green", "blue"])
        self._combo.addItems(items)
        self._combo.currentIndexChanged.connect(self._on_choice)

        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # zoom controls
        self._zoom = 1.0
        btn_zoom_in = QPushButton("+", self)
        btn_zoom_out = QPushButton("-", self)
        btn_zoom_in.clicked.connect(self._zoom_in)
        btn_zoom_out.clicked.connect(self._zoom_out)

        hl = QHBoxLayout()
        hl.addWidget(self._combo)
        hl.addWidget(btn_zoom_out)
        hl.addWidget(btn_zoom_in)

        v = QVBoxLayout(self)
        v.addLayout(hl)
        v.addWidget(self._label)

        # initial draw
        self._on_choice(0)

    def _on_choice(self, idx: int):
        choice = self._combo.currentText()
        bar_color = (120, 120, 120)
        if getattr(self._h, 'ndim', 1) == 2:
            if choice == 'combined':
                h_disp = self._h.sum(axis=0)
                stats = self._stats[0] if self._stats else None
                bar_color = (120, 120, 120)
            else:
                idxmap = {"blue": 0, "green": 1, "red": 2}
                ch = idxmap.get(choice, 0)
                if ch >= self._h.shape[0]:
                    h_disp = self._h.sum(axis=0)
                    stats = self._stats[0] if self._stats else None
                    bar_color = (120, 120, 120)
                else:
                    h_disp = self._h[ch]
                    stats = self._stats[ch] if ch < len(self._stats) else None
                    # OpenCV uses BGR order for colors in drawing primitives
                    if choice == 'red':
                        bar_color = (0, 0, 255)
                    elif choice == 'green':
                        bar_color = (0, 255, 0)
                    else:
                        bar_color = (255, 0, 0)
        else:
            h_disp = self._h
            stats = self._stats[0] if self._stats else None

        stats_dict = {}
        if stats:
            mean, median, std, count = stats
            stats_dict = {"mean": mean, "median": median, "std": std, "count": count}

        # apply zoom factor to base size
        base_w, base_h = 640, 240
        W = max(200, int(base_w * self._zoom))
        H = max(80, int(base_h * self._zoom))
        canvas = render_histogram(h_disp, size=(W, H), title=f"Histogram ({choice})", stats=stats_dict, bar_color=bar_color)
        pix = cv_to_qpixmap(canvas)
        self._label.setPixmap(pix)

    def _zoom_in(self):
        self._zoom *= 1.25
        self._on_choice(self._combo.currentIndex())

    def _zoom_out(self):
        self._zoom = max(0.2, self._zoom / 1.25)
        self._on_choice(self._combo.currentIndex())
