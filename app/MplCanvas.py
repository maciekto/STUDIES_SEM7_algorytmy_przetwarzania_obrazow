# Importy dla PyQt
from PyQt6.QtWidgets import QSizePolicy

# Importy dla Matplotlib
import matplotlib.figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import numpy as np


class MplCanvas(FigureCanvasQTAgg):
    """
    Widżet do osadzania wykresu Matplotlib.
    Dziedziczy po FigureCanvasQTAgg w celu zamienienia obiektu Matplotlib na QWidget co umożliwia dodanie go do
    QLayout-u
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        fig = matplotlib.figure.Figure(figsize=(width, height), dpi=dpi) # Utworzenie canvas-u matplotlib

        # Tworzy obszar rysowania: 1 wiersz, 1 kolumna, pierwsza pozycja?
        self.axes = fig.add_subplot(111)
        # Inicjalizacja klasy bazowej
        super().__init__(fig)
        self.setParent(parent)  # Ustawienie rodzica, jeżeli został przekazany
        # Ustawienie policy na wypełnienie całej dostępnej przestrzeni przez wykres
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()

    def draw_manual_histogram(self, lut_data: np.ndarray, color: str = 'gray'):
        """
        Rysuje histogram ręcznie, używając plt.vlines
        """

        # W przypadku braku danych wyświetlam komunikat
        if lut_data.size == 0:
            self.axes.set_title("Brak danych histogramu")
            self.draw()
            return

        # Wyczytanie maksymalnej ilości pixel-i dla danej jasności do określenia maksymalnej wartości osi Y
        max_count = np.max(lut_data)

        # Tworzy tablicę z wartościami od zera do 255, dla osi X
        x_values = np.arange(lut_data.size)

        # Tworzy ręcznie słupki
        self.axes.vlines(
            x_values,       # Wartości dla osi X
            ymin=0,         # Minimalna wartość słupków
            ymax=lut_data,  # Dane dla słupków
            colors=color,   # Color
            lw=1,           # Szerokość słupka
            alpha=0.7       # Przeźroczystość
        )

        # Tytuł histogramu
        self.axes.set_title(f"Histogram - Kanał: {color.capitalize()}")
        # Tytuł dla osi X
        self.axes.set_xlabel("Poziom Jasności (0-255)")
        # Tytuł dla osi Y
        self.axes.set_ylabel("Liczba Pixeli")

        # Ustawia zakresu widoczności osi X.
        # -1 - dla marginesu po lewej stronie
        # 256 - 255 wartości plus 1 marginesu
        self.axes.set_xlim(-1, lut_data.size)

        # Ustawia zakres widoczności osi Y.
        # Od zera do maksymalnej liczby * 105%
        self.axes.set_ylim(0, max_count * 1.05)

        # Wywołuje na FigureCanvasQAgg metodę, która dalej przekształca stan rysunku matplotlib na pixel-e i odświeżył
        # widget na ekranie
        self.draw()