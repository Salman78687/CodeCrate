import docker
import os
import tempfile
import logging
import json
import base64
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Language configurations
SUPPORTED_LANGUAGES = {
    "python": {
        "image": "python:3.9-slim",
        "command": ["bash", "-c", "echo '{code}' > /tmp/code.py && python /tmp/code.py"],
        "timeout": 30
    },
    "javascript": {
        "image": "node:18-slim",
        "command": ["bash", "-c", "echo '{code}' > /tmp/code.js && node /tmp/code.js"],
        "timeout": 30
    },
    "java": {
        "image": "openjdk:17-slim",
        "command": ["bash", "-c", "echo '{code}' > /tmp/Main.java && cd /tmp && javac Main.java && java Main"],
        "timeout": 30
    },
    "cpp": {
        "image": "gcc:latest",
        "command": ["bash", "-c", "echo '{code}' > /tmp/code.cpp && cd /tmp && g++ code.cpp -o code && ./code"],
        "timeout": 30
    },
    "go": {
        "image": "golang:1.20",
        "command": ["bash", "-c", "echo '{code}' > /tmp/main.go && cd /tmp && go run main.go"],
        "timeout": 30
    }
}

# Docker client configuration
try:
    # Try TCP first, fall back to socket
    try:
        client = docker.DockerClient(base_url='tcp://host.docker.internal:2375')
        client.ping()
        logger.info("Successfully connected to Docker daemon via TCP")
    except Exception as tcp_error:
        logger.warning(f"TCP connection failed: {str(tcp_error)}, trying socket...")
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        client.ping()
        logger.info("Successfully connected to Docker daemon via socket")
except Exception as e:
    logger.error(f"Failed to connect to Docker daemon: {str(e)}")
    client = None

# Resource limits
RESOURCE_LIMITS = {
    "memory": "256m",  # Increased for compilation
    "cpus": "1.0",     # Increased for faster compilation
    "timeout": 30,     # Increased timeout
}

def ensure_image_exists(image_name: str) -> bool:
    """Ensure Docker image exists, pull if necessary."""
    if not client:
        return False
        
    try:
        # Check if image exists locally
        try:
            client.images.get(image_name)
            logger.info(f"Image {image_name} exists locally")
            return True
        except docker.errors.ImageNotFound:
            logger.info(f"Image {image_name} not found locally, pulling...")
            client.images.pull(image_name)
            logger.info(f"Successfully pulled image {image_name}")
            return True
    except Exception as e:
        logger.error(f"Error ensuring image {image_name} exists: {str(e)}")
        return False

def run_code(language: str, code: str) -> Dict[str, Any]:
    """Execute code in an isolated Docker container."""
    if not client:
        return {"error": "Docker daemon is not available"}
        
    if language not in SUPPORTED_LANGUAGES:
        return {"error": f"Unsupported language: {language}"}
    
    config = SUPPORTED_LANGUAGES[language]
    
    # Ensure Docker image exists
    if not ensure_image_exists(config["image"]):
        return {"error": f"Failed to pull Docker image: {config['image']}"}

    # Prepare container configuration
    container_config = {
        "image": config["image"],
        "command": [cmd.replace("{code}", code) for cmd in config["command"]],
        "mem_limit": "512m",
        "cpu_period": 100000,
        "cpu_quota": 50000,
        "network_disabled": True,
        "remove": True
    }

    try:
        # Run container
        container = client.containers.run(**container_config)
        return {"output": container.decode('utf-8')}
    except Exception as e:
        return {"error": str(e)}

# Health check function
def check_docker_availability() -> bool:
    """Check if Docker daemon is accessible."""
    if not client:
        return False
    try:
        client.ping()
        return True
    except Exception:
        return False 