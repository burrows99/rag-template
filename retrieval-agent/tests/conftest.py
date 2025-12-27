from pathlib import Path

import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
