import gymnasium as gym


class NoProgressFeedback(gym.Wrapper):
    def __init__(self, env):
        super().__init__(env)

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)

        return self.populate_obs(obs, info), reward, terminated, truncated, info

    def populate_obs(self, obs, info):
        obs["text_feedback"] = ""

        extra_stats = info.get("episode_extra_stats", {})
        if "env_steps" in extra_stats:
            env_steps = extra_stats["env_steps"]

            if env_steps == 0:
                obs["text_feedback"] = "Your strategy did not result in any progress. Try a different one."

        return obs
