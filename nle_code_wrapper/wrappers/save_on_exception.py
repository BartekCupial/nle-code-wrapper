import os
import pickle
import traceback
from pathlib import Path

import gymnasium as gym
from nle import nethack
from nle_utils.utils.utils import log

from nle_code_wrapper.utils.seed import get_unique_seed


class SaveOnException(gym.Wrapper):
    def __init__(self, env, failed_game_path: str = None):
        super().__init__(env)

        self.failed_game_path = failed_game_path
        self.episode_number = 0

    def reset(self, *, seed=None, **kwargs):
        self.recorded_seed = seed if seed is not None else get_unique_seed(episode_idx=self.episode_number)
        self.recorded_actions = []
        self.named_actions = []
        self.episode_number += 1

        try:
            return super().reset(seed=self.recorded_seed, **kwargs)
        except Exception as e:
            log.error(f"Bot failed due to unhandled exception: {str(e)}\n{traceback.format_exc()}")
            self.save_to_file()

            return self.observation_space.sample(), {}

    def step(self, action):
        try:
            self.recorded_actions.append(action)
            return super().step(action)
        except Exception as e:
            log.error(f"Bot failed due to unhandled exception: {str(e)}\n{traceback.format_exc()}")
            self.save_to_file()

            return self.observation_space.sample(), 0, True, False, {}

    def save_to_file(self):
        dat = {
            "seed": self.recorded_seed,
            "actions": self.recorded_actions,
            "last_observation": self.env.unwrapped.last_observation,
        }
        og_ttyrec = self.env.unwrapped.nethack._ttyrec
        if og_ttyrec is not None:
            ttyrec = Path(og_ttyrec).stem
        else:
            ttyrec_prefix = f"nle.{os.getpid()}.{self.recorded_seed}"
            ttyrec_version = f".ttyrec{nethack.TTYREC_VERSION}.bz2"
            ttyrec = ttyrec_prefix + ttyrec_version

        fname = os.path.join(self.failed_game_path, f"{ttyrec}.demo")
        with open(fname, "wb") as f:
            log.debug(f"Saving demo to {fname}...")
            pickle.dump(dat, f)
