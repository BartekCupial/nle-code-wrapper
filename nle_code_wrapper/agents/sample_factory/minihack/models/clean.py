import torch
import torch.nn as nn


class CleanNet(nn.Module):
    def __init__(self):
        super().__init__()
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

        chars = self.char_embed(x["chars"].int())
        chars = torch.permute(chars, (0, 3, 1, 2))
        chars = self.chars_net(chars)

        concat = torch.cat([blstats, chars], dim=1)
        return self.proj(concat)

    def forward(self, x):
        return self.encode_observations(x)
