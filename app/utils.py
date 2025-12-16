# utils.py
import cv2
import numpy as np
from PyQt6.QtGui import QImage, QPixmap

def smart_image_read(file_path):
    """
    Wczytuje obraz i automatycznie decyduje, czy zwrócić go jako obraz kolorowy (BGR) czy szaroodcieniowy (Grayscale)
    """
    img = cv2.imread(file_path)

    if img is None:
        return None

    if len(img.shape) == 3 and img.shape[2] == 3:
        b, g, r = cv2.split(img)

        if np.array_equal(b, g) and np.array_equal(g, r):
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    return img
def convert_cv_to_pixmap(cv_img):
    """
    Konwertuje obraz z formatu OpenCV (BGR/Grayscale) na QPixmap dla PyQt6 (RGB).
    """
    if cv_img is None:
        return None

    # Wyjmuje wysokość i szerokość z obrazu tablicy NumPy obrazu, indeks 0 i 1
    height, width = cv_img.shape[:2]

    # Obsługa obrazów kolorowych (3 kanały)
    if len(cv_img.shape) == 3:
        # Potrzebne do utworzenia obiektu QImage (do dobrego umiejscowienia obrazu w pamięci)
        # 3 x width, bo każdy piksel kolorowy zajmuje 3 bajty w pamięci
        bytes_per_line = 3 * width

        # Konwersja obrazu z NumPy BGR do RGB
        rgb_img_for_pyqt6 = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

        # Utworzenie obiektu PyQt image
        q_img = QImage(
            rgb_img_for_pyqt6.data,     # dane pixel-i, czyli bezpośrednio tablicę NumPy zawierającą ciąg kolorów
            width,
            height,
            bytes_per_line,             # Definiuje w pamięci rozpoczęcie każdego następnego wiersza
            QImage.Format.Format_RGB888 # informacja o tym, że obraz jest 24-bitowy, po 8 bitów na kolor
        )

    # Obsługa obrazów w odcieniach szarości (1 kanał)
    else:
        # Podobnie jak wyżej tylko tutaj mamy 1 kanał na piksel,
        # więc szerokość obrazu określa od razu potrzebną długość bitów
        bytes_per_line = width

        # Utworzenie obiektu QImage
        q_img = QImage(cv_img.data,
           width,
           height,
           bytes_per_line,                  # Definiuje w pamięci rozpoczęcie każdego następnego wiersza
           QImage.Format.Format_Grayscale8  # Informacja o tym, w jakim formacie ma być obraz
        )

    # Konwertuję na QPixmap, aby to wyświetlić w PyQt widget-cie i zwracam z funkcji
    return QPixmap.fromImage(q_img)


