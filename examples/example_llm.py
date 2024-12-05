import asyncio
import os
import time
from functools import partial
from typing import Any, Dict, List

import aiolimiter
import openai
from aiohttp import ClientSession
from nle_language_wrapper.nle_language_obsv import NLELanguageObsv
from nle_utils.play import play
from tqdm.asyncio import tqdm_asyncio

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotFinished, BotPanic
from nle_code_wrapper.bot.strategy import Strategy
from nle_code_wrapper.bot.strategy.strategies import explore, goto_stairs, open_doors, open_doors_kick, search
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args, register_minihack_components

openai.organization = os.getenv("OPENAI_PERSONAL_ORG_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

LLM_TO_COST = {
    "gpt-4o": {"input": 2.5 / 1e6, "output": 10.0 / 1e6},
}

TTY_CHARS_SYSTEM_PROMPT = """Welcome to the game of MiniHack, a simplified version of NetHack!
Your goal is to find the stairs that lead **down**, not up.

Each observation will be given to you in the form of character symbols that represent the game state.
Here is a complete legend of the symbols you will see:
    + indicates a door
    . indicates a floor tile
    # indicates a corridor
    - indicates a horizontal wall
    | indicates a vertical wall
    @ indicates the player
    > indicates the stairs leading down
    < indicates the stairs leading up

For each observation, you will be able to choose from a fixed number of strategies to execute.
You can choose from:
    (1) goto_stairs: if the stairs leading down are visible, navigates the agent towards the stairs leading **down**
    (2) open_doors_kick: if a door is visible, navigates the agent towards a closed door and performs one kick towards it
    (3) explore: navigates the agent to the closest "boundary cell", i.e. the closest cell that lies at the edge of the explored and to-be-explored areas
    (4) search: navigates the agent to the closest promising cell that hasn't been searched as much and performs one search action, which can reveal secret doors or hidden passages

For each observation, please think step by step, and then output the strategy you'd like to execute in the environment. Your answer should be structured as follows:
Reasoning: <your reasoning for choosing the strategy>
Strategy: <the strategy you'd like to execute>
"""

LANGUAGE_WRAPPER_SYSTEM_PROMPT = """Welcome to the game of MiniHack, a simplified version of NetHack!
Your goal is to find the stairs that lead **down**, not up.

Each observation will be given to you in the form of a textual description of the environment around you.

For each observation, you will be able to choose from a fixed number of strategies to execute.
You can choose from:
    (1) goto_stairs: if the stairs leading down are visible, navigates the agent towards the stairs leading **down**
    (2) open_doors_kick: if a door is visible, navigates the agent towards a closed door and performs one kick towards it
    (3) explore: navigates the agent to the closest "boundary cell", i.e. the closest cell that lies at the edge of the explored and to-be-explored areas
    (4) search: navigates the agent to the closest promising cell that hasn't been searched as much and performs one search action, which can reveal secret doors or hidden passages

For each observation, please think step by step, and then output the strategy you'd like to execute in the environment. Your answer should be structured as follows:
Reasoning: <your reasoning for choosing the strategy>
Strategy: <the strategy you'd like to execute>
"""

USER_PROMPT = """The current state of the game:

{obs}

To continue playing, please output one of the available strategies.
Do not output anything else.
"""


def tty_chars_to_str(chars):
    s = ""
    for line in chars:
        s += "".join([chr(c) for c in line]) + "\n"

    return s


async def _throttled_openai_chat_completion_acreate(
    prompt: List[Dict[str, str]],
    limiter: aiolimiter.AsyncLimiter,
    max_tokens: int,
    llm_type: str = "gpt-4o",
    temperature: float = 0.0,
    json: bool = False,
) -> Dict[str, Any]:
    async with limiter:
        trial = 0
        while trial < 5:
            try:
                if json:
                    return await asyncio.wait_for(
                        openai.ChatCompletion.acreate(
                            model=llm_type,
                            messages=[*prompt],
                            max_tokens=max_tokens,
                            stop=None,
                            temperature=temperature,
                            response_format={"type": "json_object"},
                        ),
                        timeout=60,
                    )
                else:
                    return await asyncio.wait_for(
                        openai.ChatCompletion.acreate(
                            model=llm_type,
                            messages=[*prompt],
                            max_tokens=max_tokens,
                            stop=None,
                            temperature=temperature,
                        ),
                        timeout=60,
                    )
            except openai.error.InvalidRequestError:
                return {"choices": [{"message": {"content": ""}}]}
            except openai.error.OpenAIError:
                trial -= 1
                await asyncio.sleep(10)
            except asyncio.exceptions.TimeoutError:
                trial -= 1
                await asyncio.sleep(10)
            trial += 1

        return {"choices": [{"message": {"content": ""}}]}


async def query_llm(
    prompt: List[Dict[str, str]],
    requests_per_minute: int = 300,
    max_tokens: int = None,
    llm_type: str = "gpt-4o",
    temperature: float = 0.0,
    json: bool = False,
) -> List[str]:
    requests_per_minute = 200

    session = ClientSession()
    openai.aiosession.set(session)
    limiter = aiolimiter.AsyncLimiter(requests_per_minute)

    if not max_tokens:
        max_tokens = max_tokens
    async_response = [
        _throttled_openai_chat_completion_acreate(
            prompt=prompt, limiter=limiter, max_tokens=max_tokens, llm_type=llm_type, temperature=temperature, json=json
        )
    ]
    response = await tqdm_asyncio.gather(*async_response)
    await session.close()

    response = response[0]

    # compute cost
    input_cost = response["usage"]["prompt_tokens"] * LLM_TO_COST[llm_type]["input"]

    output_cost = response["usage"]["completion_tokens"] * LLM_TO_COST[llm_type]["output"]
    total_cost = input_cost + output_cost

    return response["choices"][0]["message"]["content"], total_cost


@Strategy.wrap
def general_llm(bot: "Bot", use_language_wrapper: bool = False, f=None):
    stairs_strat = goto_stairs(bot)
    kick_strat = open_doors_kick(bot)
    explore_strat = explore(bot)
    search_strat = search(bot)

    if use_language_wrapper:
        nle_language = NLELanguageObsv()
        prompt_input = [
            {"role": "system", "content": LANGUAGE_WRAPPER_SYSTEM_PROMPT},
        ]
    else:
        prompt_input = [
            {"role": "system", "content": TTY_CHARS_SYSTEM_PROMPT},
        ]

    if f:
        f.write(tty_chars_to_str(bot.tty_chars))
        if use_language_wrapper:
            f.write(nle_language.text_glyphs(bot.glyphs, bot.raw_blstats).decode("latin-1") + "\n")

    num_trials = 0
    result = True
    while True:
        try:
            # parse language using language wrapper tools
            if use_language_wrapper:
                obs = nle_language.text_glyphs(bot.glyphs, bot.raw_blstats).decode("latin-1")

            else:
                # build prompt
                obs = tty_chars_to_str(bot.tty_chars)

            prompt_input.append(
                {
                    "role": "user",
                    "content": USER_PROMPT.format(obs=obs)
                    + ("\n The last executed strategy didn't work. Please try something else." if not result else ""),
                }
            )

            output, _ = asyncio.run(query_llm(prompt_input, max_tokens=500, temperature=0.7))
            reasoning, strat = list(map(lambda x: x.strip(), output.split("Strategy:")))

            # append to history
            prompt_input.append({"role": "assistant", "content": f"{output}"})

            print("Reasoning:", reasoning)
            print("LLM Strategy:", strat)
            if f:
                f.write(f"Reasoning: {reasoning}\n")
                f.write(f"LLM Strategy: {strat}\n")

            # execute chosen strategy
            if "goto_stairs" in strat:
                result = stairs_strat()
            elif "open_doors_kick" in strat:
                result = kick_strat()
            elif "explore" in strat:
                result = explore_strat()
            elif "search" in strat:
                result = search_strat()
            else:
                raise ValueError(f"Unknown strategy: {strat}")

            if not result:
                num_trials += 1
            else:
                num_trials = 0

            if f:
                f.write(tty_chars_to_str(bot.tty_chars))
                if use_language_wrapper:
                    f.write(nle_language.text_glyphs(bot.glyphs, bot.raw_blstats).decode("latin-1") + "\n")

            if num_trials >= 5:
                raise BotFinished

        except BotPanic:
            f.close()
            pass

        yield True


def test_llm(env, seed, use_language_wrapper: bool = False, record: bool = False):
    cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--max_episode_steps=100", "--no-render"])

    f = None
    if record:
        f = open(f"examples/llm_{env}_{seed}.txt", "w")

    cfg.strategies = [partial(general_llm, use_language_wrapper=use_language_wrapper, f=f)]
    status = play(cfg)
    f.close()
    assert status["end_status"].name == "TASK_SUCCESSFUL"
    print("Success!")


def main():
    register_minihack_components()

    num_trials = 1
    record = True
    use_language_wrapper = True

    env = "MiniHack-Corridor-R3-v0"
    successes = 0
    for seed in range(num_trials):
        # try:
        test_llm(env, seed, record=record, use_language_wrapper=use_language_wrapper)
        successes += 1
        # except:
        #     pass
    print(f"Successes: {successes}. Failures: {num_trials - successes}")

    # RESULTS (glyphs): 5 success, 0 failures
    # RESULTS (wrapper): 3 success, 2 failures
    # NOTE: these are pretty easy since the stairs down is right there in the beginning
    # it's still good the LLM solves it in the first step right away (>> random policy)

    # env = "MiniHack-Corridor-R3-v0"
    # successes = 0
    # for seed in range(num_trials):
    #     try:
    #         test_llm(env, seed, record=record, use_language_wrapper=use_language_wrapper)
    #         successes += 1
    #     except:
    #         pass
    # print(f"Successes: {successes}. Failures: {num_trials - successes}")

    # RESULTS (glyphs): 1 success, 4 failures
    # RESULTS (wrapper): 2 success, 3 failures
    # NOTE: v0_1 is a good example of where LLM sees the stairs and then goes to it right away


if __name__ == "__main__":
    main()
