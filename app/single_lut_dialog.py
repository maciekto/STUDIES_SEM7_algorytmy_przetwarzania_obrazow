import numpy as np
from PyQt6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QLabel, QHeaderView
from PyQt6.QtCore import Qt


class SingleLutDialog(QDialog):
    def __init__(self, lut_data: np.ndarray, lut_index_label: str, lut_value_label: str, parent=None):
        super().__init__(parent)
        self.lut_data = lut_data
        self.lut_value_label = lut_value_label
        self.lut_index_label = lut_index_label

        # Ustawienia okna
        self.setWindowTitle(f"Dane: {self.lut_index_label} do {self.lut_value_label}")
        self.setGeometry(100, 100, 400, 600)

        # Przypisanie layoutu do zmiennej main_layout
        self.main_layout = QVBoxLayout(self)

        self.title_label = QLabel(f"Tabela: {self.lut_index_label} do {self.lut_value_label}")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14pt;")

        self.table_widget = QTableWidget()

        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.table_widget)

        self.fill_table()

    def fill_table(self):
        # Odczytanie ilości indeksów
        lut_index_count = len(self.lut_data)

        # Zdefiniowanie wielkości tabeli
        self.table_widget.setRowCount(lut_index_count)
        self.table_widget.setColumnCount(2)

        # Ustawienie nagłówków kolumn
        self.table_widget.setHorizontalHeaderLabels([self.lut_index_label, self.lut_value_label])

        self.table_widget.verticalHeader().setDefaultSectionSize(15)

        # Wypełnienie komórek
        for i in range(lut_index_count):
            # Kolumna z indexem tabeli lut
            item_index = QTableWidgetItem(str(i))
            item_index.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table_widget.setItem(i, 0, item_index)


            value = int(self.lut_data[i])
            item_value = QTableWidgetItem(str(value))
            self.table_widget.setItem(i, 1, item_value)

        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)