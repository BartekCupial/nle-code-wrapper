import functools
import importlib
from itertools import chain
from typing import Any, Callable, Generator, Iterator, List, Tuple, Union

import numba as nb
import numpy as np
from numpy import int64, ndarray

# general Python utilities


@nb.njit("b1[:,:](i2[:,:],i2,i2,b1[:])", cache=True)
def _isin_kernel(array, mi, ma, mask):
    ret = np.zeros(array.shape, dtype=nb.b1)
    for y in range(array.shape[0]):
        for x in range(array.shape[1]):
            if array[y, x] < mi or array[y, x] > ma:
                continue
            ret[y, x] = mask[array[y, x] - mi]
    return ret


@functools.lru_cache(1024)
def _isin_mask(elems: Any) -> Tuple[int, int, ndarray]:
    elems = np.array(list(chain(*elems)), np.int16)
    return _isin_mask_kernel(elems)


@nb.njit("Tuple((i2,i2,b1[:]))(i2[:])", cache=True)
def _isin_mask_kernel(elems):
    mi = 32767  # i2
    ma = -32768  # i2
    for i in range(elems.shape[0]):
        if mi > elems[i]:
            mi = elems[i]
        if ma < elems[i]:
            ma = elems[i]
    ret = np.zeros(ma - mi + 1, dtype=nb.b1)
    for i in range(elems.shape[0]):
        ret[elems[i] - mi] = True
    return mi, ma, ret


def isin(array: ndarray, *elems) -> ndarray:
    assert array.dtype == np.int16

    # for memoization
    elems = tuple(
        (
            (
                e
                if isinstance(e, tuple)
                else (
                    e
                    if isinstance(e, frozenset)
                    else tuple(e) if isinstance(e, list) else frozenset(e) if isinstance(e, set) else e
                )
            )
            for e in elems
        )
    )

    mi, ma, mask = _isin_mask(elems)
    return _isin_kernel(array, mi, ma, mask)


def any_in(array, *elems):
    # TODO: optimize
    return isin(array, *elems).any()


def infinite_iterator(func: Callable[[Any], Generator]) -> Iterator:
    iterator = iter(func())
    while True:
        try:
            data = next(iterator)
        except StopIteration:
            iterator = iter(func())
            data = next(iterator)
        yield data


def coords(glyphs: ndarray, obj: frozenset) -> List[Union[Any, Tuple[int64, int64]]]:
    return list(zip(*isin(glyphs, obj).nonzero()))


def get_function_by_name(module_name, function_name):
    try:
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        if callable(function):
            return function
        else:
            raise AttributeError(f"{function_name} is not a callable function in {module_name}")
    except ImportError:
        raise ImportError(f"Module {module_name} not found")
    except AttributeError:
        raise AttributeError(f"Function {function_name} not found in module {module_name}")
