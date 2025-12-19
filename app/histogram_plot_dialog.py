# histogram_plot_dialog.py
# Importy dla PyQt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt

# Importy dla Matplotlib
import numpy as np
from typing import Dict, Union

from mpl_canvas import MplCanvas
from multi_lut_dialog import MultiLutDialog
from single_lut_dialog import SingleLutDialog


class HistogramPlotDialog(QDialog):
    """
    Dziedziczy klasę QDialog od PyQt
    """

    def __init__(self, lut_data: Union[np.ndarray, Dict[str, np.ndarray]], parent=None):
        # Utworzenie okna, jego tytułu oraz wielkości
        super().__init__(parent)
        self.setWindowTitle("Graficzna Prezentacja Histogramu")
        self.setGeometry(100, 100, 800, 700)

        # Przechowanie danych lutu
        self.raw_lut_data = lut_data

        # Tablica dla okien z lutami
        self._child_luts = []

        # Zainicjowanie przełącznika kanałów
        self.current_channel_data = None

        # Utworzenie Layoutu wertykalnego ustawionego jako główny
        main_layout = QVBoxLayout(self)

        # Górny pasek z przełącznikiem kanałów
        control_layout = QHBoxLayout()

        # Definicja przełącznika kanałów
        control_layout.addWidget(QLabel("Wybierz kanał:"))
        self.channel_selector = QComboBox()
        self.channel_selector.currentIndexChanged.connect(self.update_plot)  # Łączy przełączenie kanału z metodą
        control_layout.addWidget(self.channel_selector)

        # Automatyczna odstęp pomiędzy tytułem i przełącznikiem kanału
        control_layout.addStretch(1)

        # Przycisk z tablicami lut
        lut_button = QPushButton("Tablica Lut")
        lut_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        lut_button.setCursor(Qt.CursorShape.PointingHandCursor)
        lut_button.setStyleSheet("""
        QPushButton {
            border-radius: 8px;
            padding: 4px 10px;
            background-color: #525252;
            border: 1px solid #a0a0a0;
        }
        QPushButton:hover {
            background-color: #636363;
        }
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
        """)
        lut_button.clicked.connect(lambda: self.show_lut_tables(lut_data))
        control_layout.addWidget(lut_button)

        # Tytuł paska z przełącznikiem kanałów
        control_layout.addWidget(QLabel("Przełącznik kanałów, tablica lut"))

        # Dodanie górnego paska do QVBoxLayout
        main_layout.addLayout(control_layout)

        # Tworzy instancję
        self.statsChart = MplCanvas(self, width=8, height=6, dpi=100)
        main_layout.addWidget(self.statsChart)

        # Label dla wykrsu
        self.stats_label = QLabel("Statystyki: ")
        # Ustawienie stylów wykresu
        self.stats_label.setStyleSheet("padding: 5px;")
        # Dodanie wykresu jako następnego elementu w QVBoxLayout
        main_layout.addWidget(self.stats_label)

        # Uzupełnienie listy z wyborem kanału
        self._setup_channel_selector()

        # Narysowanie pierwszego wykresu
        self.update_plot()

    def show_lut_tables(self, lut_data: np.ndarray | Dict[str, np.ndarray]):

        lut_dialog = None

        if isinstance(lut_data, np.ndarray):
            lut_dialog = SingleLutDialog(lut_data, lut_index_label="Jasność", lut_value_label="Ilość pixeli")
            lut_dialog.show()
        elif isinstance(lut_data, Dict):
            structured_histogram_data = {
                "red": {
                    "data": lut_data["red"],
                    "index_label": "Jasność (RED)",
                    "index_value": "Ilość pixel-i"
                },
                "green": {
                    "data": lut_data["green"],
                    "index_label": "Jasność (GREEN)",
                    "index_value": "Ilość pixel-i"
                },
                "blue": {
                    "data": lut_data["blue"],
                    "index_label": "Jasność (BLUE)",
                    "index_value": "Ilość pixel-i"
                }
            }
            lut_dialog = MultiLutDialog(structured_histogram_data)

        if lut_dialog is not None:
            lut_dialog.show()
            self._child_luts.append(lut_dialog)

            # Usunięcie referencji, gdy użytkownik zamknie okno
            lut_dialog.destroyed.connect(
                lambda: self._child_luts.remove(lut_dialog) if lut_dialog in self._child_luts else None
            )

    def _setup_channel_selector(self):
        """
        Metoda wypełniająca widget QComboBox dostępnymi opcjami dla wyświetlenia histogramu
        """

        # Czyści dane, jeżeli są w widgecie
        self.channel_selector.clear()

        # Jeżeli przekazane dane lut to tablica to jest to obraz szaroodcieniowy
        if isinstance(self.raw_lut_data, np.ndarray):
            # Ustawienie opcji w QBoxCombo
            self.channel_selector.addItem("Gray/Luminancja", self.raw_lut_data)

        # Jeżeli przekazane dane lut są jako słownik
        elif isinstance(self.raw_lut_data, dict):
            # Dodanie opcji ze wszystkimi pokazanymi kanałami jednocześnie
            all_data = {k: v for k, v in self.raw_lut_data.items()}
            self.channel_selector.addItem("Wszystkie Kanały", all_data)

            # Dodanie opcji per kanał
            for color, data_array in self.raw_lut_data.items():
                self.channel_selector.addItem(color, data_array)

    # Metoda dla wyliczenia danych dla tego obrazu, statyczna, bo w środku nie używa self
    @staticmethod
    def calculate_stats(lut_data: np.ndarray) -> str:

        pixel_values = np.repeat(np.arange(lut_data.size), lut_data)

        if pixel_values.size == 0:
            return "Brak pikseli."

        # Podstawowe statystyki
        mean_brightness = np.mean(pixel_values)
        standard_deviaton = np.std(pixel_values)
        median = np.median(pixel_values)
        min_value = np.min(pixel_values)
        max_value = np.max(pixel_values)
        total_pixels = pixel_values.size

        # Tekst do wyświetlenia
        stats_text = (
            f"Statystyki (Liczba pikseli: {total_pixels:,}):\n"
            f"  Średnia jasność: {mean_brightness:.2f}\n"
            f"  Odchylenie Standardowe - jasności: {standard_deviaton:.2f}\n"
            f"  Mediana:       {median:.2f}\n"
            f"  Min:           {min_value}\n"
            f"  Max:           {max_value}"
        )
        return stats_text

    def update_plot(self):

        # Pobiranie przekazanych danych z opcji
        selected_data = self.channel_selector.currentData()

        # Pobranie wyświetlanego tekstu-jest on nazwą kanału
        channel_name = self.channel_selector.currentText()

        # Wyczyszczenie canvasu matplotlib
        self.statsChart.axes.clear()

        # Sprawdzenie, czy zaznaczone dane są tablicą-rysowanie pojedyńczego kanału
        if isinstance(selected_data, np.ndarray):
            # Ustawienie aktualnych danych do wyświetlenia jako te z przekazane z opcji
            self.current_channel_data = selected_data

            # Przypisanie nazwy kanału jako zmiennej kolor dla lepszego kodu
            color = channel_name
            if 'Gray' in channel_name or 'Luminancja' in channel_name:
                color = 'gray'

            # Narysowanie histogramu za pomocą klasy MplCanvas
            self.statsChart.draw_manual_histogram(selected_data, color)
            self.stats_label.setText(self.calculate_stats(selected_data))

        # Sprawdzenie, czy zaznaczone dane są słownikiem-rysowanie wszystkich kanałów naraz
        # Przekazany do QComboBox słownik
        elif isinstance(selected_data, dict):
            all_lut_arrays = list(selected_data.values())
            first_lut_array = all_lut_arrays[0]

            all_pixels = np.zeros(first_lut_array.size, dtype=np.int64)
            # Iteracja po przekazanym słowniku
            for name, data_array in selected_data.items():
                color = name

                # Nadpisuje tu histogram
                self.statsChart.draw_manual_histogram(data_array, color)

                # Sumowanie wektorowe, czyli operacja += jest wywoływana dla każdego [i] z dwóch tablic
                all_pixels += data_array

            self.statsChart.axes.set_title("Histogram - Wszystkie Kanały (Nakładanie)")
            self.statsChart.draw()

            # Dodanie legendy
            self.statsChart.axes.legend(['Red', 'Green', 'Blue'], loc='upper right')
            # Dodanie tytułu
            self.statsChart.axes.set_title("Histogram - Wszystkie Kanały (Nakładanie)")
            self.statsChart.draw()

            # Wyświetlenie statystyk
            stats_output = self.calculate_stats(all_pixels)
            self.stats_label.setText(stats_output)
