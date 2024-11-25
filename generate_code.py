import pytest
import os
from vllm import LLM, SamplingParams

# Sample prompts.


def get_file_upto_function(target_filename, fun_name):
    text = ""
    # Load target file, up to the relevant function
    # This code might be somewhat fragile...
    with open(target_filename) as file:
        processed_imports = False
        processing_docstring = False
        for line in file:
            text += line
            if line.startswith(f"def {fun_name}"):
                processed_imports = True
            elif "\"\"\"" in line and processed_imports:
                if processing_docstring:
                    break
                else:
                    processing_docstring = True
    return text

def generate_function(llm, target_filename, fun_name, dependency_filenames, batch_size=1):

    # Load dependency files
    prompt = ""
    for fname in dependency_filenames:
        with open(fname) as infile:
            prompt += infile.read() + "\n\n"

    prompt += get_file_upto_function(target_filename, fun_name)
    prompts = [prompt for _ in range(batch_size)]

    sampling_params = SamplingParams(temperature=0.8, top_p=0.95, max_tokens=512)
    # Generate texts from the prompts. The output is a list of RequestOutput objects
    # that contain the prompt, generated text, and other information.
    output = llm.generate(prompts, sampling_params)
    final_texts = []
        
    for output_files in output:
        generated_text = output[0].outputs[0].text

        # Remove everything after the first function
        final_text = []
        for line in generated_text.split("\n"):
            if not line.startswith(" " * 4) and line.strip() != "":
                break
            final_text.append(line)

        final_text = "\n".join(final_text)

        final_texts.append(final_text)
    return final_texts

if __name__ == "__main__":
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    dependency_filenames = [
        "nle_code_wrapper/bot/bot.py",
        "nle_code_wrapper/bot/level.py",
        "nle_code_wrapper/bot/pathfinder/pathfinder.py",
        # "external/nle_utils/nle_utils/glyph.py",
    ]
    # Create a sampling params object.

    # Create an LLM.
    llm = LLM(model="codellama/CodeLlama-7b-hf", tokenizer="hf-internal-testing/llama-tokenizer", dtype="float16", tensor_parallel_size=1)

    target_filename = "nle_code_wrapper/bot/strategies/goto_stairs.py"
    responses = generate_function(llm, target_filename, "goto_stairs", dependency_filenames, batch_size=4)
    
    for response in responses:
        print(response)
        new_file_contents = get_file_upto_function(target_filename, "goto_stairs") + "\n" + response

        try:
            os.replace(target_filename, target_filename + ".bak")
            with open(target_filename, "w") as code_file:
                code_file.write(new_file_contents)
            # TODO: pytest stuff
            pytest.main(["-q", "--tb=no", "--capture=no", "tests/minihack/"])
        except:
            pass
        finally:
            # Retrieve the old file
            os.replace(target_filename + ".bak", target_filename)
