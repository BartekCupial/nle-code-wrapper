from functools import wraps
from typing import TYPE_CHECKING, Callable, Generator

from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.utils.utils import infinite_iterator

if TYPE_CHECKING:
    from nle_code_wrapper.bot.bot import Bot


class Panic:
    @classmethod
    def wrap(cls, func):
        return lambda *a, **k: Panic(wraps(func)(lambda: func(*a, **k)))

    def __init__(self, func: Callable[["Bot"], Generator]):
        self.func = func
        self.name = func.__name__
        self.iterator = None

    def __call__(self):
        try:
            if self.iterator is None:
                self.iterator = infinite_iterator(self.func)

            ret = next(self.iterator)
            return ret
        except BotPanic as e:
            self.iterator = infinite_iterator(self.func)
            raise e

    def reset(self):
        self.iterator = None
