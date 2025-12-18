# image_window.py
import numpy as np
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QMainWindow, QLabel, QScrollArea, QFileDialog, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt, QSize
import cv2

from histogram_plot_dialog import HistogramPlotDialog
from image_selection_dialog import ImageSelectionDialog
from utils import convert_cv_to_pixmap
from algorithms import generate_lut_histogram, linear_streching_histogram, \
    linear_saturation_streching_histogram, histogram_equalization, point_negation, point_posterize, \
    point_binary_threshold, point_keep_gray_threshold


class ImageWindow(QMainWindow):
    def __init__(self, cv_image: np. ndarray, title: str = "Obraz", main_app_window=None):
        super().__init__()
        self.setWindowTitle(title)
        self.main_app_window = main_app_window  # Referencja do okna głównego zawierającego listę otwartych okien
        self._child_windows = []  # Tablica przechowująca okna wynikowe operacji lub wykresy

        self.cv_image = cv_image  # Przechowuje oryginał w formacie OpenCV (tablica NumPy)
        self.pixmap = convert_cv_to_pixmap(cv_image)  # Przechowuje pixmap-ę
        self.view_mode = "aspect_fit"  # Ustawiam aktualny tryb aspect_fit/fit/original

        # Ustawienie GUI do wyświetlania
        self.scroll_area = QScrollArea()  # Ustawienie scroll-u, gdy zmniejszę okno
        self.label_image = QLabel()  # Bez tego nie będzie gdzie wyświetlić Pixmap-y
        self.label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Ustawia wyrównanie obrazu w QLabel na środek
        self.scroll_area.setWidget(self.label_image)  # Osadza QLabel w obszarze przewijania scroll_area
        self.scroll_area.setWidgetResizable(True)  # Włącza zmianę wielkości okna
        self.setCentralWidget(self.scroll_area)  # Ustawia QScrollArea jako jedyny, wypełniający

        self.show_image()  # Wyświetlenie obrazu

        self.create_menus()  # Menu okna ze zdjęciem

    def show_image(self):
        """Odświeża widok w oknie na podstawie self.cv_image"""
        if self.pixmap:
            # Ustawienie pixmap-y jako zawartości obiektu QLabel
            self.label_image.setPixmap(self.pixmap)

            # Dopasowanie rozmiaru okna do zdjęcia z marginesami 20 px, maksymalna wielkość okna to 800x600px
            self.resize(min(self.pixmap.width() + 20, 800), min(self.pixmap.height() + 20, 600))

    def create_menus(self):
        menu_bar = self.menuBar()

        file = menu_bar.addMenu("File")  # Zakłada dla zapisania/wczytania/duplikacji obrazu
        file_open = file.addAction("Otwórz")
        file_open.triggered.connect(self.on_file_open_triggered)

        file_duplicate = file.addAction("Duplikuj")
        file_duplicate.triggered.connect(self.on_file_duplicate_triggered)

        file_save = file.addAction("Zapisz jako")
        file_save.triggered.connect(self.on_file_save_triggered)

        view = menu_bar.addMenu("View")  # Zakładka dla operacji widoku: dopasowanie do okna, wypełniony, oryginał

        view_aspect_fit = view.addAction("Wypełnienie z zachowaniem proporcji")
        view_aspect_fit.triggered.connect(self.on_view_aspect_fit_triggered)

        view_fit = view.addAction("Dopasowanie do okna")
        view_fit.triggered.connect(self.on_view_fit_triggered)

        view_original = view.addAction("Oryginalny")
        view_original.triggered.connect(self.on_view_original_triggered)

        # Menu dla lab-ów 1
        lab1_menu = menu_bar.addMenu("Lab 1")

        ui_action_hist = lab1_menu.addAction("Zad 2 i 3 - Pokaż Histogram i tablicę LUT")
        ui_action_hist.triggered.connect(lambda: self.on_action_histogram_triggered(self.cv_image))

        ui_linear_streching = lab1_menu.addAction("Zad 3 - rozciągnięcie liniowe")
        ui_linear_streching.triggered.connect(lambda: self.on_action_linear_streching_triggered(self.cv_image))

        ui_linear_saturation_streching = lab1_menu.addAction("Zad 3 - rozciągnięcie liniowe z saturacją")
        (ui_linear_saturation_streching.triggered.
         connect(lambda: self.on_action_linear_saturation_streching_triggered(self.cv_image)))

        ui_histogram_equalization = lab1_menu.addAction("Zad 3 - equalizacja histogramu")
        (ui_histogram_equalization.triggered.
         connect(lambda: self.on_histogram_equalization_triggered(self.cv_image)))

        ui_point_negation = lab1_menu.addAction("Zad 4 - Negacja")
        ui_point_negation.triggered.connect(lambda: self.on_point_negation_triggered(self.cv_image))

        ui_point_posterize = lab1_menu.addAction("Zad 4 - Redukcja poziomów szarości (posteryzacja)")
        ui_point_posterize.triggered.connect(lambda: self.on_point_posterize_triggered(self.cv_image))

        ui_point_threshold = lab1_menu.addAction("Zad 4 - Progowanie binarne")
        ui_point_threshold.triggered.connect(lambda: self.on_point_binary_threshold_triggered(self.cv_image))

        ui_keep_gray_threshold = lab1_menu.addAction("Zad 4 - Progowanie z zachowaniem szarości")
        ui_keep_gray_threshold.triggered.connect(lambda: self.on_keep_gray_threshold_triggered(self.cv_image))

        # Menu dla lab-ów 2
        lab2_menu = menu_bar.addMenu("Lab 2")

        ui_select_windows_test = lab2_menu.addAction("Select images")
        ui_select_windows_test.triggered.connect(self.select_additional_images)


    # ------------------------------
    # MENU FILE OPTIONS METHODS
    # ------------------------------

    def on_file_open_triggered(self):
        self.main_app_window.open_image_dialog()

    def on_file_duplicate_triggered(self):

        # Bez użycia cv_image.copy() przekazana zostałaby referencja i wtedy edytując jedno zdjęcie zmiany byłyby na 2
        duplicated_image = ImageWindow(self.cv_image.copy(), title=f'(Copy) {self.windowTitle()}')
        duplicated_image.show()

        # Dodanie okna do listy przechowywanych referencji dla garbage collector-a, żeby nie usuwał
        self.main_app_window.open_windows.append(duplicated_image)

        def cleanup():
            if duplicated_image in self.main_app_window.open_windows:
                self.main_app_window.open_windows.remove(duplicated_image)

        # Kiedy okno jest zamknięte przez użytkownika zostaje usunięte z listy
        duplicated_image.destroyed.connect(cleanup)

    def on_file_save_triggered(self):

        # Wywołanie okna zapisu
        file_path, _ = QFileDialog.getSaveFileName(
            None,  # Rodzic
            "Zapisz obraz jako...",  # Tytuł okna
            self.windowTitle(),  # Domyślna nazwa
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;TIFF (*.tif)"  # Filtry
        )

        # Sprawdzenie, czy użytkownik wybrał nazwę i miejsce zapisu
        if file_path:
            # Funkcja sama wybiera format z nazwy wybranej przez użytkownika
            cv2.imwrite(file_path, self.cv_image)

    # ------------------------------
    # MENU VIEW OPTIONS METHODS
    # ------------------------------
    def on_view_aspect_fit_triggered(self):
        self.view_mode = 'aspect_fit'
        # Ustawienie wielkości minimalnej
        self.label_image.setMinimumSize(40, 40)
        self.scroll_area.setWidgetResizable(True)
        self.label_image.setScaledContents(False)

    def on_view_fit_triggered(self):
        self.view_mode = 'fit'
        # Ustawia skalowanie w QLabel
        self.label_image.setScaledContents(True)
        # Pozwala na resize
        self.scroll_area.setWidgetResizable(True)
        # Wymusza to, że QLabel będzie mogło zmniejszać rozmiar pixmap-y
        self.label_image.setMinimumSize(1, 1)

    def on_view_original_triggered(self):
        self.view_mode = 'original'
        # Usuwam ustawienie 1,1 z opcji fit
        self.label_image.setMinimumSize(0, 0)
        # Wyłączam skalowanie
        self.label_image.setScaledContents(False)
        # Ustawia Resize dla obiektu ze zdjęciem
        self.scroll_area.setWidgetResizable(True)

        # Zmienia rozmiar tak, aby pomieścić swoją zawartość
        self.label_image.adjustSize()

    # ------------------------------
    # MENU VIEW HELPERS METHODS
    # ------------------------------
    def resizeEvent(self, event: QResizeEvent):
        """Nadpisanie metody udostępnianej przez PyQt wywoływanej po zmianie wielkości okna"""

        if self.view_mode == "aspect_fit" and self.scroll_area.widgetResizable():
            self.view_aspect_fit_resize_event()

        super().resizeEvent(event)

    def view_aspect_fit_resize_event(self):
        """Wywoływana w nadpisaniu metody resizeEvent za każdym razem,
        gdy podczas trybu widoku = aspect_fit zmienia się wielkość okna"""

        # Pobieram aktualny maksymalny obszar roboczy jako 2D obiekt QSize
        full_view_size = self.scroll_area.viewport().size()

        # Ustawiam margines od zdjęcia do końca okna
        margin = 50  # /2

        # Ustawiam rozmiar zdjęcia mniejszy o margines.
        # UWAGA: Margines będzie 2 razy mniejszy ze względu na dwie strony i automatyczne centrowanie przez QLabel
        width_scaled_with_margin = full_view_size.width() - margin
        height_scaled_with_margin = full_view_size.height() - margin

        # Sprawdzenie, czy obliczona szerokość i wysokość nie są mniejsze od zera
        if width_scaled_with_margin <= 0 or height_scaled_with_margin <= 0:
            return

        # Zapisanie obliczonych rozmiarów do obiektu QSize
        max_view_size = QSize(width_scaled_with_margin, height_scaled_with_margin)

        # Obliczenie nowej pixmap-y
        scaled_pixmap = self.pixmap.scaled(
            max_view_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Ustawienie nowej pixmap-y w QLabel-u
        self.label_image.setPixmap(scaled_pixmap)

        # Automatyczne dostosowanie okna do aktualnej zawartości
        self.label_image.adjustSize()

    # ------------------------------
    # MENU LAB1 OPTIONS METHODS
    # ------------------------------

    # Zadanie 2
    def on_action_histogram_triggered(self, image_data):
        # Ta funkcja zostanie wywołana PRZY KLIKNIĘCIU
        histogram_data = generate_lut_histogram(image_data)
        histogram_dialog = None
        try:
            histogram_dialog = HistogramPlotDialog(histogram_data, self)
        except Exception as e:
            print(f"Błąd podczas tworzenia HistogramPlotDialog: {e}")
            return

        if histogram_dialog:
            histogram_dialog.show()

            self._child_windows.append(histogram_dialog)

            def cleanup():
                if histogram_dialog in self._child_windows:
                    self._child_windows.remove(histogram_dialog)

            # Usunięcie referencji, gdy użytkownik zamknie okno
            histogram_dialog.destroyed.connect(cleanup)

    # Zadanie 3
    def on_action_linear_streching_triggered(self, image_data):
        self.cv_image = linear_streching_histogram(image_data)
        self.pixmap = convert_cv_to_pixmap(self.cv_image)
        self.show_image()

    def on_action_linear_saturation_streching_triggered(self, image_data):
        self.cv_image = linear_saturation_streching_histogram(image_data)
        self.pixmap = convert_cv_to_pixmap(self.cv_image)
        self.show_image()

    def on_histogram_equalization_triggered(self, image_data):
        self.cv_image = histogram_equalization(image_data)
        self.pixmap = convert_cv_to_pixmap(self.cv_image)
        self.show_image()

    # Zadanie 4

    def ensure_grayscale(self):
        """
        Funkcja pomocnicza sprawdzająca, czy obraz jest w odcieniach szarości i w wypadku, gdy nie jest,
        prosi użytkownika o potwierdzenie zamienienia w celu wykonania operacji
        :return:
        """
        if len(self.cv_image.shape) == 3:
            reply = QMessageBox.question(self, "Konwersja",
                                         "Operacja wymaga obrazu w odcieniach szarości. Czy skonwertować?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.cv_image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2GRAY)
                self.pixmap = convert_cv_to_pixmap(self.cv_image)
                self.show_image()
                return True
            else:
                return False
        return True

    def on_point_negation_triggered(self, image_data: np.ndarray):
        self.cv_image = point_negation(image_data)
        self.pixmap = convert_cv_to_pixmap(self.cv_image)
        self.show_image()

    def on_point_posterize_triggered(self, image_data: np.ndarray):
        # Okno, w którym użytkownik wpisuje ilość poziomó∑
        levels, ok = QInputDialog.getInt(self, "Posteryzacja",
                                         "Podaj liczbę poziomów:", value=4, min=2, max=255, step=1)
        if ok:
            self.cv_image = point_posterize(image_data, levels)
            self.pixmap = convert_cv_to_pixmap(self.cv_image)
            self.show_image()

    def on_point_binary_threshold_triggered(self, image_data: np.ndarray):
        is_image_grayscale = self.ensure_grayscale()

        # Jeżeli użytkownik nie wyraził zgody wychodzę z funkcji
        if not is_image_grayscale:
            return False

        threshold, ok = QInputDialog.getInt(self, "Progowanie binarne",
                                            "Podaj próg progowania(0-255): ",
                                            value=127, min=0, max=255)
        if ok:
            self.cv_image = point_binary_threshold(self.cv_image, threshold)
            self.pixmap = convert_cv_to_pixmap(self.cv_image)
            self.show_image()

    def on_keep_gray_threshold_triggered(self, image_data: np.ndarray):
        is_image_grayscale = self.ensure_grayscale()

        # Jeżeli użytkownik nie wyraził zgody wychodzę z funkcji
        if not is_image_grayscale:
            return False

        threshold, ok = QInputDialog.getInt(self, "Progowanie z zachowanie szarości",
                                            "Podaj próg progowania(0-255): ",
                                            value=127, min=0, max=255)
        if ok:
            self.cv_image = point_keep_gray_threshold(self.cv_image, threshold)
            self.pixmap = convert_cv_to_pixmap(self.cv_image)
            self.show_image()

    # ------------------------------
    # MENU LAB2 OPTIONS METHODS
    # ------------------------------

    def select_additional_images(self):

        # Sprawdzam, czy main_app na pewno istnieje
        if self.main_app_window is None:
            QMessageBox.critical(self, "Błąd", "Brak dostępu do głównego okna aplikacji")
            return None

        # Wyświetlam dialog do zaznaczenia okien
        dialog = ImageSelectionDialog(self.main_app_window, current_window=self, parent=self)

        # Zatrzymuje program do momentu kliknięcia Ok/Anuluj
        if dialog.exec():
            # Pobieram zaznaczone obrazy
            selected_images = dialog.get_selected_images_data()

            if not selected_images:
                QMessageBox.warning(self, "Info", "Nie zaznaczono żadnych obrazów do wykonania operacji")
                return None

            return selected_images

        # Jeżeli kliknięte Anuluj
        return None
