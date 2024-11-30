import pytest

from nle_code_wrapper.envs.custom.play_custom import register_custom_components
from nle_code_wrapper.envs.minihack.play_minihack import register_minihack_components


@pytest.fixture(scope="session", autouse=True)
def register_components():
    register_minihack_components()
    register_custom_components()
