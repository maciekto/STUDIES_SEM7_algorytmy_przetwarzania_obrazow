import numpy as np
from PyQt6.QtWidgets import QDialog

class LutDialog(QDialog):
    def __init__(self, lut_table: np.ndarray):
        self.lut_table = lut_table
