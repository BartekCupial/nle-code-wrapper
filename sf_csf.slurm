#!/bin/bash
#SBATCH --job-name=sf_csf_minihack
#SBATCH --output=slurm_output/%x-%j.out
#SBATCH -N 1 #nodes
#SBATCH -n 1 #tasks
#SBATCH --cpus-per-task=15
#SBATCH --mem=50G
#SBATCH --time=0-23:59:59    # Run for 23:59:59 hours
#SBATCH --gres=gpu:1
#SBATCH -w node211,node210,node030,node031

export SLURM_TMPDIR=/n/fs/scratch/jtuyls

job_name=$1
skill_dim=$2
normalize_returns=$3
csf_lam=$4
env=$5
duplicate_skills=$6
env_seed=$7
skill_type=$8
num_epochs=$9
num_batches_per_epoch=${10}
vtrace=${11}
te_lr=${12}
lr=${13}
batch_size=${14}
max_grad_norm=${15}
skill_method=${16}
exploration_loss_coeff=${17}

python3 -m nle_code_wrapper.agents.sample_factory.minihack.train --env $env \
    --exp_point $env \
    --train_for_env_steps 400_000_000 \
    --group $env \
    --num_workers 16 \
    --num_envs_per_worker 32 \
    --worker_num_splits 2 \
    --rollout 32 \
    --batch_size $batch_size \
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
    --num_negative_z 256 \
    --normalize_returns $normalize_returns \
    --csf_lam $csf_lam \
    --duplicate_skills $duplicate_skills \
    --policy_initialization xavier_uniform \
    --env_seed $env_seed \
    --use_topline False \
    --use_bottomline False \
    --save_milestones_sec 1800 \
    --skill_type $skill_type \
    --num_epochs $num_epochs \
    --num_batches_per_epoch $num_batches_per_epoch \
    --with_vtrace $vtrace \
    --te_learning_rate $te_lr \
    --learning_rate $lr \
    --max_grad_norm $max_grad_norm \
    --skill_method $skill_method \
    --exploration_loss_coeff $exploration_loss_coeff


exit 0