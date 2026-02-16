import os
import pickle
import traceback
from pathlib import Path

import gymnasium as gym
from nle import nethack
from nle.env.base import NLE
from nle_utils.utils.utils import log

from nle_code_wrapper.utils.seed import get_unique_seed


class SaveOnException(gym.Wrapper):
    def __init__(self, env, failed_game_path: str = None, monitor: bool = False, monitor_path: str = None):
        super().__init__(env)

        self.failed_game_path = failed_game_path
        self.monitor_path = monitor_path
        self.monitor = monitor
        self.episode_number = 0

    def reset(self, *, seed=None, **kwargs):
        self.recorded_seed = seed if seed is not None else get_unique_seed(episode_idx=self.episode_number)
        self.recorded_actions = []
        self.named_actions = []
        self.episode_number += 1

        try:
            return self.env.reset(seed=self.recorded_seed, **kwargs)
        except Exception as e:
            message = f"Bot failed due to unhandled exception: {str(e)}\n{traceback.format_exc()}"
            log.error(message)
            self.save_to_file(message=message)

            bot = self.env.get_wrapper_attr("bot")
            obs = bot.last_obs
            info = bot.last_info
            info["end_status"] = NLE.StepStatus.ABORTED

            return obs, info

    def step(self, action):
        try:
            self.recorded_actions.append(action)
            if self.monitor:
                self.save_to_file(game_failed=False)
                obs, reward, terminated, truncated, info = self.env.step(action)
                if terminated or truncated:
                    self.remove_file()
                return obs, reward, terminated, truncated, info
            else:
                return self.env.step(action)
        except Exception as e:
            message = f"Bot failed due to unhandled exception: {str(e)}\n{traceback.format_exc()}"
            log.error(message)
            self.save_to_file(message=message)
            if self.monitor:
                self.remove_file()

            bot = self.env.get_wrapper_attr("bot")
            obs = bot.last_obs
            info = bot.last_info
            info["end_status"] = NLE.StepStatus.ABORTED

            return obs, bot.reward, True, False, info

    def _file_name(self):
        og_ttyrec = self.env.unwrapped.nethack._ttyrec
        if og_ttyrec is not None:
            ttyrec = Path(og_ttyrec).stem
        else:
            ttyrec_prefix = f"nle.{os.getpid()}.{self.recorded_seed}"
            ttyrec_version = f".ttyrec{nethack.TTYREC_VERSION}.bz2"
            ttyrec = ttyrec_prefix + ttyrec_version

        return f"{ttyrec}.demo"

    def save_to_file(self, message="", game_failed: bool = True):
        dat = {
            "seed": self.recorded_seed,
            "actions": self.recorded_actions,
            "last_observation": self.env.unwrapped.last_observation,
            "message": message,
        }

        file_name = self._file_name()
        save_path = self.failed_game_path if game_failed else self.monitor_path
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)
        fname = os.path.join(save_path, file_name)
        with open(fname, "wb") as f:
            log.debug(f"Saving demo to {fname}...")
            pickle.dump(dat, f)

    def remove_file(self):
        save_path = self.monitor_path
        file_name = self._file_name()
        fname = os.path.join(save_path, file_name)
        if os.path.exists(fname):
            os.remove(fname)