from typing import Optional, Tuple, Union

import numpy as np


def chebyshev_distance(
    a: np.ndarray,
    b: np.ndarray,
    axis: Optional[int] = None,
    keepdims=False,
) -> Union[np.ndarray, float]:
    """
    Compute the chebyshev distance ``max(|b - a|)``.

    Parameters
    ----------
    a
        Input vector(s) of shape ``(Ni..., n, Nk...)``.
    b
        Input vector(s) of shape ``(Ni..., n, Nk...)``.
    axis
        The axis to compute along. The default is the last axis.
    keepdims
        If this is set to True, the axis which the distance is computed along is
        left in the result as a dimension with size one. With this option the
        result will broadcast correctly against the original ``a`` and ``b``.

    Returns
    -------
    d
        The distance(s) between vectors.
        With ``keepdims`` set to True it's of shape ``(Ni..., 1, Nk...)``,
        otherwise it's of shape ``(Ni..., Nk...)``,

    """
    v = np.abs(np.subtract(b, a))

    if v.ndim == 0:
        return np.abs(v)

    if axis is None:
        axis = -1

    return np.max(v, axis=axis, keepdims=keepdims)


def cross_distance(
    a: np.ndarray,
    b: np.ndarray,
    axis: Optional[Union[int, Tuple[int, int]]] = None,
) -> np.ndarray:
    """
    Compute distance between each pair of the two collections of vectors.

    In simple terms, ``cross_distance(a, b)[i, j] = distance(a[i], b[j])``.

    Parameters
    ----------
    a
        Input vector(s) of shape ``(Ni..., n, Nk...)``.
    b
        Input vector(s) of shape ``(Nj..., n, Nl...)``.
    axis
        The axis to compute along. Either a tuple ``(axis_a, axis_b)`` or
        a single integer (equivalent to ``(axis, axis)``).
        The default is the last axis in both arrays.

    Returns
    -------
    c
        The cross distance matrix of shape ``(Ni..., Nk..., Nj..., Nl...)``.

    """
    if axis is None:
        axis = (-1, -1)
    if isinstance(axis, int):
        axis = (axis, axis)

    axis_a, axis_b = axis

    a = np.moveaxis(np.atleast_2d(a), axis_a, -1)
    b = np.moveaxis(np.atleast_2d(b), axis_b, -1)

    a_ndim = a.ndim - 1
    b_ndim = b.ndim - 1

    a = np.expand_dims(a, axis=tuple(range(a_ndim, a_ndim + b_ndim)))
    b = np.expand_dims(b, axis=tuple(range(0, a_ndim)))

    return chebyshev_distance(a, b)
