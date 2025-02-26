import hashlib
import os
import time


def get_unique_seed(process_num=None, episode_idx=0):
    """Generate a unique seed using process number, episode index, and high-resolution time."""
    pid = os.getpid()
    time_ns = time.time_ns()
    unique_str = f"{pid}_{process_num}_{episode_idx}_{time_ns}"
    hashed = hashlib.sha256(unique_str.encode()).hexdigest()
    seed = int(hashed[:8], 16)
    return seed
