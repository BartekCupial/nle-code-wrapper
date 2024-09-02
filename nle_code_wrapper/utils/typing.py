from __future__ import annotations

import argparse
from typing import Any, Callable, Dict, Optional, Tuple, Union

from nle_code_wrapper.utils.attr_dict import AttrDict

Config = Union[argparse.Namespace, AttrDict]

Env = Any

CreateEnvFunc = Callable[[str, Optional[Config], Optional[AttrDict], Optional[str]], Env]
