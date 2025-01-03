EVAL_NUM_EPISODES=5
LLM_MODEL=gpt-4o-2024-08-06
AGENT_TYPE=code_naive

# ALL ENVS
# MiniHack-Corridor-R3-v0 MiniHack-CorridorBattle-v0 MiniHack-KeyRoom-S5-v0 MiniHack-River-Narrow-v0 MiniHack-HideNSeek-v0

# ENV: MiniHack-Corridor-R3-v0
# python3 -u -m nle_code_wrapper.agents.llm.eval \
#   agent.type=$AGENT_TYPE \
#   agent.max_image_history=0 \
#   client.client_name=openai \
#   client.model_id=$LLM_MODEL \
#   eval.wandb_save=True \
#   eval.num_episodes.minihack=$EVAL_NUM_EPISODES \
#   tasks.minihack_tasks=[MiniHack-Corridor-R3-v0] \
#   code_wrapper=True \
#   strategies=[goto_stairs,open_doors_kick,explore,search] \
#   use_language_action=False

# ENV: MiniHack-CorridorBattle-v0
# python3 -u -m nle_code_wrapper.agents.llm.eval \
#   agent.type=$AGENT_TYPE \
#   agent.max_image_history=0 \
#   client.client_name=openai \
#   client.model_id=$LLM_MODEL \
#   eval.wandb_save=True \
#   eval.num_episodes.minihack=$EVAL_NUM_EPISODES \
#   tasks.minihack_tasks=[MiniHack-CorridorBattle-v0] \
#   code_wrapper=True \
#   strategies=[goto_stairs,run_away,fight_closest_monster,explore] \
#   use_language_action=False

# ENV: MiniHack-KeyRoom-S5-v0
python3 -u -m nle_code_wrapper.agents.llm.eval \
  agent.type=$AGENT_TYPE \
  agent.max_image_history=0 \
  client.client_name=openai \
  client.model_id=$LLM_MODEL \
  eval.wandb_save=True \
  eval.num_episodes.minihack=$EVAL_NUM_EPISODES \
  tasks.minihack_tasks=[MiniHack-KeyRoom-S5-v0] \
  code_wrapper=True \
  strategies=[goto_closest_staircase_down] \
  use_language_action=False