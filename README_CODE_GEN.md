Steps to run:

- Get a working image:
    - If you want to run on lumi, use the exisitng image in `/pfs/lustrep3/projappl/project_465001230/mwolczyk/vllm_rocm_v2.sif`
        - If for some reason, you want to build a new image lumi, use the [existing dockerfile](https://github.com/BartekCupial/nle-code-wrapper/blob/mwolczyk/generate_code/assets/vllm_dockerfile.rocm).
        - Note: I disabled building flash attention with the image because it made my computer explode, it might work if you have enough patience and/or RAM.
    - If you want to run on other servers, simply build an image that contains nle-code-wrapper dependencies (including `dev` packages so that you have access to the tests)
- Update the wandb user/project/credentials
- Run the `generate_code` script, e.g.,:
    
    ```bash
            python generate_code.py \                                                                    
                    --llm_model "codellama/CodeLlama-13b-hf" \                                                             
                    --llm_tokenizer "hf-internal-testing/llama-tokenizer" \                              
                    --target_filename "nle_code_wrapper/bot/strategies/goto_stairs.py" \                  
                    --target_function "goto_stairs" \                                                     
                    --dependencies "nle_code_wrapper/bot/bot.py" "nle_code_wrapper/bot/level.py" "nle_code_wrapper/bot/pathfinder/pathfinder.py"
    ```
    

TODO:

- Big thing: iterative code generation (learning from mistakes a’la Voyager)
- The unit tests like to hang forever sometimes, not sure why. I think it’s connected with how minihack spawns?
- It would be nice to control which unit tests we run, i.e., let’s not run the tests that do not use this specific function.
