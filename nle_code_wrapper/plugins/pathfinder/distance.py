import numpy as np


def chebyshev_distance(n1, n2):
    """computes the Chebyshev distance between two (x,y) tuples"""
    dx = np.abs(n1[0] - n2[0])
    dy = np.abs(n1[1] - n2[1])
    return np.max([dx, dy])
