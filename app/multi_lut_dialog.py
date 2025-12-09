import numpy as np
from PyQt6.QtWidgets import QDialog

from typing import Dict, Union, Any
MultipleLutDataType = Dict[
    str, Dict[
        str, np.ndarray | str
    ]
]

class MultiLutDialog(QDialog):
    def __init__(self, lut_data_dict: MultipleLutDataType, parent=None):
        super().__init__(parent)
        self.lut_data_dict = lut_data_dict


