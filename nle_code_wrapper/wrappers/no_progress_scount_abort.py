import gymnasium as gym
import numpy as np
from nle import nethack


class NoProgressScoutAbort(gym.Wrapper):
    def __init__(self, env, no_progress_timeout=300):
        super().__init__(env)
        self.no_progress_timeout = no_progress_timeout

    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
        self.last_explored = np.sum(self.bot.glyphs != nethack.GLYPH_CMAP_OFF)
        self.no_progress_count = 0

        return obs, info

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)

        explored = np.sum(self.bot.glyphs != nethack.GLYPH_CMAP_OFF)
        if explored != self.last_explored:
            self.last_explored = explored
            self.no_progress_count = 0
        else:
            self.no_progress_count += 1

        if self.no_progress_count >= self.no_progress_timeout:
            terminated = True

        return obs, reward, terminated, truncated, info
