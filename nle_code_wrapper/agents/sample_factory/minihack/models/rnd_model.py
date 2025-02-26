from typing import Dict

import numpy as np
import torch
from sample_factory.algo.utils.torch_utils import calc_num_elements
from sample_factory.model.encoder import Encoder
from sample_factory.utils.normalize import EPS, RunningMeanStdDictInPlace, copy_dict_structure, iter_dicts_recursively
from sample_factory.utils.typing import Config, ObsSpace
from torch import nn


class ObservationNormalizer(nn.Module):
    def __init__(self, obs_space, cfg):
        super().__init__()

        self.sub_mean = cfg.obs_subtract_mean
        self.scale = cfg.obs_scale

        self.running_mean_std = RunningMeanStdDictInPlace(obs_space, ["screen_image"])

        self.should_sub_mean = abs(self.sub_mean) > EPS
        self.should_scale = abs(self.scale - 1.0) > EPS
        self.should_normalize = self.should_sub_mean or self.should_scale or self.running_mean_std is not None

    @staticmethod
    def _clone_tensordict(obs_dict: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        obs_clone = copy_dict_structure(obs_dict)  # creates an identical dict but with None values
        for d, d_clone, k, x, _ in iter_dicts_recursively(obs_dict, obs_clone):
            if x.dtype != torch.float:
                # type conversion requires a copy, do this check to make sure we don't do it twice
                d_clone[k] = x.float()  # this will create a copy of a tensor
            else:
                d_clone[k] = x.clone()  # otherwise, we explicitly clone it since normalization is in-place

        return obs_clone

    def forward(self, obs_dict: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        if not self.should_normalize:
            return obs_dict

        with torch.no_grad():
            # since we are creating a clone, it is safe to use in-place operations
            obs_clone = self._clone_tensordict(obs_dict)

            # subtraction of mean and scaling is only applied to default "obs"
            # this should be modified for custom obs dicts
            if self.should_sub_mean:
                obs_clone["obs"].sub_(self.sub_mean)

            if self.should_scale:
                obs_clone["obs"].mul_(1.0 / self.scale)

            if self.running_mean_std:
                self.running_mean_std(obs_clone)  # in-place normalization

        return obs_clone


def layer_init(layer, std=np.sqrt(2), bias_const=0.0):
    torch.nn.init.orthogonal_(layer.weight, std)
    torch.nn.init.constant_(layer.bias, bias_const)
    return layer


class RNDModel(Encoder):
    def __init__(self, cfg: Config, obs_space: ObsSpace):
        super().__init__(cfg)

        self.obs_normalizer: ObservationNormalizer = ObservationNormalizer(obs_space, cfg)

        # Predictor Network
        self.predictor_chars_net = nn.Sequential(
            layer_init(nn.Conv2d(2, 32, 3, stride=1)),
            nn.ReLU(),
            layer_init(nn.Conv2d(32, 64, 3, stride=1)),
            nn.ReLU(),
            layer_init(nn.Conv2d(64, 64, 3, stride=1)),
            nn.ReLU(),
            nn.Flatten(),
        )
        self.predictor_proj = nn.Linear(9216, 256)
        self.predictor = nn.Sequential(
            layer_init(nn.Linear(256, 512)),
            nn.ReLU(),
            layer_init(nn.Linear(512, 512)),
            nn.ReLU(),
            layer_init(nn.Linear(512, 512)),
        )

        # Target Network
        self.target_chars_net = nn.Sequential(
            layer_init(nn.Conv2d(2, 32, 3, stride=1)),
            nn.ReLU(),
            layer_init(nn.Conv2d(32, 64, 3, stride=1)),
            nn.ReLU(),
            layer_init(nn.Conv2d(64, 64, 3, stride=1)),
            nn.ReLU(),
            nn.Flatten(),
        )
        self.target_proj = nn.Linear(9216, 256)
        self.target = nn.Sequential(
            layer_init(nn.Linear(256, 512)),
        )

        # target network is not trainable
        for name, param in self.named_parameters():
            if name.startswith("target"):
                param.requires_grad = False

    def encode_hidden(self, obs_dict, chars_net, proj):
        chars = chars_net(obs_dict["screen_image"])
        return proj(chars)

    def forward(self, obs_dict):
        predict_hidden = self.encode_hidden(
            obs_dict,
            self.predictor_chars_net,
            self.predictor_proj,
        )
        target_hidden = self.encode_hidden(
            obs_dict,
            self.target_chars_net,
            self.target_proj,
        )

        predict_feature = self.predictor(predict_hidden)
        target_feature = self.target(target_hidden)

        return predict_feature, target_feature


if __name__ == "__main__":
    import gym
    import nle

    env = gym.make("NetHackScore-v0")
    obs = env.reset()
