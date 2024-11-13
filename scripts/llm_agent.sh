EVAL_NUM_EPISODES=5
LLM_MODEL=gpt-4o-2024-08-06

# DEBUG SETTINGS
# EVAL_NUM_EPISODES=1

# NAIVE AGENT EVALUATION
# AGENT_TYPE=naive

# REACT AGENT EVALUATION
AGENT_TYPE=cot

# python3 -u -m nle_code_wrapper.agents.llm.eval \
#     agent.type=$AGENT_TYPE \
#     agent.max_image_history=0 \
#     client.client_name=openai \
#     client.model_id=$LLM_MODEL \
#     eval.wandb_save=True \
#     eval.num_episodes.minihack=$EVAL_NUM_EPISODES \
#     tasks.minihack_tasks=[MiniHack-KeyRoom-S5-v0] \
#     eval.max_steps_per_episode=5 \

for env in MiniHack-Corridor-R3-v0 MiniHack-CorridorBattle-v0 MiniHack-KeyRoom-S5-v0 MiniHack-River-Narrow-v0 MiniHack-HideNSeek-v0
do
  python3 -u -m nle_code_wrapper.agents.llm.eval \
    agent.type=$AGENT_TYPE \
    agent.max_image_history=0 \
    client.client_name=openai \
    client.model_id=$LLM_MODEL \
    eval.wandb_save=True \
    eval.num_episodes.minihack=$EVAL_NUM_EPISODES \
    tasks.minihack_tasks=[${env}]
done