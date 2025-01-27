import ast

from nle_utils.utils.utils import str2bool


def add_extra_params_language_encoder(parser):
    p = parser
    p.add_argument(
        "--transformer_hidden_size",
        type=int,
        default=64,
        help="size of transformer hidden layers",
    )
    p.add_argument(
        "--transformer_hidden_layers",
        type=int,
        default=2,
        help="number of transformer hidden layers",
    )
    p.add_argument(
        "--transformer_attention_heads",
        type=int,
        default=2,
        help="number of transformer attention heads",
    )
    p.add_argument(
        "--max_token_length",
        type=int,
        default=512,
        help="Maximum token input length before truncation",
    )


def add_extra_params_terminal_encoder(parser):
    p = parser
    p.add_argument("--char_edim", type=int, default=16, help="Char Embedding Dim. Defaults to `16`")
    p.add_argument("--color_edim", type=int, default=16, help="Color Embedding Dim. Defaults to `16`")
    p.add_argument("--hidden_dim", type=int, default=128)
    p.add_argument("--depth", type=int, default=1)
    p.add_argument(
        "--use_learned_embeddings",
        type=str2bool,
        default=True,
        help="Do we want to learn the embeddings for chars and colors",
    )
    p.add_argument(
        "--use_max_pool",
        type=str2bool,
        default=True,
        help="Do we want to use max pool in conv net",
    )
    p.add_argument(
        "--expansion",
        type=int,
        default=2,
        help="how much bigger hidden dimention in conv block",
    )


def add_extra_params_general(parser):
    """
    Specify any additional command line arguments for NetHack.
    """
    # TODO: add help
    p = parser
    p.add_argument("--exp_tags", type=str, default="local")
    p.add_argument("--exp_point", type=str, default="point-A")
    p.add_argument("--group", type=str, default="group2")
    p.add_argument("--model", type=str, default="ScaledNet")
    p.add_argument("--model_path", type=str, default=None)
    p.add_argument("--add_stats_to_info", type=str2bool, default=True)


def minihack_override_defaults(_env, parser):
    """RL params specific to NetHack envs."""
    # TODO:
    parser.set_defaults(
        use_record_episode_statistics=False,
        gamma=0.999,  # discounting
        num_workers=12,
        num_envs_per_worker=2,
        worker_num_splits=2,
        train_for_env_steps=2_000_000_000,
        nonlinearity="relu",
        use_rnn=True,
        rnn_type="lstm",
        actor_critic_share_weights=True,
        policy_initialization="orthogonal",
        policy_init_gain=1.0,
        adaptive_stddev=False,  # True only for continous action distributions
        reward_scale=1.0,
        reward_clip=10.0,  # tune?? 30?
        batch_size=1024,
        rollout=32,
        max_grad_norm=4,  # TODO: search
        num_epochs=1,  # TODO: in some atari - 4, maybe worth checking
        num_batches_per_epoch=1,  # can be used for increasing the batch_size for SGD
        ppo_clip_ratio=0.1,  # TODO: tune
        ppo_clip_value=1.0,
        value_loss_coeff=1.0,  # TODO: tune
        exploration_loss="entropy",
        exploration_loss_coeff=0.001,  # TODO: tune
        learning_rate=0.0001,  # TODO: tune
        # lr_schedule="linear_decay", # TODO: test later
        gae_lambda=1.0,  # TODO: here default 0.95, 1.0 means we turn off gae
        with_vtrace=False,
        normalize_input=False,  # TODO: turn off for now and use normalization from d&d, then switch and check what happens
        normalize_returns=True,  # TODO: we should check what works better, normalized returns or vtrace
        async_rl=True,
        experiment_summaries_interval=50,
        adam_beta1=0.9,
        adam_beta2=0.999,
        adam_eps=1e-7,
        seed=22,
        save_every_sec=120,
        encoder_conv_architecture="resnet_impala",
    )
