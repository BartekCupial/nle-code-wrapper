#!/bin/bash
#SBATCH --job-name=sf_metra_minihack
#SBATCH --output=slurm_output/%x-%j.out
#SBATCH -N 1 #nodes
#SBATCH -n 1 #tasks
#SBATCH --cpus-per-task=10
#SBATCH --mem=40G
#SBATCH --time=0-23:59:59    # Run for 23:59:59 hours
#SBATCH --gres=gpu:1
#SBATCH -w node211,node210

export SLURM_TMPDIR=/n/fs/scratch/jtuyls

job_name=$1
skill_dim=$2
normalize_returns=$3
env=$4
duplicate_skills=$5
env_seed=$6
skill_type=$7
num_epochs=$8
num_batches_per_epoch=${9}

python3 -m nle_code_wrapper.agents.sample_factory.minihack.train --env $env \
    --exp_point $env \
    --train_for_env_steps 400_000_000 \
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
    --code_wrapper False \
    --restart_behavior overwrite \
    --experiment $job_name \
    --skill-wrapper True \
    --skill_dim $skill_dim \
    --normalize_returns $normalize_returns \
    --duplicate_skills $duplicate_skills \
    --policy_initialization xavier_uniform \
    --env_seed $env_seed \
    --use_topline False \
    --use_bottomline False \
    --save_milestones_sec 1800 \
    --skill_method METRA \
    --skill_type $skill_type \
    --num_epochs $num_epochs \
    --num_batches_per_epoch $num_batches_per_epoch

exit 0