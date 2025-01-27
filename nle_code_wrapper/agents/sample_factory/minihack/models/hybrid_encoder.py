import torch
import torch.nn as nn
from sample_factory.algo.utils.torch_utils import calc_num_elements
from sample_factory.model.encoder import Encoder
from sample_factory.utils.typing import Config, ObsSpace

from nle_code_wrapper.agents.sample_factory.minihack.models.chaotic_dwarf import BLStatsEncoder
from nle_code_wrapper.agents.sample_factory.minihack.models.language_encoder import RobertaTransformer
from nle_code_wrapper.agents.sample_factory.minihack.models.terminal_encoder import SimBaCNN


class SimBaHybridEncoder(nn.Module):
    def __init__(
        self,
        obs_space,
        hidden_dim,
        depth,
        use_prev_action: bool = True,
        use_learned_embeddings: bool = False,
        char_edim: int = 16,
        color_edim: int = 16,
        use_max_pool: bool = False,
        expansion: int = 2,
        transformer_hidden_size=64,
        transformer_hidden_layers=2,
        transformer_attention_heads=2,
    ):
        super().__init__()
        self.use_prev_action = use_prev_action
        self.use_learned_embeddings = use_learned_embeddings
        self.char_edim = char_edim
        self.color_edim = color_edim

        self.char_embeddings = nn.Embedding(256, self.char_edim)
        self.color_embeddings = nn.Embedding(128, self.color_edim)
        C, W, H = obs_space["screen_image"].shape
        if self.use_learned_embeddings:
            in_channels = self.char_edim + self.color_edim
        else:
            in_channels = C

        self.screen_encoder = torch.jit.script(
            SimBaCNN(
                in_channels=in_channels,
                hidden_dim=hidden_dim,
                num_blocks=depth,
                use_max_pool=use_max_pool,
                expansion=expansion,
            )
        )
        self.language_encoder = RobertaTransformer(
            obs_space=obs_space,
            transformer_attention_heads=transformer_attention_heads,
            transformer_hidden_layers=transformer_hidden_layers,
            transformer_hidden_size=transformer_hidden_size,
        )
        self.blstats_encoder = torch.jit.script(BLStatsEncoder())

        if self.use_prev_action:
            self.num_actions = obs_space["prev_actions"].n
            self.prev_actions_dim = self.num_actions
        else:
            self.num_actions = None
            self.prev_actions_dim = 0

        screen_shape = (in_channels, W, H)
        bottomline_shape = (obs_space["blstats"].shape[0],)
        self.out_dim = sum(
            [
                calc_num_elements(self.screen_encoder, screen_shape),
                calc_num_elements(self.blstats_encoder, bottomline_shape),
                self.language_encoder.get_out_size(),
                self.prev_actions_dim,
            ]
        )

        self.fc = nn.Sequential(
            nn.Linear(self.out_dim, hidden_dim),
            nn.ELU(inplace=True),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
        )

    def forward(self, obs_dict):
        B, C, H, W = obs_dict["screen_image"].shape

        if self.use_learned_embeddings:
            screen_image = obs_dict["screen_image"]
            chars = screen_image[:, 0]
            colors = screen_image[:, 1]
            chars, colors = self._embed(chars, colors)
            screen_image = self._stack(chars, colors)
        else:
            screen_image = obs_dict["screen_image"]

        encodings = [
            self.language_encoder(obs_dict),
            self.blstats_encoder(obs_dict["blstats"]),
            self.screen_encoder(screen_image.float(memory_format=torch.contiguous_format).view(B, -1, H, W)),
        ]

        if self.use_prev_action:
            prev_actions = obs_dict["prev_actions"].long().view(B)
            encodings.append(torch.nn.functional.one_hot(prev_actions, self.num_actions))

        encodings = self.fc(torch.cat(encodings, dim=1))

        return encodings

    def _embed(self, chars, colors):
        chars = selectt(self.char_embeddings, chars.long(), True)
        colors = selectt(self.color_embeddings, colors.long(), True)
        return chars, colors

    def _stack(self, chars, colors):
        obs = torch.cat([chars, colors], dim=-1)
        return obs.permute(0, 3, 1, 2).contiguous()


def selectt(embedding_layer, x, use_index_select):
    """Use index select instead of default forward to possible speed up embedding."""
    if use_index_select:
        out = embedding_layer.weight.index_select(0, x.view(-1))
        # handle reshaping x to 1-d and output back to N-d
        return out.view(x.shape + (-1,))
    else:
        return embedding_layer(x)


class NLEHybridEncoder(Encoder):
    def __init__(self, cfg: Config, obs_space: ObsSpace):
        super().__init__(cfg)

        self.model = SimBaHybridEncoder(
            obs_space=obs_space,
            hidden_dim=self.cfg.hidden_dim,
            depth=self.cfg.depth,
            use_prev_action=self.cfg.use_prev_action,
            use_learned_embeddings=self.cfg.use_learned_embeddings,
            char_edim=self.cfg.char_edim,
            color_edim=self.cfg.color_edim,
            use_max_pool=self.cfg.use_max_pool,
            expansion=self.cfg.expansion,
            transformer_hidden_size=cfg.transformer_hidden_size,
            transformer_hidden_layers=cfg.transformer_hidden_layers,
            transformer_attention_heads=cfg.transformer_attention_heads,
        )

    def forward(self, x):
        return self.model(x)

    def get_out_size(self):
        return self.cfg.hidden_dim


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
            "True",
            "--use_prev_action",
            "True",
            "--use_learned_embeddings",
            "True",
            "--use_max_pool",
            "True",
            "--pixel_size",
            "1",
            "--tokenize_keys",
            '["text_message", "text_inventory"]',
            "--obs_keys",
            '["screen_image", "blstats", "env_steps", "prev_actions", "input_ids", "attention_mask"]',
        ]
    )

    env = make_env_func_batched(cfg, env_config=AttrDict(worker_index=0, vector_index=0, env_id=0))
    env_info = extract_env_info(env, cfg)

    encoder = NLEHybridEncoder(cfg, env_info.obs_space)
    print(encoder)

    obs, info = env.reset()
    x = encoder(obs)
    print(x.shape)
