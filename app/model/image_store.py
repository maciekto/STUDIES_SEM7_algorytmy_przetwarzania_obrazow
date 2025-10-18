"""Kontener dla otwartego obrazu

Klasa ImageDoc trzyma tablicę NumPy i opcjonalną ścieżkę pliku na dysku.
Jeżeli ścieżka jest pusta zdjęcie ma status niezapisanego/bez nazwy.
"""

# from dataclasses import dataclass
from pathlib import Path
import numpy as np


# @dataclass
class ImageDoc:
    """Lekki kontener dla obrazu w formacie NumPy

    Pola:
    - array: NumPy ndarray z pixelami obrazu
    - path: pathlib.Path lub None kiedy obraz nie został wczytany z dysku
    """
    def __init__(self, array: np.ndarray, path: Path | None):
        self.array = array
        self.path = path

    @property
    def title(self) -> str:
        """Zwraca user friendly nazwę (nazwa pliku albo 'untitled')."""
        return self.path.name if self.path else "untitled"
