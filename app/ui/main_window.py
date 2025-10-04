from PyQt6.QtWidgets import QMainWindow, QLabel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Algorytmy Przetwarzania Obrazu - LAB1")
        self.setGeometry(200, 200, 800, 600)

        # na razie tylko prosty label
        label = QLabel("Hello, PyQt6!", self)
        self.setCentralWidget(label)
