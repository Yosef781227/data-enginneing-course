"""Shared pytest fixtures. A fixture named `spark` is passed to any test that asks for it."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # the lab root, for `labutils`


@pytest.fixture(scope="session")
def spark():
    from labutils import get_spark
    return get_spark()
