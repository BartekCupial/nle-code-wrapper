import argparse
import json
import pytest
import os
import re
import subprocess
import time
import wandb

from vllm import LLM, SamplingParams

# Sample prompts.


def get_file_except_function(target_filename, fun_name):
    """Load the target file and divide it into three parts: before the function,
       contents of the function, and text after the function.
    """

    with open(target_filename) as file:
        file_iter = iter(file)

        fun_indent_size = 0
        text_pre = ""
        text_function = ""
        text_post = ""

        # Processing file up to function definition
        for line in file_iter:
            text_pre += line
            if line.strip().startswith(f"def {fun_name}"):
                fun_indent_size = len(line) - len(line.lstrip(' '))
                break
        else:
            raise ValueError(f"File does not contain the {fun_name} function!")

        line = next(file_iter)

        # Process docstrings:
        if line.strip().startswith("\"\"\""):
            text_pre += line
            for line in file_iter:
                text_pre += line
                if "\"\"\"" in line:
                    break
        else:
            text_function += line

        # Process the function
        for line in file_iter:
            current_indent_size = len(line) - len(line.lstrip(' '))

            if current_indent_size <= fun_indent_size and line.strip() != "":
                text_post += line
                break
            else:
                text_function += line

        # Process the rest of the file
        for line in file_iter:
            text_post += line


    return text_pre, text_function, text_post

def generate_function(llm, target_filename, fun_name, dependency_filenames, batch_size=1):

    # Load dependency files
    prompt = ""
    for fname in dependency_filenames:
        with open(fname) as infile:
            prompt += infile.read() + "\n\n"

    text_pre, text_function, text_post = get_file_except_function(target_filename, fun_name)

    prompt += text_pre
    prompts = [prompt for _ in range(batch_size)]

    sampling_params = SamplingParams(temperature=0.8, top_p=0.95, max_tokens=512)
    # Generate texts from the prompts. The output is a list of RequestOutput objects
    # that contain the prompt, generated text, and other information.
    output = llm.generate(prompts, sampling_params)
    final_texts = []

    for output_instance in output:
        generated_text = output_instance.outputs[0].text

        # Remove everything after the first function
        final_text = []
        for line in generated_text.split("\n"):
            if not line.startswith(" " * 4) and line.strip() != "":
                break
            final_text.append(line)

        final_text = "\n".join(final_text)

        final_texts.append(final_text)
    return final_texts

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm_model", type=str,
                        help="The LLM used to generate the code. Use the Huggingface format, compatible with VLLM",
                        required=True)
    parser.add_argument("--llm_tokenizer",
                        help="Tokenizer used with the LLM model. Use the Huggingface format",
                        type=str, required=True)
    parser.add_argument("--target_filename",
                        help="The filename containing the function you want the LLM to rewrite",
                        type=str, required=True)
    parser.add_argument("--target_function",
                        help="Name of the function to rewrite",
                        type=str, required=True)
    parser.add_argument("--dependencies",
                        help="File dependencies that should be useful for generating the target function" \
                        "These files will be added as context for LLM generation",
                        nargs="*",
                        type=str, required=True)

    return parser.parse_args()

def run_tests(args, test_result_filename):
        # TODO: this likes to hang sometimes for some reason...
        output = subprocess.run(["pytest", "-s", "-q", "-n", "8", "--json-report", f"--json-report-file={test_result_filename}", "--tb=no", "--capture=no", "--timeout", "10", "tests/minihack/"], capture_output=True)
        full_log = output.stdout.decode("utf-8")
        return full_log

def main():
    # Create a sampling params object.
    args = parse_args()

    run = wandb.init(entity="ideas-ncbr", project="code_generation", config=vars(args))

    # Create an LLM.
    llm = LLM(model=args.llm_model, tokenizer=args.llm_tokenizer, dtype="float16", tensor_parallel_size=1)
    # Generate a few version of the target function
    responses = generate_function(llm, args.target_filename, args.target_function, args.dependencies, batch_size=4)

    for response_idx, response in enumerate(responses):
        text_pre, text_function, text_post = get_file_except_function(args.target_filename, args.target_function)

        new_file_contents = text_pre + "\n" + response + "\n" + text_post

        test_filename = f"test_results/result_{int(time.time())}.json"

        try:
            os.replace(args.target_filename, args.target_filename + ".bak")
            with open(args.target_filename, "w") as code_file:
                code_file.write(new_file_contents)
            full_log = run_tests(args, test_filename)
        finally:
            # Retrieve the old file
            os.replace(args.target_filename + ".bak", args.target_filename)

        result_line = full_log.split("\n")[-2]
        # Parse the result line
        numbers = re.findall(r'\d+', result_line)
        failed, succeeded, warnings = numbers[:3]


        with open(test_filename, "r") as f:
            report_data = json.load(f)

        wandb.log({
            "failed": int(failed),
            "succeeded": int(succeeded),
            "warnings": int(warnings),
            "full_log": full_log,
            "generated_function": response}
        )
        wandb.save(test_filename)

if __name__ == "__main__":
    os.environ["VLLM_USE_TRITON_FLASH_ATTN"] = "0"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    main()
