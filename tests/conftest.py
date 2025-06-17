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
    with patch('codecrate.executor.CodeExecutor') as mock_class:
        # Create a mock container
        mock_container = MagicMock()
        mock_container.decode.return_value = "Test output"
        
        # Create a mock client instance
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.containers.run.return_value = mock_container
        mock_client.images.get.return_value = True
        mock_client.images.pull.return_value = True
        
        # Create a mock executor instance
        mock_instance = MagicMock()
        mock_instance.client = mock_client
        mock_instance.run_code.return_value = {"exitCode": 0, "output": "Test output"}
        mock_instance.check_availability.return_value = True
        
        # Set the mock instance as the return value
        mock_class.return_value = mock_instance
        
        # Update the global executor
        from codecrate.executor import executor
        executor = mock_instance
        
        yield mock_instance 