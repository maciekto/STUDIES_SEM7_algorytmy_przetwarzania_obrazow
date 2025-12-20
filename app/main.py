# main.py
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QSizePolicy
from image_window import ImageWindow
from utils import smart_image_read


class MainWindow(QMainWindow):
    """
    MainWindow dziedziczy klasę QMainWindow z PyQt
    """
    def __init__(self):
        super().__init__()

        # Ustawienia okna startowego
        self.setWindowTitle("APO")
        self.resize(300, 150)

        # Lista do przechowywania referencji do otwartych okien zdjęć
        self.open_windows = []

        # Prosty przycisk do otwierania
        layout = QVBoxLayout()                              # QVBoxLayout dziecko QBBoxLayout-układa od góry do dołu
        btn_open = QPushButton("Wczytaj nowy obraz")        # Zdefiniowanie instancji przycisku
        btn_open.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        btn_open.setStyleSheet("""
            QPushButton {
                background-color: #666666;  /* Jasnoszary kolor tła */
                border-radius: 15px;        /* Promień zaokrąglenia */
                border: 1px solid #aaaaaa;  /* Opcjonalne: cienka ramka */
                font-size: 16px;            /* Opcjonalne: większy tekst */
            }
            QPushButton:hover {
                background-color: #777777;  /* Efekt po najechaniu myszką */
            }
            QPushButton:pressed {
                background-color: #666666;  /* Efekt po kliknięciu */
            }
        
        """)
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.clicked.connect(self.open_image_dialog)    # Utworzenie sygnału dla tego przycisku, wywołuje metodę

        layout.addWidget(btn_open)  # Dodanie przycisku do layoutu

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_image_dialog(self):
        # Obsługa formatów bmp, tif, png, jpg

        # Zwraca ścieżkę do pliku i zastosowany filtr, który ignorujemy wg. konwencji _
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Wybierz obraz", "", "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )

        if file_path:

            # imread (image read) wczytuje obraz jako BGR
            cv_img = smart_image_read(file_path)

            if cv_img is not None:
                # Tworzymy nowe, niezależne okno dla tego zdjęcia
                image_window = ImageWindow(cv_img, title=file_path, main_app_window=self)
                image_window.show()

                # Zapamiętujemy okno, żeby nie zniknęło
                self.open_windows.append(image_window)

                # Podczas zamknięcia okna ze zdjęciem usuwa referencje do tego okna z listy self.open_windows
                image_window.destroyed.connect(
                    lambda: self.open_windows.remove(image_window) if image_window in self.open_windows else None)


if __name__ == "__main__":
    # Instancja aplikacji QApplication
    app = QApplication(sys.argv)

    # Tworzy główne okno aplikacji (klasa MainWindow zdefiniowana wyżej)
    window = MainWindow()

    # Wywołanie metody sprawia, że okno pojawia się dla użytkownika
    window.show()

    # app.exec() - główna pętla programu.
    # W wypadku zamknięcia programu app.exec() - sys.exit() zapewnia zakończenie programu czyste dla pamięci
    sys.exit(app.exec())
