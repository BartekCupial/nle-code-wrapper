import gymnasium as gym


class AddChanngelDim(gym.ObservationWrapper):
    def __init__(self, env):
        super().__init__(env)

        obs_space = self.env.observation_space
        self.obs_keys = list(sorted(obs_space.keys()))  # always the same order

        new_obs_space = {}
        for obs_key in self.obs_keys:
            shape = obs_space[obs_key].shape

            if len(shape) == 1:
                new_obs_space[obs_key] = obs_space[obs_key]
            elif len(shape) > 1:
                new_obs_space[obs_key] = gym.spaces.Box(
                    obs_space[obs_key].low[0][0],
                    obs_space[obs_key].high[0][0],
                    shape=(1,) + obs_space[obs_key].shape,
                    dtype=obs_space[obs_key].dtype,
                )
            else:
                raise NotImplementedError(f"Unsupported observation space {obs_space}")

        self.observation_space = gym.spaces.Dict(new_obs_space)

    def observation(self, observation):
        new_observation = {}
        for obs_key in self.obs_keys:
            shape = observation[obs_key].shape

            if len(shape) == 1:
                new_observation[obs_key] = observation[obs_key]
            elif len(shape) > 1:
                new_observation[obs_key] = observation[obs_key][None, ...]
            else:
                raise NotImplementedError("Unsupported observation")

        return new_observation
