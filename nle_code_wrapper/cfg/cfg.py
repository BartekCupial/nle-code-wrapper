import ast
from argparse import ArgumentParser

from nle_utils.utils.utils import str2bool


def add_code_wrapper_cli_args(p: ArgumentParser) -> None:
    p.add_argument("--code_wrapper", type=str2bool, default=True, help="Do we want to wrap the env with code wrapper")
    p.add_argument("--strategies", type=ast.literal_eval, default=[], help="List of strategy names")
    p.add_argument(
        "--strategies_loc",
        type=str,
        default="nle_code_wrapper.bot.strategies",
        help="where to search for strategies implementation",
    )
    p.add_argument("--max_strategy_steps", type=int, default=100, help="Strategy episode horizon.")
