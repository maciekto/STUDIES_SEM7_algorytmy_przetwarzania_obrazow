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
from PyQt6.QtWidgets import QInputDialog


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
        # track last clicked ImageView to apply operations when multiple are open
        self._last_active_view = None

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
        # Undo / Redo
        self.actUndo = QAction("Cofnij", self)
        self.actUndo.setShortcut("Ctrl+Z")
        self.actUndo.triggered.connect(self._undo)

        self.actRedo = QAction("Ponów", self)
        self.actRedo.setShortcut("Ctrl+Y")
        self.actRedo.triggered.connect(self._redo)

    def _build_toolbar(self):
        """Zbudowanie menu w toolbar"""
        tb = QToolBar("Main")
        self.addToolBar(tb)
        for a in (self.actOpen, self.actSaveAs, self.actDuplicate, self.actDuplicateNewTab):
            tb.addAction(a)
        tb.addSeparator()
        for a in (self.actActual, self.actFit, self.actFill, self.actFull):
            tb.addAction(a)
        tb.addSeparator()
        tb.addAction(self.actUndo)
        tb.addAction(self.actRedo)

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

    def _set_last_active(self, view):
        self._last_active_view = view

    def _active_image_view(self) -> Optional[ImageView]:
        # prefer last active if it still exists in current tab
        if self._last_active_view is not None:
            # ensure it is still a child of current tab
            idx = self.tabs.currentIndex()
            if idx >= 0:
                cont = self.tabs.widget(idx)
                if isinstance(cont, QSplitter):
                    if self._last_active_view in cont.findChildren(ImageView):
                        return self._last_active_view
                elif isinstance(cont, ImageView):
                    return cont
        # fallback: find focused ImageView
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

    def _remove_view(self, view: ImageView) -> None:
        """Remove a single ImageView from whichever tab/splitter contains it.

        If the view is the only widget in its tab, the tab is closed. If the view
        is inside a splitter and after removal only one child remains, the
        splitter is replaced by that remaining widget to simplify the layout.
        """
        # find tab index that contains this view
        for i in range(self.tabs.count()):
            cont = self.tabs.widget(i)
            # direct widget
            if cont is view:
                self.tabs.removeTab(i)
                view.deleteLater()
                return
            # splitter container
            if isinstance(cont, QSplitter):
                children = cont.findChildren(ImageView)
                if view in children:
                    # remove the widget from splitter
                    view.setParent(None)
                    view.deleteLater()
                    # if splitter now has 0 children remove tab
                    remaining = [w for w in cont.findChildren(ImageView)]
                    if len(remaining) == 0:
                        self.tabs.removeTab(i)
                        cont.deleteLater()
                    elif len(remaining) == 1:
                        # replace splitter with the remaining widget
                        rem = remaining[0]
                        title = self.tabs.tabText(i)
                        # take rem out of splitter
                        rem.setParent(None)
                        self.tabs.removeTab(i)
                        self.tabs.insertTab(i, rem, title)
                        self.tabs.setCurrentIndex(i)
                    return

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
        view.clicked.connect(lambda v=view: self._set_last_active(v))
        view.closeRequested.connect(lambda v=view: self._remove_view(v))
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
        dup.clicked.connect(lambda v=dup: self._set_last_active(v))
        dup.closeRequested.connect(lambda v=dup: self._remove_view(v))
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
        dup.clicked.connect(lambda v=dup: self._set_last_active(v))
        dup.closeRequested.connect(lambda v=dup: self._remove_view(v))
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

    # ---------- undo/redo handling ----------
    def _undo(self):
        v = self._active_image_view()
        if not v:
            return
        ok = v.undo()
        if not ok:
            QMessageBox.information(self, "Cofnij", "Brak operacji do cofnięcia")

    def _redo(self):
        v = self._active_image_view()
        if not v:
            return
        ok = v.redo()
        if not ok:
            QMessageBox.information(self, "Ponów", "Brak operacji do ponowienia")
