import argparse
import pytest
import os
import re
import subprocess
import wandb

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
    parser.add_argument("--llm_model", type=str, required=True)
    parser.add_argument("--llm_tokenizer", type=str, required=True)
    parser.add_argument("--target_filename", type=str, required=True)
    parser.add_argument("--target_function", type=str, required=True)
    parser.add_argument("--dependencies", nargs="*", type=str, required=True)

    return parser.parse_args()

def run_tests(new_file_contents, args):
        os.replace(args.target_filename, args.target_filename + ".bak")
        with open(args.target_filename, "w") as code_file:
            code_file.write(new_file_contents)

        output = subprocess.run(["pytest", "-s", "-q", "--tb=no", "--capture=no", "--timeout", "10", "tests/minihack/"], capture_output=True) 
        full_log = output.stdout.decode("utf-8")
        return full_log

def main():
    # Create a sampling params object.
    args = parse_args()

    wandb.init(entity="ideas-ncbr", project="code_generation", config=vars(args))

    # Create an LLM.
    # TODO: dtype as argument?
    llm = LLM(model=args.llm_model, tokenizer=args.llm_tokenizer, dtype="float16", tensor_parallel_size=1)
    responses = generate_function(llm, args.target_filename, args.target_function, args.dependencies, batch_size=4)
    
    for response in responses:
        print(response)
        new_file_contents = get_file_upto_function(args.target_filename, args.target_function) + "\n" + response

        try:
            full_log = run_tests(new_file_contents, args)
        finally:
            # Retrieve the old file
            os.replace(args.target_filename + ".bak", args.target_filename)
        result_line = full_log.split("\n")[-2]
        numbers = re.findall(r'\d+', result_line)
        failed, succeeded, warnings = numbers[:3]
        print(numbers)
        wandb.log({"failed": int(failed), "succeeded": int(succeeded), "warnings": int(warnings), "full_log": full_log})

if __name__ == "__main__":
    os.environ["VLLM_USE_TRITON_FLASH_ATTN"] = "0"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    main()
