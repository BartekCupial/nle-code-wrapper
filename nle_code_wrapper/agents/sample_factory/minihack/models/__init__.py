from sample_factory.model.encoder import default_make_encoder_func

from nle_code_wrapper.agents.sample_factory.minihack.models.chaotic_dwarf import ChaoticDwarvenGPT5
from nle_code_wrapper.agents.sample_factory.minihack.models.clean import CleanNet
from nle_code_wrapper.agents.sample_factory.minihack.models.scaled import ScaledNet

MODELS = [
    default_make_encoder_func,
    CleanNet,
    ScaledNet,
    ChaoticDwarvenGPT5,
]
MODELS_LOOKUP = {c.__name__: c for c in MODELS}
