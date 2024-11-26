import ast
from argparse import ArgumentParser

from nle_utils.utils.utils import str2bool


def add_code_wrapper_cli_args(p: ArgumentParser):
    p.add_argument("--code_wrapper", type=str2bool, default=True, help="Do we want to wrap the env with code wrapper")
    p.add_argument("--strategies", type=ast.literal_eval, default=[], help="List of strategy names")
    p.add_argument(
        "--strategies_loc",
        type=str,
        default="nle_code_wrapper.bot.strategies",
        help="where to search for strategies implementation",
    )


def add_skill_wrapper_cli_args(p: ArgumentParser):
    p.add_argument("--skill-wrapper", type=str2bool, default=True, help="Do we want to wrap the env with skill wrapper")
    p.add_argument("--skill_dim", type=int, default=2, help="Dimension of the skill space")
    p.add_argument("--num_negative_z", type=int, default=256, help="Number of negative samples for the skill space")
    p.add_argument("--csf_lam", type=float, default=1.0, help="CSF lambda")
    p.add_argument("--duplicate_skills", type=int, default=1, help="Number of duplicate skills")
    p.add_argument("--dual_lam", type=float, default=30.0, help="Dual lambda")
    p.add_argument(
        "--skill_method", type=str, default="CSF", help="Method to use for skill learning.", choices=["CSF", "METRA"]
    )
    p.add_argument("--dual_slack", type=float, default=1e-3)
    p.add_argument(
        "--skill_type", type=str, default="continuous", help="Type of skill space", choices=["continuous", "discrete"]
    )
    p.add_argument("--te_learning_rate", type=float, default=1e-4)
