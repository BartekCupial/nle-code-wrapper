import argparse
import copy
import sys
from typing import List, Optional, Tuple

from nle_code_wrapper.cfg.cfg import add_basic_cli_args, add_default_env_args
from nle_code_wrapper.utils.utils import get_git_commit_hash


def parse_args(
    argv: Optional[List[str]] = None, evaluation: bool = False
) -> Tuple[argparse.ArgumentParser, argparse.Namespace]:
    """
    Create a parser and parse the known arguments (default SF configuration, see cfg.py).
    Returns a parser that can be further extended with additional arguments before a final pass is made.
    This allows custom scripts to add any additional arguments they need depending on partially known configuration,
    such as the environment name.

    argv: list of arguments to parse. If None, use sys.argv.
    evaluation: if True, also add evaluation-only arguments.
    returns: (parser, args)
    """
    if argv is None:
        argv = sys.argv[1:]

    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)
    add_basic_cli_args(p)
    add_default_env_args(p)

    args, _ = p.parse_known_args(argv)
    return p, args


def parse_full_cfg(parser: argparse.ArgumentParser, argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Given a parser, parse all arguments and return the final configuration."""
    if argv is None:
        argv = sys.argv[1:]

    args = parser.parse_args(argv)
    args = postprocess_args(args, argv, parser)
    return args


def postprocess_args(args, argv, parser) -> argparse.Namespace:
    """
    Postprocessing after parse_args is called.
    Makes it easy to use SF within another codebase which might have its own parse_args call.

    """

    if args.help:
        parser.print_help()
        sys.exit(0)

    args.command_line = " ".join(argv)

    # following is the trick to get only the args passed from the command line
    # We copy the parser and set the default value of None for every argument. Since one cannot pass None
    # from command line, we can differentiate between args passed from command line and args that got initialized
    # from their default values. This will allow us later to load missing values from the config file without
    # overriding anything passed from the command line
    no_defaults_parser = copy.deepcopy(parser)
    for arg_name in vars(args).keys():
        no_defaults_parser.set_defaults(**{arg_name: None})
    cli_args = no_defaults_parser.parse_args(argv)

    for arg_name in list(vars(cli_args).keys()):
        if cli_args.__dict__[arg_name] is None:
            del cli_args.__dict__[arg_name]

    args.cli_args = vars(cli_args)
    args.git_hash, args.git_repo_name = get_git_commit_hash()
    return args
