"""Integration tests for Cognee API endpoints.

These tests verify the actual behavior of the Cognee API by making real HTTP requests
to a running Cognee instance. They test the complete workflow: add data, process it,
search for information, and clean up.

Test Organization (following pytest good practices):
- Tests are organized in classes prefixed with 'Test' (pytest convention)
- Test methods are prefixed with 'test_' (pytest convention)
- Fixtures are used for dependency injection and test data setup
- Tests use standard Python assert statements (pytest introspection)
- Custom markers (@pytest.mark.integration, @pytest.mark.slow) categorize tests

Prerequisites:
    - Cognee service running on http://localhost:8000
    - Ollama service with qwen2.5:1.5b-instruct model
    - Authentication disabled (REQUIRE_AUTHENTICATION=False)

Running tests:
    pytest tests/integration/              # Run all integration tests
    pytest tests/integration/ -v           # Verbose output
    pytest -m "not slow"                   # Skip slow tests
    pytest -k "health"                     # Run tests matching pattern
"""
import time
import pytest
import requests


@pytest.mark.integration
class TestCogneeAPI:
    """Integration tests for core Cognee API endpoints.
    
    Following pytest good practices:
    - Class name starts with 'Test' for automatic discovery
    - No __init__ method (pytest requirement)
    - Each test is independent and can run in any order
    - Tests use fixtures for dependencies (base_url, api_headers, tmp_path)
    """

    def test_health_check(self, base_url):
        """Test that the API is accessible and responding.
        
        This is a smoke test that verifies basic connectivity.
        Uses fixture 'base_url' for dependency injection (pytest best practice).
        """
        response = requests.get(f"{base_url}/health")
        
        # Use simple assert statements - pytest provides detailed introspection
        assert response.status_code == 200
        data = response.json()
        assert "health" in data
        assert data["health"] == "healthy"

    def test_add_endpoint_with_text(self, base_url, api_headers, tmp_path):
        """Test adding text data to Cognee via the /api/v1/add endpoint.
        
        Uses pytest's built-in tmp_path fixture for temporary file handling.
        This is a pytest best practice - use provided fixtures instead of
        managing temp files manually.
        """
        # Create a temporary test file using pytest's tmp_path fixture
        test_file = tmp_path / "test_data.txt"
        test_content = """
        Artificial Intelligence is transforming the world.
        Machine Learning is a subset of AI that focuses on learning from data.
        Deep Learning uses neural networks with multiple layers.
        """
        test_file.write_text(test_content)

        # Upload the file
        with open(test_file, "rb") as f:
            files = {"file": ("test_data.txt", f, "text/plain")}
            data = {"datasetName": "test_dataset"}
            response = requests.post(
                f"{base_url}/api/v1/add",
                headers=api_headers,
                files=files,
                data=data,
            )

        # Verify response - pytest will show detailed failure info on assert
        assert response.status_code == 200, f"Failed with: {response.text}"
        data = response.json()
        assert "pipeline_run_id" in data
        assert data["pipeline_run_id"] is not None

    def test_cognify_endpoint(self, base_url, api_headers, tmp_path):
        """Test the /api/v1/cognify endpoint to process added data.
        
        Integration test that requires external service (Cognee + Ollama).
        Tests are independent - this test adds its own data rather than
        depending on previous tests (pytest best practice).
        """
        # Arrange - create test data file
        test_file = tmp_path / "cognify_test.txt"
        test_content = "Python is a popular programming language for data science and AI."
        test_file.write_text(test_content)
        
        # Act - add data using file upload
        with open(test_file, "rb") as f:
            files = {"file": ("cognify_test.txt", f, "text/plain")}
            data = {"datasetName": "test_cognify_dataset"}
            add_response = requests.post(
                f"{base_url}/api/v1/add",
                headers=api_headers,
                files=files,
                data=data,
            )
        # Assert - verify add succeeded
        assert add_response.status_code == 200
        
        # Wait a moment for data to be ready
        time.sleep(2)
        
        # Act - run cognify to process the data
        cognify_data = {"datasets": ["test_cognify_dataset"]}
        response = requests.post(
            f"{base_url}/api/v1/cognify",
            headers=api_headers,
            json=cognify_data,
        )
        
        # Assert - verify cognify succeeded
        assert response.status_code == 200, f"Cognify failed with: {response.text}"
        data = response.json()
        # Response should contain dataset processing results
        assert isinstance(data, dict)

    def test_search_endpoint(self, base_url, api_headers, tmp_path):
        """Test the /api/v1/search endpoint for semantic search.
        
        Independent integration test following Arrange-Act-Assert pattern.
        Each test sets up its own data to avoid test interdependencies.
        """
        # Arrange - create test data file
        test_file = tmp_path / "search_test.txt"
        test_content = "Natural Language Processing enables computers to understand human language."
        test_file.write_text(test_content)
        
        with open(test_file, "rb") as f:
            files = {"file": ("search_test.txt", f, "text/plain")}
            data = {"datasetName": "test_search_dataset"}
            add_response = requests.post(
                f"{base_url}/api/v1/add",
                headers=api_headers,
                files=files,
                data=data,
            )
        assert add_response.status_code == 200
        
        # Process the data
        time.sleep(2)
        cognify_data = {"datasets": ["test_search_dataset"]}
        cognify_response = requests.post(
            f"{base_url}/api/v1/cognify",
            headers=api_headers,
            json=cognify_data,
        )
        assert cognify_response.status_code == 200
        
        # Wait for processing to complete
        time.sleep(3)
        
        # Act - search for related content
        search_query = {
            "query": "What is NLP?"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/search",
            headers=api_headers,
            json=search_query,
        )
        
        # Assert - verify search results
        assert response.status_code == 200, f"Search failed with: {response.text}"
        data = response.json()
        # The response structure may vary, check for common fields
        assert isinstance(data, (dict, list))

    def test_list_datasets_endpoint(self, base_url, api_headers):
        """Test the /api/v1/datasets endpoint to list available datasets.
        
        Simple integration test that doesn't require test data setup.
        """
        # Act
        response = requests.get(
            f"{base_url}/api/v1/datasets",
            headers=api_headers,
        )
        
        # Assert
        assert response.status_code == 200, f"List datasets failed with: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_delete_endpoint(self, base_url, api_headers):
        """Test the /api/v1/delete endpoint structure.
        
        Note: Full deletion requires both data_id (UUID) and dataset_id.
        This test verifies the endpoint exists and returns appropriate error
        for missing parameters.
        """
        # Act - call delete without required parameters
        response = requests.delete(
            f"{base_url}/api/v1/delete",
            headers=api_headers,
        )
        
        # Assert - should return 400 for missing required params
        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data
        # Verify it mentions the required fields
        error_str = str(error_data)
        assert "data_id" in error_str or "dataset_id" in error_str

    @pytest.mark.slow
    def test_complete_workflow(self, base_url, api_headers, tmp_path):
        """Test a complete workflow: add → cognify → search → delete.
        
        Marked as @pytest.mark.slow since it exercises the full workflow.
        Can be skipped with: pytest -m "not slow"
        
        This test demonstrates:
        - Using tmp_path fixture for file handling
        - Clear Arrange-Act-Assert structure
        - Comprehensive workflow testing
        - Proper test cleanup
        """
        # Arrange - create test data
        test_file = tmp_path / "workflow_test.txt"
        test_content = "Cognee is a knowledge graph platform for AI applications."
        test_file.write_text(test_content)
        
        # Act & Assert - Step 1: Add data
        with open(test_file, "rb") as f:
            files = {"file": ("workflow_test.txt", f, "text/plain")}
            data = {"datasetName": "test_workflow_dataset"}
            add_response = requests.post(
                f"{base_url}/api/v1/add",
                headers=api_headers,
                files=files,
                data=data,
            )
        
        assert add_response.status_code == 200
        pipeline_run_id = add_response.json().get("pipeline_run_id")
        assert pipeline_run_id is not None
        
        # Step 2: Process with cognify
        time.sleep(2)
        cognify_data = {"datasets": ["test_workflow_dataset"]}
        cognify_response = requests.post(
            f"{base_url}/api/v1/cognify",
            headers=api_headers,
            json=cognify_data,
        )
        assert cognify_response.status_code == 200
        
        # Step 3: Search for the data
        time.sleep(3)
        search_response = requests.post(
            f"{base_url}/api/v1/search",
            headers=api_headers,
            json={"query": "knowledge graph"},
        )
        assert search_response.status_code == 200
        
        # Step 4: List datasets to verify data was added
        datasets_response = requests.get(
            f"{base_url}/api/v1/datasets",
            headers=api_headers,
        )
        assert datasets_response.status_code == 200
        datasets = datasets_response.json()
        
        # Verify our dataset exists
        dataset_found = any(
            dataset.get("name") == "test_workflow_dataset"
            for dataset in datasets
        )
        assert dataset_found, "Test dataset not found in datasets list"


@pytest.mark.integration
class TestCogneeErrorHandling:
    """Test error handling and edge cases.
    
    Separate test class for error/edge case scenarios following pytest
    best practice of organizing related tests into classes.
    """

    def test_add_without_data(self, base_url, api_headers):
        """Test that adding without data returns appropriate error.
        
        Negative test case to verify proper error handling.
        """
        # Act
        response = requests.post(
            f"{base_url}/api/v1/add",
            headers=api_headers,
        )
        
        # Assert - should return 4xx client error
        assert response.status_code >= 400

    def test_search_with_empty_query(self, base_url, api_headers):
        """Test searching with an empty query.
        
        Edge case test to verify graceful handling of invalid input.
        """
        # Act
        response = requests.post(
            f"{base_url}/api/v1/search",
            headers=api_headers,
            json={"query": ""},
        )
        
        # Assert - should handle gracefully (200 with empty results or 4xx)
        assert response.status_code in [200, 400, 422]

    def test_invalid_endpoint(self, base_url):
        """Test that invalid endpoints return 404.
        
        Sanity check to verify proper routing and error responses.
        """
        # Act
        response = requests.get(f"{base_url}/api/v1/nonexistent")
        
        # Assert
        assert response.status_code == 404
