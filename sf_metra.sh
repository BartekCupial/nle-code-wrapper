# env=MiniHack-Corridor-R5-v0

for env in MiniHack-Corridor-R5-v0
do 
    for skill_dim in 8
    do
        for normalize_returns in False
        do
            for duplicate_skills in 20
            do
                for env_seed in 0
                do
                    for skill_type in continuous
                    do
                        for num_epochs in 10
                        do
                            for num_batches_per_epoch in 50
                            do
                                for seed in 0 1
                                do
                                    job_name=sf_metra_${env}_${skill_dim}_${normalize_returns}_${seed}_${duplicate_skills}_${env_seed}_${skill_type}_${num_epochs}_${num_batches_per_epoch}
                                    sbatch -A pnlp --job-name $job_name sf_metra.slurm $job_name $skill_dim $normalize_returns $env $duplicate_skills $env_seed $skill_type $num_epochs $num_batches_per_epoch
                                done
                            done
                        done
                    done
                done
            done
        done
    done
done