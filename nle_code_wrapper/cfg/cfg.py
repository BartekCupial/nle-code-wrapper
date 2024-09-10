import ast
from argparse import ArgumentParser

from nle_code_wrapper.utils.utils import str2bool


def add_basic_cli_args(p: ArgumentParser):
    p.add_argument("-h", "--help", action="store_true", help="Print the help message", required=False)
    p.add_argument("--env", type=str, default=None, help="Name of the environment to use", required=True)
    p.add_argument("--seed", type=int, default=None, help="Seed to use")
    p.add_argument("--code-wrapper", type=str2bool, default=True, help="Do we want to wrap the env with code wrapper")
    p.add_argument("--strategies", type=ast.literal_eval, default=[], help="List of strategy names")


def add_default_env_args(p: ArgumentParser):
    p.add_argument(
        "--max-steps",
        type=int,
        default=10000,
        help="Number of maximum steps per episode.",
    )
    p.add_argument(
        "--ngames",
        type=int,
        default=1,
        help="Number of episodes to play.",
    )
    p.add_argument("--play-mode", type=str, default="human")
    p.add_argument("--no-render", action="store_true", help="Disables env.render().")
    p.add_argument(
        "--render_mode",
        type=str,
        default="human",
        choices=["human", "full", "ansi"],
        help="Render mode. Defaults to 'human'.",
    )
