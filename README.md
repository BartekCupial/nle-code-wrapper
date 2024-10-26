# nle-code-wrapper

Code Wrapper for [Nethack Learning Environment (NLE)](https://github.com/facebookresearch/nle) and [MiniHack](https://github.com/facebookresearch/minihack)

### Installation

git submodule update --init --recursive

```bash
PYTHON_VERSION=$(python3 -c 'import sys; print(f"cp{sys.version_info.major}{sys.version_info.minor}")')
pip install  "https://github.com/BartekCupial/nle/releases/download/barlog/nle-0.9.0+a0aa022-${PYTHON_VERSION}-${PYTHON_VERSION}-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
pip install git+https://github.com/BartekCupial/minihack.git
pip install sample_factory
pip install git+https://gitlab.com/awarelab/mrunner.git
pip install -e external/nle_utils
pip install -e .
```