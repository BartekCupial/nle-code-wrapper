from nle_code_wrapper.agents.sample_factory.minihack.models.chaotic_dwarf import ChaoticDwarvenGPT5
from nle_code_wrapper.agents.sample_factory.minihack.models.scaled import ScaledNet

MODELS = [
    ScaledNet,
    ChaoticDwarvenGPT5,
]
MODELS_LOOKUP = {c.__name__: c for c in MODELS}
