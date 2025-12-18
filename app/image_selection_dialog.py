# image_selection_dialog.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QDialogButtonBox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from image_window import ImageWindow
    from main import MainWindow


class ImageSelectionDialog(QDialog):
    def __init__(self, main_app: 'MainWindow', current_window, parent=None):
        super().__init__()

        self.setWindowTitle("Wybierz obrazy do operacji")
        self.resize(300, 400)

        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        all_windows: list[ImageWindow] = main_app.open_windows

        found_other_windows = False

        # Iteracja po wszysktich dostępnych oknach klasy ImageWindow i ustawianie każdego elementu z listy
        for window in all_windows:

            # Jeżeli znajdzie okno, na którym został wywołany dialog: pomija
            if window is current_window:
                continue

            found_other_windows = True

            # Tytuł do wyświetlenia na liście
            title = window.windowTitle() if window.windowTitle() else "Obraz bez nazwy"

            # Tworzę element listy
            item = QListWidgetItem(title)

            # Dodaję flagi: aktywny, można zaznaczyć, ma checkbox i można go zaznaczyć
            flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable
            item.setFlags(flags)

            # Domyślnie odznaczone
            item.setCheckState(Qt.CheckState.Unchecked)

            # Przypisanie obiektu ImageWindow do elementu listy
            item.setData(Qt.ItemDataRole.UserRole, window)

            self.list_widget.addItem(item)

        if not found_other_windows:
            self.list_widget.addItem("Brak innych otwartych okien")
            self.list_widget.setEnabled(False)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_selected_images_data(self):
        """
        :return: Zwraca listę tablic NumPy z zaznaczonych okien
        """

        selected_images: list[ImageWindow] = []

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)

            if item.checkState() == Qt.CheckState.Checked:
                window_object = item.data(Qt.ItemDataRole.UserRole)

                if window_object and hasattr(window_object, 'cv_image'):
                    selected_images.append(window_object.cv_image)

        return selected_images
