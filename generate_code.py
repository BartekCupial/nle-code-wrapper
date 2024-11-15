from vllm import LLM, SamplingParams

# Sample prompts.

def main():
    dependency_filenames = [
        "nle_code_wrapper/bot/bot.py",
        "nle_code_wrapper/bot/level.py",
        "nle_code_wrapper/bot/pathfinder/pathfinder.py",
        # "external/nle_utils/nle_utils/glyph.py",
    ]

    prompt = ""
    for fname in dependency_filenames:
        with open(fname) as infile:
            prompt += infile.read() + "\n\n"

    target_filename = "nle_code_wrapper/bot/strategies/goto_stairs.py"

    with open(target_filename) as file:
        processed_imports = False
        processing_docstring = False
        for line in file:
            prompt += line
            if "def" in line:
                processed_imports = True
            elif "\"\"\"" in line:
                if processing_docstring:
                    break
                else:
                    processing_docstring = True

    print(prompt)

    # Create a sampling params object.
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95, max_tokens=512)

    # Create an LLM.
    llm = LLM(model="codellama/CodeLlama-34b-hf", tokenizer="hf-internal-testing/llama-tokenizer", dtype="float16", tensor_parallel_size=2)
    # Generate texts from the prompts. The output is a list of RequestOutput objects
    # that contain the prompt, generated text, and other information.
    outputs = llm.generate([prompt], sampling_params)
    # Print the outputs.
    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Generated text: {generated_text}")

if __name__ == "__main__":
    main()
