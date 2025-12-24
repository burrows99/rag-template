"""pytest configuration for Cognee integration tests.

This module configures pytest for the test suite following best practices:
- Registers custom markers to avoid warnings with --strict-markers
- Defines session-scoped fixtures for shared test resources
- Configures test discovery and execution settings
"""

import pytest


def pytest_configure(config):
    """Register custom markers to avoid warnings.
    
    Following pytest good practices, all markers used in tests should be
    registered to prevent typos and ensure consistency.
    """
    config.addinivalue_line(
        "markers",
        "integration: Integration tests that interact with real services (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers",
        "slow: Tests that take a long time to run (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "unit: Fast isolated unit tests"
    )


@pytest.fixture(scope="session")
def base_url():
    """Base URL for Cognee API.
    
    Session-scoped fixture as the base URL doesn't change during test run.
    This follows pytest best practice of using appropriate fixture scopes.
    """
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def api_headers():
    """Common headers for API requests.
    
    Session-scoped fixture as headers are static across all tests.
    """
    return {
        "accept": "application/json"
    }
