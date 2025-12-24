# Cognee API Integration Tests

This directory contains integration tests for the Cognee API endpoints.

## Prerequisites

Before running the tests, ensure:

1. **Cognee service is running** on `http://localhost:8000`
   ```bash
   docker compose up -d
   ```

2. **Ollama service is available** with required models:
   - LLM: `qwen2.5:1.5b-instruct`
   - Embeddings: `nomic-embed-text:v1.5`

3. **Authentication is disabled** in `.env`:
   ```
   REQUIRE_AUTHENTICATION=False
   ENABLE_BACKEND_ACCESS_CONTROL=False
   ```

## Running Tests

### Run all integration tests
```bash
uv run pytest tests/integration/
```

### Run with verbose output
```bash
uv run pytest tests/integration/ -v
```

### Run specific test
```bash
uv run pytest tests/integration/test_cognee_api.py::TestCogneeAPI::test_health_check
```

### Skip slow tests
```bash
uv run pytest tests/integration/ -m "not slow"
```

### Run only integration tests (if you have unit tests too)
```bash
uv run pytest -m integration
```

## Test Structure

- `test_cognee_api.py`: Main integration tests for Cognee API endpoints
  - `TestCogneeAPI`: Core functionality tests
  - `TestCogneeErrorHandling`: Error handling and edge case tests

## Test Categories

Tests are marked with pytest markers:

- `@pytest.mark.integration`: All tests interacting with real services
- `@pytest.mark.slow`: Tests that take longer to run (e.g., complete workflows)

## Fixtures

Shared fixtures are defined in `tests/conftest.py`:

- `base_url`: Cognee API base URL (http://localhost:8000)
- `api_headers`: Common HTTP headers for requests
- `tmp_path`: Pytest built-in fixture for temporary file paths

## Notes

- Tests include appropriate delays (`time.sleep()`) to allow async operations to complete
- Tests use real HTTP requests via the `requests` library
- Some tests may have side effects (data in databases) - clean up is included where possible
- Network connectivity and service availability affect test results
