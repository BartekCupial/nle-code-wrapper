import inspect
from functools import partial
from typing import Callable, Union


def check_strategy_parameters(strategy: Union[Callable, partial]) -> int:
    if isinstance(strategy, partial):
        # Get the original function's signature
        original_sig = inspect.signature(strategy.func)

        # Get already filled parameters from partial
        filled_params = set(strategy.keywords.keys())
        if strategy.args:
            # Map positional args to parameter names
            param_names = list(original_sig.parameters.keys())
            filled_params.update(param_names[: len(strategy.args)])

        # Create new signature with only unfilled parameters
        remaining_params = {name: param for name, param in original_sig.parameters.items() if name not in filled_params}

        return len(remaining_params)
    else:
        # Regular function - return all parameters
        return len(inspect.signature(strategy).parameters)
