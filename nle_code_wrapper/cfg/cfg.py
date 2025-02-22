import ast
import os
from argparse import ArgumentParser
from os.path import join

from nle_utils.utils.utils import str2bool


def add_code_wrapper_cli_args(p: ArgumentParser) -> None:
    p.add_argument("--code_wrapper", type=str2bool, default=True, help="Do we want to wrap the env with code wrapper")
    p.add_argument("--save_on_exception", type=str2bool, default=True, help="Do we want to save demo on exception")
    p.add_argument("--strategies", type=ast.literal_eval, default=[], help="List of strategy names")
    p.add_argument(
        "--strategies_loc",
        type=str,
        default="nle_code_wrapper.bot.strategies",
        help="where to search for strategies implementation",
    )
    p.add_argument("--max_strategy_steps", type=int, default=None, help="Strategy episode horizon.")
    p.add_argument("--add_letter_strategies", type=str2bool, default=True, help="Allow typing letters a-zA-Z.")
    p.add_argument(
        "--add_direction_strategies", type=str2bool, default=True, help="Allow basic low level skills eat, quaff etc."
    )
    p.add_argument("--add_more_strategy", type=str2bool, default=True, help="Allow typing `more` to skip stuff.")
    p.add_argument("--panics", type=ast.literal_eval, default=[], help="List of panic names")
    p.add_argument(
        "--panics_loc",
        type=str,
        default="nle_code_wrapper.bot.panics",
        help="where to search for panics implementation",
    )
    if "experiment" not in [action.dest for action in p._actions]:
        p.add_argument(
            "--experiment",
            type=str,
            default="default_experiment",
            help="Unique experiment name. This will also be the name for the experiment folder in the train dir."
            "If the experiment folder with this name aleady exists the experiment will be RESUMED!"
            "Any parameters passed from command line that do not match the parameters stored in the experiment config.json file will be overridden.",
        )
    if "train_dir" not in [action.dest for action in p._actions]:
        p.add_argument("--train_dir", default=join(os.getcwd(), "train_dir"), type=str, help="Root for all experiments")
