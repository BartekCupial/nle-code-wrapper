"""
Adapted from NLE-language-wrapper https://github.com/ngoodger/nle-language-wrapper
"""

import torch
import torch.nn as nn
from sample_factory.model.encoder import Encoder
from sample_factory.utils.typing import Config, ObsSpace
from transformers import RobertaConfig, RobertaModel


class RobertaTransformer(nn.Module):
    def __init__(
        self,
        obs_space,
        transformer_hidden_size=64,
        transformer_attention_heads=2,
        transformer_hidden_layers=2,
    ):
        super().__init__()
        config = RobertaConfig(
            attention_probs_dropout_prob=0.0,
            bos_token_id=0,
            classifier_dropout=None,
            eos_token_id=2,
            hidden_act="gelu",
            hidden_dropout_prob=0.0,
            hidden_size=transformer_hidden_size,
            initializer_range=0.02,
            intermediate_size=transformer_hidden_size,
            layer_norm_eps=1e-05,
            max_position_embeddings=obs_space["input_ids"].shape[0] + 2,  # Roberta requires max sequence length + 2.
            model_type="roberta",
            num_attention_heads=transformer_attention_heads,
            num_hidden_layers=transformer_hidden_layers,
            pad_token_id=1,
            position_embedding_type="absolute",
            transformers_version="4.17.0",
            type_vocab_size=1,
            use_cache=False,
            vocab_size=50265,
        )
        self.model = RobertaModel(config=config)
        self.encoder_out_size = self.model.config.hidden_size

    def get_out_size(self):
        return self.encoder_out_size

    def device_and_type_for_input_tensor(self, input_tensor_name):  # pylint: disable=['unused-argument']
        return "cuda", torch.int32  # pylint: disable=['no-member']

    def forward(self, obs_dict):
        input_ids = obs_dict["input_ids"]
        attention_mask = obs_dict["attention_mask"]
        # Input transformation to allow for sample factory enjoy
        if len(input_ids.shape) == 3:
            input_ids = input_ids.squeeze(0)
            attention_mask = attention_mask.squeeze(0)
        if input_ids.dtype == torch.float32:  # pylint: disable=['no-member']
            input_ids = input_ids.long()
            attention_mask = attention_mask.long()
        output = self.model(input_ids=input_ids, attention_mask=attention_mask)
        return output.last_hidden_state[:, 0]


class NLELanguageTransformerEncoder(Encoder):
    def __init__(self, cfg: Config, obs_space: ObsSpace):
        super().__init__(cfg)

        self.model = RobertaTransformer(
            obs_space=obs_space,
            transformer_hidden_size=cfg.transformer_hidden_size,
            transformer_attention_heads=cfg.transformer_attention_heads,
            transformer_hidden_layers=cfg.transformer_hidden_layers,
        )

    def forward(self, x):
        return self.model(x)

    def get_out_size(self):
        return self.model.encoder_out_size


if __name__ == "__main__":
    from sample_factory.algo.utils.env_info import extract_env_info
    from sample_factory.algo.utils.make_env import make_env_func_batched
    from sample_factory.utils.attr_dict import AttrDict

    from nle_code_wrapper.agents.sample_factory.minihack.train import parse_minihack_args, register_minihack_components

    register_minihack_components()
    cfg = parse_minihack_args(
        argv=[
            "--env=MiniHack-Corridor-R5-v0",
            "--add_image_observation",
            "False",
            "--use_prev_action",
            "False",
            "--tokenize_keys",
            '["text_glyphs", "text_message", "text_blstats", "text_inventory", "text_cursor"]',
            "--obs_keys",
            '["input_ids", "attention_mask", "env_steps"]',
        ]
    )

    env = make_env_func_batched(cfg, env_config=AttrDict(worker_index=0, vector_index=0, env_id=0))
    env_info = extract_env_info(env, cfg)

    obs, info = env.reset()
    encoder = NLELanguageTransformerEncoder(cfg, env_info.obs_space)
    print(encoder)
    x = encoder(obs)
    print(x.shape)
