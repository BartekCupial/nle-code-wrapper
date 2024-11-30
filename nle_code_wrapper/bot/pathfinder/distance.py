from typing import Tuple

import numpy as np
from numpy import int64


def chebyshev_distance(n1: Tuple[int64, int64], n2: Tuple[int64, int64]) -> int64:
    """computes the Chebyshev distance between two (x,y) tuples"""
    dx = np.abs(n1[0] - n2[0])
    dy = np.abs(n1[1] - n2[1])
    return np.max([dx, dy])
