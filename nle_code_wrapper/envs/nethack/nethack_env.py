from pathlib import Path
from typing import Optional

from nle.env.tasks import (
    NetHackChallenge,
    NetHackEat,
    NetHackGold,
    NetHackOracle,
    NetHackScore,
    NetHackScout,
    NetHackStaircase,
    NetHackStaircasePet,
)
from nle_utils.wrappers import GymV21CompatibilityV0, LoadSave, NLETimeLimit

NETHACK_ENVS = dict(
    staircase=NetHackStaircase,
    score=NetHackScore,
    pet=NetHackStaircasePet,
    oracle=NetHackOracle,
    gold=NetHackGold,
    eat=NetHackEat,
    scout=NetHackScout,
    challenge=NetHackChallenge,
)


def nethack_env_by_name(name):
    if name in NETHACK_ENVS.keys():
        return NETHACK_ENVS[name]
    else:
        raise Exception("Unknown NetHack env")


def make_nethack_env(env_name, cfg, env_config, render_mode: Optional[str] = None):
    env_class = nethack_env_by_name(env_name)

    observation_keys = cfg.observation_keys

    if cfg.gameloaddir:
        # gameloaddir can be either list or a single path
        if isinstance(cfg.gameloaddir, list):
            # if gameloaddir is a list we will pick only one element from this list
            if env_config:
                # based on env_id
                idx = env_config["env_id"] % len(cfg.gameloaddir)
                gameloaddir = cfg.gameloaddir[idx]
            else:
                # if no env_id use first element
                gameloaddir = cfg.gameloaddir[0]
        else:
            # if gameliaddir is a single path
            assert isinstance(cfg.gameloaddir, (str, Path))
            gameloaddir = cfg.gameloaddir
    else:
        gameloaddir = None

    kwargs = dict(
        character=cfg.character,
        max_episode_steps=cfg.max_episode_steps,
        observation_keys=observation_keys,
        penalty_step=cfg.penalty_step,
        penalty_time=cfg.penalty_time,
        penalty_mode=cfg.fn_penalty_step,
        savedir=cfg.savedir,
        save_ttyrec_every=cfg.save_ttyrec_every,
    )
    if env_name == "challenge":
        kwargs["no_progress_timeout"] = 150

    if env_name in ("staircase", "pet", "oracle"):
        kwargs.update(reward_win=cfg.reward_win, reward_lose=cfg.reward_lose)
    # else:  # print warning once
    # warnings.warn("Ignoring cfg.reward_win and cfg.reward_lose")
    if cfg.state_counter is not None:
        kwargs.update(state_counter=cfg.state_counter)

    if env_name == "scout_challenge":
        kwargs.update(scout_multiplier=cfg.scout_multiplier, score_clip=cfg.score_clip)

    env = env_class(**kwargs)

    # add TimeLimit.truncated to info
    env = NLETimeLimit(env)

    if gameloaddir is not None:
        env = LoadSave(env, gameloaddir)

    env = GymV21CompatibilityV0(env=env)

    if render_mode:
        env.render_mode = render_mode

    return env
