env=MiniHack-Corridor-R5-v0
job_name=debug_lm_rl

strategies="['explore_corridor','explore_corridor_systematically','explore_room','explore_room_systematically','fight_closest_monster','goto_closest_corridor','goto_closest_corridor_east','goto_closest_corridor_north','goto_closest_corridor_south','goto_closest_corridor_west','goto_closest_room','goto_closest_room_east','goto_closest_room_north','goto_closest_room_south','goto_closest_room_west','goto_closest_staircase_down','goto_closest_staircase_up','goto_closest_unexplored_corridor','goto_closest_unexplored_room','open_doors','open_doors_kick','open_doors_key','random_move','run_away','search_corridor_for_hidden_doors','search_for_traps','search_room_for_hidden_doors']"

python3 -m nle_code_wrapper.agents.sample_factory.minihack.train --env $env \
    --exp_point $env \
    --train_for_env_steps 10_000_000 \
    --group $env \
    --num_workers 2 \
    --num_envs_per_worker 2 \
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
    --restart_behavior overwrite \
    --experiment $job_name \
    --normalize_returns True \
    --code_wrapper True \
    --hierarchical_gamma True \
    --model ChaoticDwarvenGPT5 \
    --gamma 0.999 \
    --strategies $strategies \
    --use_rnn False \