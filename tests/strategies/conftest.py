import pytest

from nle_code_wrapper.envs.minihack.play_minihack import register_minihack_components


@pytest.fixture(scope="session", autouse=True)
def register_components():
    register_minihack_components()
