"""Small entry point that starts the PyQt application.

Running `python -m app.main` will create a QApplication and show the
MainWindow. This module is intentionally tiny — most logic is in
app.ui.main_window.
"""

import sys
from PyQt6.QtWidgets import QApplication
from app.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
