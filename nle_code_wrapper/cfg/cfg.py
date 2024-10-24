import ast
from argparse import ArgumentParser

from nle_utils.utils.utils import str2bool


def add_code_wrapper_cli_args(p: ArgumentParser):
    p.add_argument("--code-wrapper", type=str2bool, default=True, help="Do we want to wrap the env with code wrapper")
    p.add_argument("--strategies", type=ast.literal_eval, default=[], help="List of strategy names")
    p.add_argument(
        "--strategies_loc",
        type=str,
        default="nle_code_wrapper.bot.strategy.strategies",
        help="where to search for strategies implementation",
    )
