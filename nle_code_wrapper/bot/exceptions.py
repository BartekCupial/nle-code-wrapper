class BotFinished(BaseException):
    pass


class BotPanic(BaseException):
    """TODO(@bcupial): Add description."""

    pass


class EnemyAppeared(BotPanic):
    pass


class LostHP(BotPanic):
    pass


class BotChangeStrategy(BaseException):
    pass
