import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import docker

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def mock_docker():
    """Mock Docker client for all tests."""
    with patch('docker.DockerClient') as mock_client:
        # Create a mock container
        mock_container = MagicMock()
        mock_container.decode.return_value = "Test output"
        
        # Create a mock client instance
        mock_instance = MagicMock()
        mock_instance.ping.return_value = True
        mock_instance.containers.run.return_value = mock_container
        mock_instance.images.get.return_value = True
        mock_instance.images.pull.return_value = True
        
        # Set the mock instance as the return value
        mock_client.return_value = mock_instance
        
        yield mock_instance 