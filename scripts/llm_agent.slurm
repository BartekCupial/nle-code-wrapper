#!/bin/bash
#SBATCH --job-name=llm_agent
#SBATCH --output=slurm_output/%x-%j.out
#SBATCH -N 1 #nodes
#SBATCH -n 1 #tasks
#SBATCH --cpus-per-task=4
#SBATCH --mem=40G
#SBATCH --time=0-23:59:59    # Run for 23:59:59 hours
#SBATCH --gres=gpu:1
#SBATCH -w node211

# Default values
AGENT_TYPE="" # OPTIONS: # OPTIONS: code_naive, code_cot, cot, naive
LLM_MODEL="" # OPTIONS: gpt-4o-2024-08-06, meta-llama/Llama-3.2-3B-Instruct
TASK=""
DEBUG="False" # OPTIONS: True, False

# Parse command line arguments
while [ $# -gt 0 ]; do
  case $1 in
    --agent_type=*)
      AGENT_TYPE="${1#*=}"
      ;;
    --llm_model=*)
      LLM_MODEL="${1#*=}"
      ;;
    --task=*)
      TASK="${1#*=}"
      ;;
    --debug=*)
      DEBUG="${1#*=}"
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
  shift
done

# Validate required arguments
if [ -z "$AGENT_TYPE" ] || [ -z "$LLM_MODEL" ] || [ -z "$TASK" ]; then
  echo "Usage: $0 --agent_type=... --llm_model=... --task=... [--debug=...]"
  exit 1
fi

# Base script
base_script="python3 -u -m nle_code_wrapper.agents.llm.eval \
 agent.type=$AGENT_TYPE \
 agent.max_image_history=0 \
 client.client_name=openai \
 client.model_id=$LLM_MODEL \
 tasks.minihack_tasks=[$TASK]"

# DEBUG flags
if [ "$DEBUG" == "True" ]; then
  base_script="$base_script \
  eval.max_steps_per_episode=20 \
  eval.wandb_save=False \
  eval.num_episodes.minihack=1 \
  strategies=[goto_corridor,goto_corridor_north,goto_corridor_south,goto_corridor_east,goto_corridor_west,goto_room,goto_room_north,goto_room_south,goto_room_east,goto_room_west,explore_room,explore_room_north,explore_room_south,explore_room_west,explore_room_east] \
  client.generate_kwargs.temperature=0.7"
else
  base_script="$base_script \
  eval.max_steps_per_episode=100 \
  eval.wandb_save=True \
  eval.num_episodes.minihack=3"
fi

# LLM model flags
if [ "$LLM_MODEL" == "meta-llama/Llama-3.2-3B-Instruct" ]; then
  base_script="$base_script \
  client.client_name=vllm \
  client.base_url=http://0.0.0.0:8080/v1"
fi

# AGENT TYPE flags
case $AGENT_TYPE in
  code_naive|code_cot)
    base_script="$base_script \
    code_wrapper=True \
    use_language_action=False"
    ;;
  cot|naive)
    base_script="$base_script \
    code_wrapper=False \
    use_language_action=True"
    ;;
  *)
    echo "Invalid AGENT_TYPE: $AGENT_TYPE"
    exit 1
    ;;
esac

# Run script
if [[ "$LLM_MODEL" =~ ^meta-llama ]]; then
  server_script="vllm serve $LLM_MODEL --port 8080"
  echo "Running server: $server_script"
  eval $server_script &
  sleep 20
fi

echo "Running main script: $base_script"
eval $base_script

# SAMPLE USAGE
# sh scripts/llm_agent.slurm --agent_type=code_naive --llm_model=meta-llama/Llama-3.2-3B-Instruct --task=MiniHack-Corridor-R3-v0 --debug=True
# sh scripts/llm_agent.slurm --agent_type=code_naive --llm_model=gpt-4o-2024-08-06 --task=MiniHack-Corridor-R3-v0 --debug=True