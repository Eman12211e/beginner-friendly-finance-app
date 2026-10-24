import os
import sys

# Must be set before config is imported; load_dotenv does not override existing env vars.
os.environ["DATA_MODE"] = "demo"
os.environ["WARM_CACHE"] = "0"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest  # noqa: E402

from app import create_app  # noqa: E402
from services import cache  # noqa: E402


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def client():
    return create_app().test_client()
