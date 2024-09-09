import argparse
import functools
import importlib
import logging
import os
from itertools import chain
from subprocess import SubprocessError, check_output, run
from typing import Any, Callable, Generator, Iterator

import numba as nb
import numpy as np
from colorlog import ColoredFormatter

# Logging

log = logging.getLogger("rl")
log.setLevel(logging.DEBUG)
log.handlers = []  # No duplicated handlers
log.propagate = False  # workaround for duplicated logs in ipython
log_level = logging.DEBUG

stream_handler = logging.StreamHandler()
stream_handler.setLevel(log_level)

stream_formatter = ColoredFormatter(
    "%(log_color)s[%(asctime)s][%(process)05d] %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "white,bold",
        "INFOV": "cyan,bold",
        "WARNING": "yellow",
        "ERROR": "red,bold",
        "CRITICAL": "red,bg_white",
    },
    secondary_log_colors={},
    style="%",
)
stream_handler.setFormatter(stream_formatter)
log.addHandler(stream_handler)


# CLI args


def str2bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str) and v.lower() in ("true",):
        return True
    elif isinstance(v, str) and v.lower() in ("false",):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected")


def git_root():
    """:returns None if we're not in the git repo, otherwise full path to the root of the repo."""
    cwd = os.getcwd()

    # check if we're inside a git repository
    curr_dir = cwd
    max_depth = 20
    for _ in range(max_depth):
        if ".git" in os.listdir(curr_dir):
            return curr_dir

        parent_dir = os.path.dirname(curr_dir)
        if curr_dir == parent_dir:  # climbed all the way to the root
            break
        curr_dir = parent_dir

    return None


def get_git_commit_hash():
    git_hash = "unknown"
    git_repo_name = "not a git repository"

    git_root_dir = git_root()
    if git_root_dir:
        try:
            git_hash = check_output(["git", "rev-parse", "HEAD"], cwd=git_root_dir, timeout=1).strip().decode("ascii")
            git_repo_name = (
                check_output(["git", "config", "--get", "remote.origin.url"], cwd=git_root_dir, timeout=1)
                .strip()
                .decode("ascii")
            )
        except SubprocessError:
            log.debug("Could not query the git revision for the logs, perhaps git is not available")

    return git_hash, git_repo_name


# general Python utilities


def is_module_available(module_name):
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


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
def _isin_mask(elems):
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


def isin(array, *elems):
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
                    else tuple(e)
                    if isinstance(e, list)
                    else frozenset(e)
                    if isinstance(e, set)
                    else e
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
