import torch
from nle import nethack
from sample_factory.algo.utils.torch_utils import calc_num_elements
from sample_factory.model.encoder import Encoder
from sample_factory.utils.typing import Config, ObsSpace
from torch import nn
from torch.nn import functional as F

from nle_code_wrapper.agents.sample_factory.minihack.models.chaotic_dwarf import (
    BottomLinesEncoder,
    CharColorEncoder,
    TopLineEncoder,
)


class RNDModel(Encoder):
    def __init__(self, cfg: Config, obs_space: ObsSpace):
        super().__init__(cfg)
        self.obs_keys = list(sorted(obs_space.keys()))  # always the same order
        self.encoders = nn.ModuleDict()

        self.use_tty_only = cfg.use_tty_only
        self.use_prev_action = cfg.use_prev_action

        # screen encoders
        screen_shape = obs_space["tty_chars"].shape
        self.predictor_screen_encoder = CharColorEncoder(
            (screen_shape[0] - 3, screen_shape[1]),
            char_edim=cfg.char_edim,
            color_edim=cfg.color_edim,
        )
        self.target_screen_encoder = CharColorEncoder(
            (screen_shape[0] - 3, screen_shape[1]),
            char_edim=cfg.char_edim,
            color_edim=cfg.color_edim,
        )

        # top and bottom encoders
        self.predictor_topline_encoder = TopLineEncoder()
        self.predictor_bottomline_encoder = torch.jit.script(BottomLinesEncoder())
        self.target_topline_encoder = TopLineEncoder()
        self.target_bottomline_encoder = torch.jit.script(BottomLinesEncoder())

        if self.use_prev_action:
            self.num_actions = obs_space["prev_actions"].n
            self.prev_actions_dim = self.num_actions
        else:
            self.num_actions = None
            self.prev_actions_dim = 0

        self.encoder_out_size = sum(
            [
                self.predictor_topline_encoder.hidden_dim,
                self.predictor_bottomline_encoder.hidden_dim,
                self.predictor_screen_encoder.hidden_dim,
                self.prev_actions_dim,
            ]
        )

        self.predictor_proj = nn.Linear(self.encoder_out_size, 256)
        self.target_proj = nn.Linear(self.encoder_out_size, 256)

        # MAIN
        self.predictor = nn.Sequential(
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
        )

        self.target = nn.Sequential(
            nn.Linear(256, 512),
        )

        # target network is not trainable
        for name, param in self.named_parameters():
            if name.startswith("target"):
                param.requires_grad = False

    def encode_hidden(self, obs_dict, bottomline_encoder, topline_encoder, screen_encoder, proj):
        B, H, W = obs_dict["tty_chars"].shape
        # to process images with CNNs we need channels dim
        C = 1

        # Take last channel for now
        topline = obs_dict["tty_chars"][:, 0].contiguous()
        bottom_line = obs_dict["tty_chars"][:, -2:].contiguous()

        # Blstats
        blstats_rep = bottomline_encoder(bottom_line.float(memory_format=torch.contiguous_format).view(B, -1))

        encodings = [
            topline_encoder(topline.float(memory_format=torch.contiguous_format).view(B, -1)),
            blstats_rep,
        ]

        # Main obs encoding
        tty_chars = (
            obs_dict["tty_chars"][:, 1:-2]
            .contiguous()
            .float(memory_format=torch.contiguous_format)
            .view(B, C, H - 3, W)
        )
        tty_colors = obs_dict["tty_colors"][:, 1:-2].contiguous().view(B, C, H - 3, W)
        encodings.append(screen_encoder(tty_chars, tty_colors))

        if self.use_prev_action:
            prev_actions = obs_dict["prev_actions"].long().view(B)
            encodings.append(torch.nn.functional.one_hot(prev_actions, self.num_actions))

        concat = torch.cat(encodings, dim=1)

        return proj(concat)

    def forward(self, obs_dict):
        predict_hidden = self.encode_hidden(
            obs_dict,
            self.predictor_bottomline_encoder,
            self.predictor_topline_encoder,
            self.predictor_screen_encoder,
            self.predictor_proj,
        )
        target_hidden = self.encode_hidden(
            obs_dict,
            self.target_bottomline_encoder,
            self.target_topline_encoder,
            self.target_screen_encoder,
            self.target_proj,
        )

        predict_feature = self.predictor(predict_hidden)
        target_feature = self.target(target_hidden)

        return predict_feature, target_feature
