"""
Adapted from NLE-language-wrapper https://github.com/ngoodger/nle-language-wrapper
"""

from functools import lru_cache

import gymnasium as gym
import numpy as np
import torch
from nle import nle_language_obsv
from transformers import RobertaTokenizerFast


class NLETokenizer(gym.Wrapper):
    LRU_CACHE_SIZE = 1000

    def __init__(self, env, max_token_length):
        super().__init__(env)
        self.max_token_length = max_token_length

        obs_space = {
            "obs": gym.spaces.Box(0, 1000000, shape=(1,), dtype=np.int32),
            "input_ids": gym.spaces.Box(0, 1000000, shape=(self.max_token_length,), dtype=np.int32),
            "attention_mask": gym.spaces.Box(0, 1, shape=(self.max_token_length,), dtype=np.int32),
        }
        if "env_steps" in self.env.observation_space.keys():
            obs_space["env_steps"] = self.env.observation_space.spaces["env_steps"]

        self.observation_space = gym.spaces.Dict(obs_space)
        self.action_space = self.env.action_space
        self.tokenizer = RobertaTokenizerFast.from_pretrained("distilroberta-base", truncation_side="left")
        self.nle_language = nle_language_obsv.NLELanguageObsv()

    # We use caching to avoid re-tokenizing observations that are already seen.
    @lru_cache(maxsize=LRU_CACHE_SIZE)
    def _tokenize(self, str_obsv):
        tokens = self.tokenizer(
            str_obsv,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=self.max_token_length,
        )
        # Sample factory insists on normalizing obs key.
        tokens.data["obs"] = torch.zeros(1)
        return tokens.data

    def _nle_obs_to_language(self, nle_obs):
        """Translate NLE Observation into a language observation.
        Args:
            nle_obs (dict): NLE observation from the base environment
        Returns:
            (dict): language observation
        """
        glyphs = nle_obs["glyphs"]
        blstats = nle_obs["blstats"]
        tty_cursor = nle_obs["tty_cursor"]
        inv_strs = nle_obs["inv_strs"]
        inv_letters = nle_obs["inv_letters"]
        text_message = (
            nle_obs["text_message"]
            if "text_message" in nle_obs
            else self.nle_language.text_message(nle_obs["tty_chars"]).decode("latin-1")
        )

        return {
            "text_glyphs": self.nle_language.text_glyphs(glyphs, blstats).decode("latin-1"),
            "text_message": text_message,
            "text_blstats": self.nle_language.text_blstats(blstats).decode("latin-1"),
            "text_inventory": self.nle_language.text_inventory(inv_strs, inv_letters).decode("latin-1"),
            "text_cursor": self.nle_language.text_cursor(glyphs, blstats, tty_cursor).decode("latin-1"),
        }

    def _process_obs(self, obs):
        lang_obs = self._nle_obs_to_language(obs)
        text = f"""
Inventory:
{lang_obs['text_inventory']}

Stats:
{lang_obs['text_blstats']}

Cursor:
{lang_obs['text_cursor']}

Observation:
{lang_obs['text_glyphs']}

Message:
{lang_obs['text_message']}
        """
        text_obs = self._tokenize(text)

        if "env_steps" in obs:
            text_obs["env_steps"] = obs["env_steps"]

        return text_obs

    def reset(self, **kwargs):
        obs, info = super().reset(**kwargs)

        return self._process_obs(obs), info

    def step(self, action):
        obs, reward, terminated, truncated, info = super().step(action)

        return self._process_obs(obs), reward, terminated, truncated, info


if __name__ == "__main__":
    import gym
    import nle
    from nle_utils.wrappers import GymV21CompatibilityV0

    env = gym.make("NetHackScore-v0")
    env = GymV21CompatibilityV0(env=env)
    env = NLETokenizer(env, max_token_length=256)

    obs = env.reset()
