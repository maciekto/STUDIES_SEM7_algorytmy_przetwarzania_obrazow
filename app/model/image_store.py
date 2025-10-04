"""Small container for an opened image.

ImageDoc holds the NumPy array (pixel data) and an optional pathlib.Path
pointing to the file on disk. If path is None the document is considered
unsaved/untitled.
"""

from dataclasses import dataclass
from pathlib import Path
import numpy as np


@dataclass
class ImageDoc:
    """A light-weight container for image data and its source path.

    Fields:
    - array: NumPy ndarray with image pixels
    - path: pathlib.Path or None when the image was not loaded from disk
    """
    array: np.ndarray
    path: Path | None  # None = not saved / untitled

    @property
    def title(self) -> str:
        """Return a human-friendly title for UI (filename or 'untitled')."""
        return self.path.name if self.path else "untitled"
