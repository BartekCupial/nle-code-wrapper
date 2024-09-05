import ast


def add_extra_params_minihack_env(parser):
    """
    Specify any additional command line arguments for NetHack environments.
    """
    # TODO: add help
    p = parser
    p.add_argument("--character", type=str, default="@")
    p.add_argument("--max_episode_steps", type=int, default=None)
    p.add_argument("--penalty_step", type=float, default=0.0)
    p.add_argument("--penalty_time", type=float, default=0.001)
    p.add_argument("--reward_shaping_coefficient", type=float, default=0.1)
    p.add_argument("--fn_penalty_step", type=str, default="constant")
    p.add_argument("--savedir", type=str, default=None)
    p.add_argument("--save_ttyrec_every", type=int, default=0)
    p.add_argument("--gameloaddir", type=ast.literal_eval, default=None)
    p.add_argument("--state_counter", type=str, default=None)
