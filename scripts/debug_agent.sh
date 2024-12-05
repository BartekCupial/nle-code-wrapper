LLM_MODEL=gpt-4o-2024-08-06

python3 -u -m nle_code_wrapper.agents.llm.eval \
    agent.type=code_cot \
    agent.max_image_history=0 \
    client.client_name=openai \
    client.model_id=$LLM_MODEL \
    eval.wandb_save=False \
    eval.num_episodes.minihack=1 \
    tasks.minihack_tasks=[MiniHack-CorridorBattle-v0] \
    code_wrapper=True \
    use_language_action=False \
    strategies=[goto_stairs,run_away,fight_closest_monster,explore]
    # eval.max_steps_per_episode=5 \