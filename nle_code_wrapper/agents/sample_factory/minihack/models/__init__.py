from nle_code_wrapper.agents.sample_factory.minihack.models.hybrid_encoder import NLEHybridEncoder
from nle_code_wrapper.agents.sample_factory.minihack.models.language_encoder import NLELanguageTransformerEncoder
from nle_code_wrapper.agents.sample_factory.minihack.models.terminal_encoder import NLETerminalCNNEncoder

MODELS = [
    NLETerminalCNNEncoder,
    NLEHybridEncoder,
    NLELanguageTransformerEncoder,
]
MODELS_LOOKUP = {c.__name__: c for c in MODELS}
