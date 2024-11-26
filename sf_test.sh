experiment_name=skill-MiniHack-Corridor-R3-v0

python3 -m nle_code_wrapper.agents.sample_factory.minihack.train --env MiniHack-Corridor-R3-v0 \
    --exp_point MiniHack-Corridor-R5-v0 \
    --train_for_env_steps 100_000_000 \
    --group MiniHack-Corridor-R5-v0 \
    --num_workers 16 \
    --num_envs_per_worker 32 \
    --worker_num_splits 2 \
    --rollout 32 \
    --batch_size 4096 \
    --async_rl True \
    --serial_mode True \
    --wandb_user jtuyls \
    --wandb_project nle_code_wrapper \
    --wandb_group jtuyls \
    --with_wandb False \
    --decorrelate_envs_on_one_worker False \
    --code_wrapper False \
    --restart_behavior overwrite \
    --experiment $experiment_name \
    --skill-wrapper True \
    --skill_dim 10 \
    --num_negative_z 256 \
    --normalize_returns False \
    --csf_lam 1.0 \
    --duplicate_skills 10 \
    --policy_initialization xavier_uniform \
    --use_inventory False \
    --use_topline False \
    --use_bottomline False \
    --env_seed 0 \
    --save_milestones_sec 3000 \
    --use_topline False \
    --use_bottomline False \
    --num_batches_per_epoch 1 \
    # --skill_method METRA