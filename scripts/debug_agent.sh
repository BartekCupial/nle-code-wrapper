# LLM_MODEL=gpt-4o-2024-08-06
LLM_MODEL=meta-llama/Llama-3.2-3B-Instruct

python3 -u -m nle_code_wrapper.agents.llm.eval \
    agent.type=code_naive \
    agent.max_image_history=0 \
    client.client_name=openai \
    client.model_id=$LLM_MODEL \
    client.client_name=vllm \
    client.base_url=http://0.0.0.0:8080/v1 \
    eval.wandb_save=False \
    eval.num_episodes.minihack=1 \
    tasks.minihack_tasks=[MiniHack-Corridor-R3-v0] \
    code_wrapper=True \
    use_language_action=False \
    strategies=[explore_corridor,explore_corridor_east,explore_corridor_north,explore_corridor_south,explore_corridor_systematically,explore_corridor_systematically_east,explore_corridor_systematically_north,explore_corridor_systematically_south,explore_corridor_systematically_west,explore_corridor_west,explore_room,explore_room_east,explore_room_north,explore_room_south,explore_room_systematically,explore_room_systematically_east,explore_room_systematically_north,explore_room_systematically_south,explore_room_systematically_west,explore_room_west,explore_items,goto_closest_corridor,goto_closest_corridor_east,goto_closest_corridor_north,goto_closest_corridor_south,goto_closest_corridor_west,goto_closest_room,goto_closest_room_east,goto_closest_room_north,goto_closest_room_south,goto_closest_room_west,goto_closest_staircase_down,goto_closest_staircase_up,goto_closest_unexplored_corridor,goto_closest_unexplored_room,open_doors,open_doors_kick,search_corridor_for_hidden_doors,search_room_for_hidden_doors] \
    eval.max_steps_per_episode=5 \