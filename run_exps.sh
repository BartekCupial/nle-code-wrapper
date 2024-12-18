for llm_model in "codellama/CodeLlama-13b-hf"; do # "codellama/CodeLlama-13b-hf" "codellama/CodeLlama-34b-hf" "codellama/CodeLlama-70b-hf"; do
	python generate_code.py \
		--llm_model $llm_model \
		--llm_tokenizer "hf-internal-testing/llama-tokenizer" \
		--target_filename "nle_code_wrapper/bot/strategies/open_doors.py" \
		--target_function "open_doors" \
		--dependencies "nle_code_wrapper/bot/bot.py" "nle_code_wrapper/bot/level.py" "nle_code_wrapper/bot/pathfinder/pathfinder.py"
done
# for llm_model in "codellama/CodeLlama-7b-hf" "codellama/CodeLlama-13b-hf" "codellama/CodeLlama-34b-hf" "codellama/CodeLlama-70b-hf"; do
# 	python generate_code.py \
# 		--llm_model $llm_model \
# 		--llm_tokenizer "hf-internal-testing/llama-tokenizer" \
# 		--target_filename "nle_code_wrapper/bot/strategies/goto_stairs.py" \
# 		--target_function "goto_stairs" \
# 		--dependencies "nle_code_wrapper/bot/bot.py" "nle_code_wrapper/bot/level.py" "nle_code_wrapper/bot/pathfinder/pathfinder.py"
# done


