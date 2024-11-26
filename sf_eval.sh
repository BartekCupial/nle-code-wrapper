experiment_name=sf_CSF_MiniHack-Corridor-R5-v0_4_False_1.0_1_40_0_discrete_10_20_False_1e-4_1e-4_512_1.0_0.001

python3 -m nle_code_wrapper.agents.sample_factory.minihack.enjoy --env MiniHack-Corridor-R5-v0 \
    --experiment $experiment_name \
    --max_num_episodes 10 \
    --save_video \
    # --fps 1 \
    # --save_video \