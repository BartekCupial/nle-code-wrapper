import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from transformers.generation import GenerationConfig

model_id = "meta-llama/Llama-3.2-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token_id = tokenizer.eos_token_id  # TODO: I'm still not entirely sure if this is the right thing to do
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16)
# model.config.pad_token_id = model.config.eos_token_id
model.to("cuda")
model.eval()

system_prompt = """
You are an agent playing MiniHack. The following are the possible high-level strategies you can take in the game, followed by a short description of each strategy:

- explore_corridor
- explore_corridor_systematically
- explore_room
- explore_room_systematically
- fight_closest_monster
- goto_closest_corridor
- goto_closest_corridor_east
- goto_closest_corridor_north
- goto_closest_corridor_south
- goto_closest_corridor_west
- goto_closest_room
- goto_closest_room_east
- goto_closest_room_north
- goto_closest_room_south
- goto_closest_room_west
- goto_closest_staircase_down
- goto_closest_staircase_up
- goto_closest_unexplored_corridor
- goto_closest_unexplored_room
- open_doors
- open_doors_kick
- open_doors_key
- random_move
- run_away
- search_corridor_for_hidden_doors
- search_for_traps
- search_room_for_hidden_doors


Each observation in the game is character-based. Here is a legend for what each character represents in the observation:
    @: the player
    #: a corridor
    +: a closed door
    |: a vertical wall
    -: a horizontal wall
    .: the floor
    <: stairs leading up
    >: stairs leading down

Please output the strategy you would like to take when prompted with an observation in the following format:
STRATEGY: <your_strategy>
Note that you can only pick from the strategies given above.
"""

obs_1 = """
Hello Agent, welcome to NetHack!  You are a chaotic male human Rogue.



                               -----------
                               +......@..|
                               |..........
                               ..........|
                               |.........|
                               -----------












Agent the Footpad              St:17 Dx:18 Co:13 In:11 Wi:8 Ch:8 Chaotic S:0
Dlvl:1 $:0 HP:12(12) Pw:2(2) AC:7 Xp:1/0
"""

obs_2 = """
Hello Agent, welcome to NetHack!



                               -----------
                               |.........|
                               |..........
                               .....@....|
                               |.........|
                               -----------












Agent the Angel              St:17 Dx:18 Co:13 In:11 Wi:8 Ch:8 Chaotic S:0
Dlvl:1 $:0 HP:12(12) Pw:2(2) AC:7 Xp:1/0
"""

messages = [
    [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": obs_1},
    ],
    [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": obs_2},
    ],
]

inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    continue_final_message=False,  # TODO: double check this
    return_dict=True,
    return_tensors="pt",
    padding=True,
    # **tokenizer_kwargs, # TODO: check if anything else needed here
)


for key in inputs:
    inputs[key] = inputs[key].to("cuda")

# NOTE: this is based on the code internals of model.generate
pad_token_id = model.config.eos_token_id[0]
# breakpoint()
generation_config = GenerationConfig(
    bos_token_id=128000,
    do_sample=False,  # TODO: change back to True!
    eos_token_id=[128001, 128008, 128009],
    temperature=0.6,
    top_p=0.9,
)

generated_sequence = model.generate(
    **inputs,
    max_new_tokens=256,
    output_scores=True,
    return_dict_in_generate=True,
    generation_config=generation_config,
    # **generate_kwargs # TODO: check if anything else needed here
)

# Generated tokens and their logits
logits = generated_sequence.scores  # A list of logits for each generated step
generated_tokens = generated_sequence.sequences[:, inputs["input_ids"].shape[1] :]  # Only the newly generated tokens

# Calculate log probabilities
logits = torch.stack(logits)  # T x B x V
logits = logits.permute(1, 0, 2)  # Rearrange to B x T x V
log_softmaxed_logits = F.log_softmax(logits, dim=-1)  # Shape: B x T x V
gathered_log_probs = log_softmaxed_logits.gather(dim=2, index=generated_tokens.unsqueeze(-1))  # Shape: B x T x 1
gathered_log_probs = gathered_log_probs.squeeze(-1)  # Shape: B x T

padding_mask = generated_tokens != pad_token_id  # Shape: B x T
masked_log_probs = gathered_log_probs.masked_fill(~padding_mask, 0.0)

total_log_prob = masked_log_probs.sum(dim=1)  # Shape: B

print("Log Probability of the Generated Sequence:", total_log_prob)

# generated_sequence = generated_sequence.sequences.cpu().numpy().tolist()
generated_sequence = generated_tokens.cpu().numpy().tolist()
for sequence in generated_sequence:
    text = tokenizer.decode(
        sequence,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True,
    )

    print(text)
    # prompt_length = len(
    #     tokenizer.decode(
    #         inputs["input_ids"][0],
    #         skip_special_tokens=True,
    #         clean_up_tokenization_spaces=True,
    #     )
    # )
    # text = text[prompt_length:]

# print(text)
# breakpoint()
# # print()


pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype=torch.bfloat16,
    device_map="cuda",
    # model_kwargs={"attn_implementation": "flash_attention_2"} # NOTE: flash attention messes up generations for some reason, turn off for now
)

pipe.tokenizer.pad_token = pipe.tokenizer.eos_token

outputs = pipe(
    messages,
    max_new_tokens=256,
    batch_size=2,
    # return_dict_in_generate=True,
    # output_scores=True
)
print()
print()
print(outputs[0][0]["generated_text"][-1])
print(outputs[1][0]["generated_text"][-1])
