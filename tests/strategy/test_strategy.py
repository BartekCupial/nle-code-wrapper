import pickle

import pytest

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategy import State, Strategy
from nle_code_wrapper.bot.strategy.strategies import explore, goto_stairs, open_doors, open_doors_kick, search


def test_strategy_state_persistence():
    """Test that strategy state persists even after BotPanic."""

    @Strategy.wrap
    def example_strategy(bot: "Bot", state=State(0)):
        while True:
            state.value += 1

            if state.value == 2:
                raise BotPanic("Test panic")

            yield True

    mock_bot = None

    strategy = example_strategy(mock_bot)

    # First call should succeed and change the state
    assert strategy()

    # Second call should raise BotPanic but keep the state
    try:
        strategy()
    except BotPanic:
        pass

    # Subsequent calls should continue from the last state
    assert strategy()
    assert strategy()
    assert strategy()


def test_strategy_composition():
    """Test composing strategies and handling inner strategy exceptions."""

    @Strategy.wrap
    def inner_strategy(bot: "Bot", state=State(0)):
        while True:
            state.value += 1

            if state.value == 2:
                raise BotPanic("Test panic")

            yield True

    @Strategy.wrap
    def outer_strategy(bot: "Bot"):
        inner = inner_strategy(bot)
        while True:
            # The strategy should catch the panic and yield
            try:
                data = inner()
                yield data
            except BotPanic:
                yield False

    mock_bot = None

    strategy = outer_strategy(mock_bot)

    assert strategy()
    assert not strategy()
    assert strategy()
    assert strategy()
    assert strategy()


def test_strategy_infinite_iteration():
    """Test that a strategy is iterated indefinietely."""

    @Strategy.wrap
    def example_strategy(bot: "Bot"):
        yield True
        yield False

    mock_bot = None
    strategy = example_strategy(mock_bot)

    assert strategy()
    assert not strategy()
    assert strategy()
    assert not strategy()


def test_strategy_reset():
    """Test that resetting a strategy works as expected."""

    @Strategy.wrap
    def example_strategy(bot: "Bot"):
        yield True
        yield False

    mock_bot = None
    strategy = example_strategy(mock_bot)

    # First call should succeed
    assert strategy()

    # Second call should fail
    assert not strategy()

    # Third call should succeed
    assert strategy()

    # Reset the strategy
    strategy.reset()

    # First call after reset should succeed again
    assert strategy()


def is_picklable(func):
    try:
        pickle.dumps(func)
        return True
    except (pickle.PicklingError, TypeError, AttributeError):
        return False


@pytest.mark.parametrize("strat", [explore, goto_stairs, open_doors, open_doors_kick, search])
def test_strategy_pickle(strat):
    assert is_picklable(strat)
