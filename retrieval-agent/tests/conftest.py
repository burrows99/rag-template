from pathlib import Path
import os

import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
# Try multiple locations in order of preference
env_paths = [
    Path(__file__).parent.parent.parent / ".env.retrieval-agent",  # ../langflow-agents/.env.retrieval-agent
    Path(__file__).parent.parent / ".env",  # retrieval-agent/.env
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break

# Override ELASTICSEARCH_URL for local testing (outside Docker)
# When running locally, 'elasticsearch' hostname doesn't resolve, so use localhost
# Inside Docker Compose, the original 'http://elasticsearch:9200' is used via Docker network
if os.environ.get("ELASTICSEARCH_URL") == "http://elasticsearch:9200":
    os.environ["ELASTICSEARCH_URL"] = "http://localhost:9200"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
