import pytest

from nle_code_wrapper.envs.minihack.play_minihack import register_minihack_components


@pytest.fixture(scope="session", autouse=True)
def register_components():
    register_minihack_components()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    stats = terminalreporter.stats
    print(f"\nCustom Summary:")
    for outcome, tests in stats.items():
        print(f"{outcome.capitalize()}: {len(tests)} tests")

