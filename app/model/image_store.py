from dataclasses import dataclass
from pathlib import Path
import numpy as np

@dataclass
class ImageDoc:
    array: np.ndarray
    path: Path | None  # None = nie zapisany jeszcze

    @property
    def title(self) -> str:
        return self.path.name if self.path else "untitled"

