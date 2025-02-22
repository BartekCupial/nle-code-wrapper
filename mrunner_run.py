import subprocess

from mrunner.helpers.client_helper import get_configuration

if __name__ == "__main__":
    cfg = get_configuration(print_diagnostics=True, with_neptune=False)

    del cfg["experiment_id"]
    run_script = cfg.pop("run_script", "nle_code_wrapper.agents.sample_factory.minihack.train")

    key_pairs = [f"--{key}={value}" for key, value in cfg.items()]
    cmd = ["python", "-m", run_script] + key_pairs
    subprocess.run(cmd)
