import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def mock_executor_functions():
    """Mock executor functions for all tests."""
    with patch('codecrate.executor.run_code', autospec=True) as mock_run_code, \
         patch('codecrate.executor.check_docker_availability', autospec=True) as mock_check_docker:
        # Configure default mock responses
        mock_run_code.return_value = {
            "exitCode": 0,
            "output": "Test output",
            "error": None,
            "executionTime": 0.1,
            "stderr": None
        }
        mock_check_docker.return_value = True
        
        # Apply the mocks
        import codecrate.executor
        codecrate.executor.run_code = mock_run_code
        codecrate.executor.check_docker_availability = mock_check_docker
        
        yield 