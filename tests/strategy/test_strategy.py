import pickle

import pytest

from nle_code_wrapper.bot.strategy.strategies import explore, goto_stairs, open_doors, open_doors_kick, search


def is_picklable(func):
    try:
        pickle.dumps(func)
        return True
    except (pickle.PicklingError, TypeError, AttributeError):
        return False


@pytest.mark.parametrize("strat", [explore, goto_stairs, open_doors, open_doors_kick, search])
def test_strategy_pickle(strat):
    assert is_picklable(strat)
