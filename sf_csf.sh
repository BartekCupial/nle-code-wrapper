# env=MiniHack-Corridor-R5-v0

for skill_method in CSF
do
    for env in MiniHack-Corridor-R5-v0
    do 
        for skill_dim in 4 8
        do
            for normalize_returns in False
            do
                for csf_lam in 1.0
                do
                    for duplicate_skills in 40
                    do
                        for env_seed in 0
                        do
                            for skill_type in discrete
                            do
                                for num_epochs in 1
                                do
                                    for num_batches_per_epoch in 1
                                    do
                                        for vtrace in False
                                        do
                                            for te_lr in 1e-4
                                            do
                                                for lr in $te_lr
                                                do
                                                    for batch_size in 4096
                                                    do
                                                        for max_grad_norm in 1.0
                                                        do
                                                            for exploration_loss_coeff in 0.001
                                                            do
                                                                for seed in 0 1
                                                                do
                                                                    job_name=sf_${skill_method}_${env}_${skill_dim}_${normalize_returns}_${csf_lam}_${seed}_${duplicate_skills}_${env_seed}_${skill_type}_${num_epochs}_${num_batches_per_epoch}_${vtrace}_${te_lr}_${lr}_${batch_size}_${max_grad_norm}_${exploration_loss_coeff}
                                                                    sbatch -A pnlp --job-name $job_name sf_csf.slurm $job_name $skill_dim $normalize_returns $csf_lam $env $duplicate_skills $env_seed $skill_type $num_epochs $num_batches_per_epoch $vtrace $te_lr $lr $batch_size $max_grad_norm $skill_method $exploration_loss_coeff
                                                                done
                                                            done
                                                        done
                                                    done
                                                done
                                            done
                                        done
                                    done
                                done
                            done
                        done
                    done
                done
            done
        done
    done
done