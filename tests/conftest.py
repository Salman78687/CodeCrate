import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import docker

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def mock_executor():
    """Mock CodeExecutor for all tests."""
    with patch('codecrate.executor.executor') as mock_instance:
        # Create a mock container
        mock_container = MagicMock()
        mock_container.decode.return_value = "Test output"
        
        # Create a mock client instance
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.containers.run.return_value = mock_container
        mock_client.images.get.return_value = True
        mock_client.images.pull.return_value = True
        
        # Configure the mock instance
        mock_instance.client = mock_client
        mock_instance.run_code.return_value = {"exitCode": 0, "output": "Test output"}
        mock_instance.check_availability.return_value = True
        
        yield mock_instance 