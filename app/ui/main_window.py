from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QTabWidget, QMessageBox, QToolBar, QApplication
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt

from app.ui.image_view import ImageView, ScaleMode
from app.io.image_io import load, save
from app.utils.cv_qt_convert import cv_to_qpixmap
from app.model.image_store import ImageDoc


IMG_FILTER = "Images (*.bmp *.tif *.tiff *.png *.jpg *.jpeg)"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APOZ – Viewer (LAB1)")
        self.resize(1200, 800)

        self.tabs = QTabWidget(movable=True, tabsClosable=True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.setCentralWidget(self.tabs)

        self._build_actions()
        self._build_toolbar()
        self._build_menu()

    # ---------- UI ----------
    def _build_actions(self):
        self.actOpen = QAction("Open…", self)
        self.actOpen.setShortcut(QKeySequence.StandardKey.Open)
        self.actOpen.triggered.connect(self.open_images)

        self.actSaveAs = QAction("Save As…", self)
        self.actSaveAs.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.actSaveAs.triggered.connect(self.save_current_as)

        self.actDuplicate = QAction("Duplicate", self)
        self.actDuplicate.setShortcut("Ctrl+D")
        self.actDuplicate.triggered.connect(self.duplicate_current)

        self.actFit = QAction("Fit to window", self, checkable=True)
        self.actFit.setShortcut("2")
        self.actFit.setChecked(True)
        self.actFit.triggered.connect(lambda: self._set_mode(ScaleMode.FIT))

        self.actActual = QAction("Actual size (1:1)", self, checkable=True)
        self.actActual.setShortcut("1")
        self.actActual.triggered.connect(lambda: self._set_mode(ScaleMode.ACTUAL))

        self.actFill = QAction("Fill", self, checkable=True)
        self.actFill.setShortcut("3")
        self.actFill.triggered.connect(lambda: self._set_mode(ScaleMode.FILL))

        self.actFull = QAction("Toggle Full Screen", self, checkable=False)
        self.actFull.setShortcut(QKeySequence(Qt.Key.Key_F11))
        self.actFull.triggered.connect(self._toggle_fullscreen)

        self.scale_group = [self.actActual, self.actFit, self.actFill]

    def _build_toolbar(self):
        tb = QToolBar("Main")
        self.addToolBar(tb)
        for a in (self.actOpen, self.actSaveAs, self.actDuplicate):
            tb.addAction(a)
        tb.addSeparator()
        for a in (self.actActual, self.actFit, self.actFill, self.actFull):
            tb.addAction(a)

    def _build_menu(self):
        m = self.menuBar().addMenu("&File")
        m.addAction(self.actOpen)
        m.addAction(self.actSaveAs)
        m.addSeparator()
        m.addAction(self.actDuplicate)
        m.addSeparator()
        exit_act = QAction("E&xit", self)
        exit_act.setShortcut(QKeySequence.StandardKey.Quit)
        exit_act.triggered.connect(QApplication.instance().quit)
        m.addAction(exit_act)

        v = self.menuBar().addMenu("&View")
        v.addAction(self.actActual)
        v.addAction(self.actFit)
        v.addAction(self.actFill)
        v.addSeparator()
        v.addAction(self.actFull)

    # ---------- Actions ----------
    def _current_view(self) -> ImageView | None:
        w = self.tabs.currentWidget()
        return w if isinstance(w, ImageView) else None

    def _set_mode(self, mode: str):
        v = self._current_view()
        if not v:
            return
        # ekskluzywne zaznaczenie
        for a in self.scale_group:
            a.setChecked(False)
        if mode == ScaleMode.ACTUAL:
            self.actActual.setChecked(True)
        elif mode == ScaleMode.FIT:
            self.actFit.setChecked(True)
        else:
            self.actFill.setChecked(True)
        v.set_mode(mode)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _close_tab(self, idx: int):
        w = self.tabs.widget(idx)
        self.tabs.removeTab(idx)
        if w:
            w.deleteLater()

    # ---------- File ops ----------
    def open_images(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Open image(s)", "", IMG_FILTER
        )
        if not paths:
            return
        for path in paths:
            self._open_single(Path(path))

    def _open_single(self, path: Path):
        try:
            cv_img = load(str(path))
        except Exception as e:
            QMessageBox.critical(self, "Open error", str(e))
            return
        doc = ImageDoc(array=cv_img, path=path)
        view = ImageView(doc)
        view.set_mode(ScaleMode.FIT)
        view.set_pixmap(cv_to_qpixmap(cv_img))
        self.tabs.addTab(view, doc.title)
        self.tabs.setCurrentWidget(view)

    def save_current_as(self):
        v = self._current_view()
        if not v:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save image as…", "",
                                              IMG_FILTER)
        if not path:
            return
        try:
            save(v.doc.array, path)
            v.doc.path = Path(path)
            i = self.tabs.currentIndex()
            self.tabs.setTabText(i, v.doc.title)
        except Exception as e:
            QMessageBox.critical(self, "Save error", str(e))

    def duplicate_current(self):
        v = self._current_view()
        if not v or v.doc is None:
            return
        # kopiujemy macierz (nie-referencyjnie)
        import numpy as np
        new_doc = ImageDoc(array=np.copy(v.doc.array), path=None)
        dup = ImageView(new_doc)
        dup.set_mode(self.actFit.isChecked() and ScaleMode.FIT or ScaleMode.ACTUAL)
        dup.set_pixmap(v.pixmap())  # kopia QPixmap wystarczy do podglądu
        self.tabs.addTab(dup, f"{v.doc.title} (copy)")
        self.tabs.setCurrentWidget(dup)
