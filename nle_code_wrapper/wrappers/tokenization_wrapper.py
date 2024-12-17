from functools import partial
from string import ascii_lowercase, ascii_uppercase
from typing import Any, Callable, Dict, List, Tuple, Union

import gymnasium as gym
import numpy as np
from nle.nethack import actions as A
from nle_utils.wrappers.gym_compatibility import GymV21CompatibilityV0
from numpy import int32, int64, ndarray
from transformers import AutoTokenizer

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy

INSTRUCTION_PROMPT = """
You are an agent playing MiniHack. The following are the possible high-level strategies you can take in the game, followed by a short description of each strategy:

{skill_list}

Each observation in the game is character-based. Here is a legend for what each character represents in the observation:
    @: the player
    #: a corridor
    +: a closed door
    |: a vertical wall
    -: a horizontal wall
    .: the floor
    <: stairs leading up
    >: stairs leading down

Please output the strategy you would like to take when prompted with an observation in the following format:
STRATEGY: <your_strategy>
Note that you can only pick from the strategies given above.
"""


class TokenizationWrapper(gym.Wrapper):
    def __init__(self, env, lm_model_name: str, strategies, lm_max_obs_tokens: int) -> None:
        super().__init__(env)

        self.lm_max_obs_tokens = lm_max_obs_tokens
        self.tokenizer = AutoTokenizer.from_pretrained(lm_model_name)
        self.tokenizer.pad_token = (
            self.tokenizer.eos_token
        )  # TODO: I'm still not entirely sure if this is the right thing to do

        self.pad_token_id = 128001  # TODO: see if we can avoid hardcoding this

        skill_list = ""
        for _, s in enumerate(strategies, 1):
            skill_list += f"- {s}\n"
        self.system_prompt = INSTRUCTION_PROMPT.format(skill_list=skill_list)

        self.observation_space = gym.spaces.Dict(
            {
                "tokenized_tty_chars_input_ids": gym.spaces.Box(
                    low=0,
                    high=self.tokenizer.vocab_size,
                    shape=(self.lm_max_obs_tokens,),
                    dtype=int64,
                ),
                "tokenized_tty_chars_attn_mask": gym.spaces.Box(
                    low=0,
                    high=1,
                    shape=(self.lm_max_obs_tokens,),
                    dtype=int64,
                ),
                **self.env.observation_space,
            }
        )

    def _create_messages_from_obs(self, obs):
        tty_chars = obs["tty_chars"]
        text_obs = ""
        for line in tty_chars:
            text_obs += "".join([chr(c) for c in line]) + "\n"

        message = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text_obs},
        ]

        return message

    def _pad_tokens(self, tokens, pad_token):
        # pad to max so that all obs have the same number of tokens
        cur_length = tokens.shape[1]
        max_length = self.lm_max_obs_tokens
        if cur_length < max_length:
            padding = np.full(
                (tokens.shape[0], max_length - cur_length),
                pad_token,
                dtype=tokens.dtype,
            )
            tokens = np.concatenate([tokens, padding], axis=1)

        return tokens

    def _augment_obs_with_tokens(self, obs):
        message = self._create_messages_from_obs(obs)

        tokenized_message = self.tokenizer.apply_chat_template(
            message,
            add_generation_prompt=True,
            continue_final_message=False,  # TODO: double check this
            return_dict=True,
            return_tensors="np",
            # **tokenizer_kwargs, # TODO: check if anything else needed here
        )

        # padd to fixed length
        tokenized_message["input_ids"] = self._pad_tokens(tokenized_message["input_ids"], pad_token=self.pad_token_id)
        tokenized_message["attention_mask"] = self._pad_tokens(tokenized_message["attention_mask"], pad_token=0)

        obs["tokenized_tty_chars_input_ids"] = tokenized_message["input_ids"]
        obs["tokenized_tty_chars_attn_mask"] = tokenized_message["attention_mask"]

    def step(self, action: List[int]) -> Tuple[Dict[str, ndarray], float, bool, bool, Dict[str, Any]]:
        if isinstance(action, np.ndarray):
            # need to decode action first
            action = self.tokenizer.decode(
                action,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )

        obs, reward, terminated, truncated, info = self.env.step(action)

        self._augment_obs_with_tokens(obs)

        return obs, reward, terminated, truncated, info

    def reset(self, *args, **kwargs) -> Tuple[Dict[str, ndarray], Dict[str, Any]]:
        obs, info = self.bot.reset(*args, **kwargs)
        self._augment_obs_with_tokens(obs)

        return obs, info
