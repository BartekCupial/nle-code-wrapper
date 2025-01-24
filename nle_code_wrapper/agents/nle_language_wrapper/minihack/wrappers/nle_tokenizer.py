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

        self.observation_space = gym.spaces.Dict()
        self.observation_space.spaces["obs"] = gym.spaces.Box(0, 1000000, shape=(1,), dtype=np.int32)
        self.observation_space.spaces["input_ids"] = gym.spaces.Box(
            0, 1000000, shape=(self.max_token_length,), dtype=np.int32
        )
        self.observation_space.spaces["attention_mask"] = gym.spaces.Box(
            0, 1, shape=(self.max_token_length,), dtype=np.int32
        )
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

    def _convert_obs_to_str(self, obsv):
        text_obsv = ""
        text_obsv += f"Inventory:\n{obsv['text_inventory']}\n\n"
        text_obsv += f"Stats:\n{obsv['text_blstats']}\n\n"
        text_obsv += f"Cursor:\n{obsv['text_cursor']}\n\n"
        text_obsv += f"Stats:\n{obsv['text_glyphs']}\n\n"
        text_obsv += f"Message:\n{obsv['text_message']}"
        return text_obsv

    def reset(self, **kwargs):
        obs, info = super().reset(**kwargs)
        tokenized_obs = self._tokenize(self._convert_obs_to_str(self._nle_obs_to_language(obs)))

        return tokenized_obs, info

    def step(self, action):
        obs, reward, terminated, truncated, info = super().step(action)
        tokenized_obs = self._tokenize(self._convert_obs_to_str(self._nle_obs_to_language(obs)))

        return tokenized_obs, reward, terminated, truncated, info
