env=MiniHack-KeyRoom-Dark-S5-v0

for seed in 0 1
do
    job_name=sf_ppo_${env}_${seed}
    sbatch -A pnlp --job-name $job_name sf_ppo.slurm $job_name $env
done