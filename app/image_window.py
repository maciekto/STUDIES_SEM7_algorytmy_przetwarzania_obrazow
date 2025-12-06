# image_window.py
from PyQt6.QtWidgets import QMainWindow, QLabel, QScrollArea, QMenu
from PyQt6.QtCore import Qt
import cv2
from utils import convert_cv_to_pixmap


# Tu będziesz importować swoje algorytmy z algorithms.py

class ImageWindow(QMainWindow):
    def __init__(self, cv_image, title="Obraz"):
        super().__init__()
        self.setWindowTitle(title)

        # Przechowujemy oryginał w formacie OpenCV (tablica NumPy)
        self.cv_image = cv_image

        # Ustawienie GUI do wyświetlania
        self.scroll_area = QScrollArea()                            # Ustawienie scroll-u, gdy zmniejszę okno
        self.label_image = QLabel()                                 # Bez tego nie będzie gdzie wyświetlić Pixmap-y
        self.label_image.setAlignment(Qt.AlignmentFlag.AlignCenter) # Ustawia wyrównanie obrazu w QLabel na środek
        self.scroll_area.setWidget(self.label_image)                # Osadza QLabel w obszarze przewijania scroll_area
        self.scroll_area.setWidgetResizable(True)                   # Włącza zmianę wielkości okna
        self.setCentralWidget(self.scroll_area)                     # Ustawia QScrollArea jako jedyny, wypełniający
                                                                    # element QMainWindow

        # Wyświetlenie obrazu
        self.show_image()

        # Menu okna ze zdjęciem
        self.create_menus()

    def show_image(self):
        """Odświeża widok w oknie na podstawie self.cv_image"""
        pixmap = convert_cv_to_pixmap(self.cv_image)
        if pixmap:
            # Ustawienie pixmap-y jako zawartości obiektu QLabel
            self.label_image.setPixmap(pixmap)

            # Dopasowanie rozmiaru okna do zdjęcia z marginesami 20 px, maksymalna wielkość okna to 800x600px
            self.resize(min(pixmap.width() + 20, 800), min(pixmap.height() + 20, 600))

    def create_menus(self):
        menu_bar = self.menuBar()

        # Menu dla lab-ów 1
        lab1_menu = menu_bar.addMenu("Lab 1")

        # Przykład: Wywołanie histogramu (Zadanie 3 z Lab 1)
        action_hist = lab1_menu.addAction("Pokaż Histogram")
        action_hist.triggered.connect(self.show_histogram_placeholder)

        # Menu dla lab-ów 2
        lab2_menu = menu_bar.addMenu("Lab 2")
        # Tu dodasz operacje arytmetyczne, logiczne itd.

    def show_histogram_placeholder(self):
        print("Tu wywołasz okno z wykresem histogramu (zrób to ręcznie, nie używaj gotowca!)")
        # Tutaj w przyszłości:
        # 1. Oblicz tablicę LUT (algorithms.calculate_histogram)
        # 2. Otwórz nowe okno dialogowe rysujące słupki na QGraphicsView lub Matplotlib