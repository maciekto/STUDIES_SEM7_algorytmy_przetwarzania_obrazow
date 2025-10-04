"""Główne okno aplikacji z główną logiką ui"""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QTabWidget, QMessageBox, QToolBar, QApplication,
    QSplitter, QWidget
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
        """Ustawienie okna głównego (roota)"""
        super().__init__()
        self.setWindowTitle("APOZ - Przeglądarka")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(False)           # macOS: unikamy „X” bez tytułu
        self.tabs.setTabBarAutoHide(False)         # pasek kart zawsze widoczny
        self.setCentralWidget(self.tabs)

        self.tabs.setTabsClosable(True)
        self.tabs.setTabBarAutoHide(False)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self._build_actions()
        self._build_toolbar()
        self._build_menu()

    # ---------- UI ----------
    def _build_actions(self):
        """Zdefiniowanie wykonywanych akcji"""
        self.actOpen = QAction("Otwórz…", self)
        self.actOpen.setShortcut(QKeySequence.StandardKey.Open)
        self.actOpen.triggered.connect(self.open_images)

        self.actSaveAs = QAction("Zapisz jako…", self)
        self.actSaveAs.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.actSaveAs.triggered.connect(self.save_current_as)

        # Domyślnie Ctrl+D = side-by-side
        self.actDuplicate = QAction("Zduplikuj (obok siebie)", self)
        self.actDuplicate.setShortcut("Ctrl+D")
        self.actDuplicate.triggered.connect(self.duplicate_side_by_side)

        # Alternatywa: duplikat w nowej zakładce
        self.actDuplicateNewTab = QAction("Zduplikuj (nowa zakładka)", self)
        self.actDuplicateNewTab.setShortcut("Ctrl+Shift+D")
        self.actDuplicateNewTab.triggered.connect(self.duplicate_current)

        self.actFit = QAction("Dopasuj do okna", self, checkable=True)
        self.actFit.setShortcut("2")
        self.actFit.setChecked(True)
        self.actFit.triggered.connect(lambda: self._set_mode(ScaleMode.FIT))

        self.actActual = QAction("Oryginalny rozmiar", self, checkable=True)
        self.actActual.setShortcut("1")
        self.actActual.triggered.connect(lambda: self._set_mode(ScaleMode.ACTUAL))

        self.actFill = QAction("Wypełnij okno", self, checkable=True)
        self.actFill.setShortcut("3")
        self.actFill.triggered.connect(lambda: self._set_mode(ScaleMode.FILL))

        self.actFull = QAction("Zmaksymalizuj", self, checkable=False)
        self.actFull.setShortcut(QKeySequence(Qt.Key.Key_F11))
        self.actFull.triggered.connect(self._toggle_fullscreen)

        self.scale_group = [self.actActual, self.actFit, self.actFill]

    def _build_toolbar(self):
        """Zbudowanie menu w toolbar"""
        tb = QToolBar("Main")
        self.addToolBar(tb)
        for a in (self.actOpen, self.actSaveAs, self.actDuplicate, self.actDuplicateNewTab):
            tb.addAction(a)
        tb.addSeparator()
        for a in (self.actActual, self.actFit, self.actFill, self.actFull):
            tb.addAction(a)

    def _build_menu(self):
        """Zbudowanie menu w oknie głównym"""
        m = self.menuBar().addMenu("&Plik")
        m.addAction(self.actOpen)
        m.addAction(self.actSaveAs)
        m.addSeparator()
        m.addAction(self.actDuplicate)
        m.addAction(self.actDuplicateNewTab)
        m.addSeparator()
        exit_act = QAction("E&xit", self)
        exit_act.setShortcut(QKeySequence.StandardKey.Quit)
        exit_act.triggered.connect(QApplication.instance().quit)
        m.addAction(exit_act)

        v = self.menuBar().addMenu("&Widok")
        v.addAction(self.actActual)
        v.addAction(self.actFit)
        v.addAction(self.actFill)
        v.addSeparator()
        v.addAction(self.actFull)

    # ---------- Helpers ----------
    def _current_container(self) -> Optional[QWidget]:
        return self.tabs.currentWidget()

    def _active_image_view(self) -> Optional[ImageView]:
        fw = QApplication.focusWidget()
        if isinstance(fw, ImageView):
            return fw
        cont = self._current_container()
        if isinstance(cont, ImageView):
            return cont
        if isinstance(cont, QSplitter):
            views = cont.findChildren(ImageView)
            return views[0] if views else None
        return None

    def _set_mode(self, mode: str):
        for a in self.scale_group:
            a.setChecked(False)
        if mode == ScaleMode.ACTUAL:
            self.actActual.setChecked(True)
        elif mode == ScaleMode.FIT:
            self.actFit.setChecked(True)
        else:
            self.actFill.setChecked(True)

        cont = self._current_container()
        if isinstance(cont, ImageView):
            cont.set_mode(mode)
        elif isinstance(cont, QSplitter):
            for v in cont.findChildren(ImageView):
                v.set_mode(mode)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _ensure_splitter_for_current_tab(self) -> Optional[QSplitter]:
        """
        Jeśli aktywna zakładka ma pojedynczy ImageView, zamień ją na QSplitter (Horizontal)
        i włóż ten widok do splittera. Jeśli już jest splitter – zwróć go.
        """
        idx = self.tabs.currentIndex()
        if idx < 0:
            return None
        cont = self.tabs.widget(idx)
        if isinstance(cont, QSplitter):
            return cont
        if isinstance(cont, ImageView):
            splitter = QSplitter(Qt.Orientation.Horizontal, self)
            splitter.setChildrenCollapsible(False)
            cont.setParent(None)
            splitter.addWidget(cont)
            splitter.setStretchFactor(0, 1)
            title = self.tabs.tabText(idx)
            self.tabs.removeTab(idx)
            self.tabs.insertTab(idx, splitter, title if title else "image")
            self.tabs.setCurrentIndex(idx)
            return splitter
        return None

    def _close_tab(self, index: int) -> None:
        """Close and clean up the tab at `index`.
        """
        if index < 0 or index >= self.tabs.count():
            return
        widget = self.tabs.widget(index)
        # Remove the tab first, then schedule the widget for deletion.
        self.tabs.removeTab(index)
        if widget is not None:
            widget.deleteLater()

    # ---------- File ops ----------
    def open_images(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Open image(s)", "", IMG_FILTER)
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

        # W każdej karcie od razu trzymajmy splitter (1 panel startowy) – to stabilniejsze na macOS
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(view)
        splitter.setStretchFactor(0, 1)

        title = path.name if path else "untitled"
        self.tabs.addTab(splitter, title)
        self.tabs.setCurrentWidget(splitter)

    def save_current_as(self):
        # zapisuje aktywny ImageView (fokus/1. panel w karcie)
        v = self._active_image_view()
        if not v:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save image as…", "", IMG_FILTER)
        if not path:
            return
        try:
            save(v.doc.array, path)
            v.doc.path = Path(path)
            i = self.tabs.currentIndex()
            self.tabs.setTabText(i, v.doc.path.name if v.doc.path else "untitled")
        except Exception as e:
            QMessageBox.critical(self, "Save error", str(e))

    # ---------- Duplicate ----------
    def duplicate_current(self):
        """Kopia w nowej zakładce."""
        v = self._active_image_view()
        if not v or v.doc is None:
            return
        import numpy as np
        new_doc = ImageDoc(array=np.copy(v.doc.array), path=None)
        dup = ImageView(new_doc)
        dup.set_mode(v._mode)
        if v.pixmap():
            dup.set_pixmap(v.pixmap().copy())

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(dup)
        splitter.setStretchFactor(0, 1)

        title_src = v.doc.path.name if v.doc.path else "untitled"
        self.tabs.addTab(splitter, f"{title_src} (copy)")
        self.tabs.setCurrentWidget(splitter)

    def duplicate_side_by_side(self):
        """Kopia obok w tej samej zakładce (QSplitter poziomy)."""
        v = self._active_image_view()
        if not v or v.doc is None:
            return
        import numpy as np
        new_doc = ImageDoc(array=np.copy(v.doc.array), path=None)
        dup = ImageView(new_doc)
        dup.set_mode(v._mode)
        if v.pixmap():
            dup.set_pixmap(v.pixmap().copy())

        splitter = self._ensure_splitter_for_current_tab()
        if splitter is None:
            return
        splitter.addWidget(dup)
        last_index = splitter.count() - 1
        splitter.setStretchFactor(last_index, 1)
        splitter.setSizes([1] * splitter.count())
