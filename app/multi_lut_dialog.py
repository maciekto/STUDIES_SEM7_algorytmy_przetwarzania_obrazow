import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QWidget, QVBoxLayout, QLabel, QTableWidget, QHeaderView, \
    QTableWidgetItem

from typing import Dict

"""
Example:

"RED" : {
    "data": Array,
    "index_label": "Jasność (Red)",
    "value_label": "Liczba pixel-i"
}

"""
MultipleLutDataType = Dict[
    str, Dict[
        str, np.ndarray | str
    ]
]

class MultiLutDialog(QDialog):
    def __init__(self, lut_data_dict: MultipleLutDataType, parent=None):
        super().__init__(parent)
        self.lut_data_dict = lut_data_dict

        self.setWindowTitle("Tablica lut dla 3 kanałów")
        self.setGeometry(100, 100, 900, 600)

        # Przypisanie layout-u do zmiennej
        self.main_layout = QHBoxLayout(self)

        # Iteracja po słowniku
        for title, package in lut_data_dict.items():
            # Pobieram dane kanału
            data_array = package.get("data")

            # Pobieram tytuły dla tablicy, jeżeli ich nie ma daje domyślne
            index_label = package.get("index_label", "Indeks")
            value_label = package.get("value_label", "Value")

            # Sprawdzam czy tablica nie jest pusta i czy zmienna przechowuje tablicę
            if data_array is not None and isinstance(data_array, np.ndarray):
                self.add_lut_column(title, data_array, str(index_label), str(value_label))


    def add_lut_column(self, title: str, data_array: np.ndarray, index_label: str, value_label: str):
        """Tworzy kolumnę z tabelą"""

        # Okno QWidget z layoutem pionowym
        column_widget = QWidget()
        column_layout = QVBoxLayout(column_widget)
        column_layout.setContentsMargins(5, 0, 5, 0)

        # Tytuł tabeli
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt; margin-bottom: 5px;")
        column_layout.addWidget(title_label)

        # Definicja tabeli
        table = QTableWidget()
        data_count = len(data_array)
        table.setRowCount(data_count)
        table.setColumnCount(2)

        # Ustawienie tytułów dla argumentów
        table.setHorizontalHeaderLabels([index_label, value_label])

        # Wysokość wiersza
        table.verticalHeader().setDefaultSectionSize(20)
        # Blokuje zmianę wysokości wiersza
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        # Ustawienie flag by nie można było zmieniać tablicy lut
        flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

        # Iteracja po danych i wypełnienie tabeli
        for i in range(data_count):
            item_index = QTableWidgetItem(str(i))
            item_index.setFlags(flags)
            table.setItem(i, 0, item_index)

            val = int(data_array[i])
            item_val = QTableWidgetItem(str(val))
            item_val.setFlags(flags)
            table.setItem(i, 1, item_val)

        # Wypełnia całą dostępną przestrzeń równomiernie
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Dodaje widget tabeli do QWidgetu, który jest kolumną
        column_layout.addWidget(table)
        # Dodaje QWidget (całą kolumnę z tytułem i tabelą) do HBox
        self.main_layout.addWidget(column_widget)