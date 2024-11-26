#!/bin/bash
#SBATCH --job-name=sf_ppo_minihack
#SBATCH --output=slurm_output/%x-%j.out
#SBATCH -N 1 #nodes
#SBATCH -n 1 #tasks
#SBATCH --cpus-per-task=15
#SBATCH --mem=40G
#SBATCH --time=0-23:59:59    # Run for 23:59:59 hours
#SBATCH --gres=gpu:1
#SBATCH -w node211,node210,node030,node031

job_name=$1
env=$2

python3 -m nle_code_wrapper.agents.sample_factory.minihack.train --env $env \
    --exp_point $env \
    --train_for_env_steps 200_000_000 \
    --group $env \
    --num_workers 16 \
    --num_envs_per_worker 32 \
    --worker_num_splits 2 \
    --rollout 32 \
    --batch_size 4096 \
    --async_rl True \
    --serial_mode False \
    --wandb_user jtuyls \
    --wandb_project nle_code_wrapper \
    --wandb_group jtuyls \
    --with_wandb True \
    --decorrelate_envs_on_one_worker False \
    --restart_behavior overwrite \
    --experiment $job_name \
    --normalize_returns True \
    --code_wrapper False \
    --skill-wrapper False

exit 0