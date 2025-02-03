import pickle
from os.path import join

from nle_utils.cfg.arguments import parse_args, parse_full_cfg
from nle_utils.envs.minihack.minihack_params import add_extra_params_minihack_env
from nle_utils.utils.attr_dict import AttrDict
from sample_factory.cfg.arguments import load_from_checkpoint
from sample_factory.envs.create_env import create_env
from sample_factory.utils.utils import experiment_dir

from nle_code_wrapper.agents.sample_factory.minihack.train import register_minihack_components
from nle_code_wrapper.cfg.cfg import add_code_wrapper_cli_args


def parse_minihack_args(argv=None):
    parser, partial_cfg = parse_args(argv=argv)
    add_extra_params_minihack_env(parser)
    add_code_wrapper_cli_args(parser)
    parser.add_argument("--demo_name", type=str, required=True)
    final_cfg = parse_full_cfg(parser, argv)
    return final_cfg


def main():
    register_minihack_components()
    cfg = parse_minihack_args()
    cfg = load_from_checkpoint(cfg)

    failed_game_path = join(experiment_dir(cfg=cfg), "failed_games")
    with open(join(failed_game_path, cfg.demo_name), "rb") as f:
        dat = pickle.load(f)

    seed = dat["seed"]
    recorded_actions = dat["actions"]
    # last_observation = dat["last_observation"]
    cfg.seed = seed

    env = create_env(
        cfg.env,
        cfg=cfg,
        env_config=AttrDict(worker_index=0, vector_index=0, env_id=0),
        render_mode="human",
    )
    obs, info = env.reset(seed=cfg.seed)
    bot = env.get_wrapper_attr("bot")

    for action in recorded_actions:
        strategy = bot.strategies[action]
        print(strategy.__name__)
        obs, reward, teraminated, truncated, info = env.step(action)


if __name__ == "__main__":
    main()
