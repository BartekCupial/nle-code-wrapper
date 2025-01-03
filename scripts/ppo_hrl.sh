env=MiniHack-Corridor-R5-v0

for seed in 6 7
do
    job_name=ppo_hrl_${env}_${seed}
    sbatch -A pnlp --job-name $job_name scripts/ppo_hrl.slurm $job_name $env
done