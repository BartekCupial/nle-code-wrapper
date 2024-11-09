# nle-code-wrapper

Code Wrapper for [Nethack Learning Environment (NLE)](https://github.com/facebookresearch/nle) and [MiniHack](https://github.com/facebookresearch/minihack)

### Installation

git submodule update --init --recursive

```bash
MINOR=$(python3 -c 'import sys; print(f"cp{sys.version_info.major}{sys.version_info.minor}")')
pip install "https://github.com/BartekCupial/nle/releases/download/fair/nle-0.9.0-${MINOR}-${MINOR}-manylinux_2_17_$(uname -m).manylinux2014_$(uname -m).whl"
pip install -e external/nle_utils
pip install -e external/sample_factory
pip install -e .[dev,mrunner,minihack]
```

### post-installation setup
```bash
pre-commit install
```