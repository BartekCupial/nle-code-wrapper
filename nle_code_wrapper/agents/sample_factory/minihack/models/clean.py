import torch
import torch.nn as nn
from sample_factory.model.encoder import Encoder
from sample_factory.utils.typing import Config, ObsSpace


class CleanNet(Encoder):
    def __init__(self, cfg: Config, obs_space: ObsSpace):
        super().__init__(cfg)
        self.blstats_net = nn.Sequential(
            nn.Embedding(256, 32),
            nn.Flatten(),
        )

        self.char_embed = nn.Embedding(256, 32)
        self.chars_net = nn.Sequential(
            nn.Conv2d(32, 32, 5, stride=(2, 3)),
            nn.ReLU(),
            nn.Conv2d(32, 64, 5, stride=(1, 3)),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, stride=1),
            nn.ReLU(),
            nn.Flatten(),
        )

        self.encoder_out_size = 256
        self.proj = nn.Linear(864 + 960, self.encoder_out_size)

    def get_out_size(self) -> int:
        return self.encoder_out_size

    def encode_observations(self, x):
        blstats = torch.clip(x["blstats"] + 1, 0, 255).int()
        blstats = self.blstats_net(blstats)

        chars = self.char_embed(x["tty_chars"][..., 1:-2, :-1].int())
        chars = torch.permute(chars, (0, 3, 1, 2))
        chars = self.chars_net(chars)

        concat = torch.cat([blstats, chars], dim=1)
        return self.proj(concat)

    def forward(self, x):
        return self.encode_observations(x)


if __name__ == "__main__":
    import gym
    import nle

    env = gym.make("NetHackChallenge-v0")
    x = env.reset()
    blstats = torch.from_numpy(x["blstats"]).unsqueeze(0)
    chars = torch.from_numpy(x["tty_chars"]).unsqueeze(0)[..., 1:-2, :-1]

    blstats_net = nn.Sequential(
        nn.Embedding(256, 32),
        nn.Flatten(),
    )

    char_embed = nn.Embedding(256, 32)
    chars_net = nn.Sequential(
        nn.Conv2d(32, 32, 5, stride=(2, 3)),
        nn.ReLU(),
        nn.Conv2d(32, 64, 5, stride=(1, 3)),
        nn.ReLU(),
        nn.Conv2d(64, 64, 3, stride=1),
        nn.ReLU(),
        nn.Flatten(),
    )

    encoder_out_size = 256
    proj = nn.Linear(864 + 960, encoder_out_size)

    blstats = torch.clip(blstats + 1, 0, 255).int()
    blstats = blstats_net(blstats)

    chars = char_embed(chars.int())
    chars = torch.permute(chars, (0, 3, 1, 2))
    chars = chars_net(chars)

    concat = torch.cat([blstats, chars], dim=1)
    proj(concat)
