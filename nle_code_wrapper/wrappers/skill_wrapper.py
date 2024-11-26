import gymnasium as gym
import numpy as np
from minihack.tiles.glyph_mapper import GlyphMapper


class SkillWrapper(gym.Wrapper):
    def __init__(self, env, skill_dim: int, skill_type: str = "continuous"):
        super().__init__(env)

        self.env = env

        self.skill_dim = skill_dim
        self.skill = None
        self.skill_type = skill_type

        self._glyph_mapper = GlyphMapper()

        self.observation_space = gym.spaces.Dict(
            {
                "option": gym.spaces.Box(
                    low=np.finfo(np.float32).min, high=np.finfo(np.float32).max, shape=(skill_dim,), dtype=np.float32
                ),
                **self.env.observation_space,
            }
        )

        self.last_observation = None

    def reset(self, *args, **kwargs):
        obs, info = self.env.reset(*args, **kwargs)

        self.last_observation = obs

        # Generate a new skill for the entire episode
        if self.skill_type == "continuous":
            unnormalized_skill = np.random.randn(self.skill_dim)
            self.skill = unnormalized_skill / np.linalg.norm(unnormalized_skill, keepdims=True)
        elif self.skill_type == "discrete":
            # generate one-hot skill
            self.skill = np.zeros(self.skill_dim)
            self.skill[np.random.randint(self.skill_dim)] = 1.0

        obs["option"] = self.skill

        return obs, info

    def step(self, *args, **kwargs):
        obs, reward, terminated, truncated, info = self.env.step(*args, **kwargs)

        self.last_observation = obs

        obs["option"] = self.skill

        return obs, reward, terminated, truncated, info

    def render(self, *args, **kwargs):
        return self._glyph_mapper.to_rgb(self.last_observation["glyphs_crop"]).transpose(2, 0, 1)
