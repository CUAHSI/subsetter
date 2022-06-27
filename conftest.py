import pytest

# typing imports
from typing import List


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "-S",
        "--run-slow",
        action="store_true",
        default=False,
        help="Run tests marked slow.",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Function]):
    if config.getoption("--run-slow") or config.getoption("-S"):
        # --run-slow given in cli: do not skip slow tests
        return
    deselected = []
    selected = []

    for item in items:
        if "slow" in item.keywords:
            deselected.append(item)
        else:
            selected.append(item)

    config.hook.pytest_deselected(items=deselected)
    items[:] = selected
