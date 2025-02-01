import pickle
from functools import partial
from os.path import join

from nle_utils.cfg.arguments import parse_args, parse_full_cfg
from nle_utils.envs.nethack.nethack_params import add_extra_params_nethack_env
from nle_utils.play import play
from sample_factory.cfg.arguments import load_from_checkpoint
from sample_factory.utils.utils import experiment_dir

from nle_code_wrapper.cfg.cfg import add_code_wrapper_cli_args
from nle_code_wrapper.envs.nethack.play_nethack import register_nethack_components
from nle_code_wrapper.utils.play import play_from_actions


def parse_nethack_args(argv=None):
    parser, partial_cfg = parse_args(argv=argv)
    add_extra_params_nethack_env(parser)
    add_code_wrapper_cli_args(parser)
    parser.add_argument("--demo_name", type=str, required=True)
    final_cfg = parse_full_cfg(parser, argv)
    return final_cfg


def main():
    register_nethack_components()
    cfg = parse_nethack_args()
    cfg = load_from_checkpoint(cfg)

    failed_game_path = join(experiment_dir(cfg=cfg), "failed_games")
    with open(join(failed_game_path, cfg.demo_name), "rb") as f:
        dat = pickle.load(f)

    recorded_actions = dat["actions"]
    seed = dat["seed"]
    cfg.seed = seed
    play(cfg, get_action=partial(play_from_actions, actions=recorded_actions))


if __name__ == "__main__":
    main()
