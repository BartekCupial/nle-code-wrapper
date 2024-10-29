# nle-code-wrapper

Code Wrapper for [Nethack Learning Environment (NLE)](https://github.com/facebookresearch/nle) and [MiniHack](https://github.com/facebookresearch/minihack)

### Installation

git submodule update --init --recursive

```bash
PYTHON_VERSION=$(python3 -c 'import sys; print(f"cp{sys.version_info.major}{sys.version_info.minor}")')
pip install "https://github.com/BartekCupial/nle/releases/download/fair/nle-0.9.0-${PYTHON_VERSION}-${PYTHON_VERSION}-manylinux_2_17_$(uname -m).manylinux2014_$(uname -m).whl"
pip install git+https://github.com/facebookresearch/minihack.git
pip install git+https://gitlab.com/awarelab/mrunner.git
pip install -e external/nle_utils
pip install -e .[dev,sample_factory,mrunner]
```

### post-installation setup
```bash
pre-commit install
```