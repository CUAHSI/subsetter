import numpy as np
from dataclasses import dataclass

# typing imports
from typing import Tuple


@dataclass
class SimpleBoundingBox:
    top: float  # max lat; top
    right: float  # max long; right
    bottom: float  # min lat: bottom
    left: float  # min long; left

    def as_array(self) -> np.array:
        return np.array(((self.left, self.right), (self.bottom, self.top)))


@dataclass
class SimpleBoundingBoxIndices:
    top: int  # max lat; top
    right: int  # max long; right
    bottom: int  # min lat; bottom
    left: int  # min long; left

    def as_array(self) -> np.array:
        return np.array(((self.left, self.right), (self.bottom, self.top)))


@dataclass
class BoundingBox:
    top_right: Tuple[float, float]
    bottom_right: Tuple[float, float]
    bottom_left: Tuple[float, float]
    top_left: Tuple[float, float]


@dataclass
class BoundingBoxIndices:
    top_right: Tuple[int, int]
    bottom_right: Tuple[int, int]
    bottom_left: Tuple[int, int]
    top_left: Tuple[int, int]
