from nle_code_wrapper.agents.sample_factory.minihack.models.scaled import ScaledNet

MODELS = [
    ScaledNet,
]
MODELS_LOOKUP = {c.__name__: c for c in MODELS}
