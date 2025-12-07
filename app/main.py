# main.py
import sys
import cv2
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget
from image_window import ImageWindow


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
            cv_img = cv2.imread(file_path)

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