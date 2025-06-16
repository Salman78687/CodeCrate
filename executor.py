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

# Docker client
client = docker.from_env()

# Language configurations
LANGUAGE_CONFIGS = {
    "python": {
        "image": "python:3.9-slim",
        "command": ["python", "/app/code.py"],
        "timeout": 30
    },
    "javascript": {
        "image": "node:18-slim",
        "command": ["node", "/app/code.js"],
        "timeout": 30
    },
    "java": {
        "image": "openjdk:17-slim",
        "command": ["java", "-cp", "/app", "Main"],
        "timeout": 30
    },
    "cpp": {
        "image": "gcc:latest",
        "command": ["./a.out"],
        "timeout": 30
    },
    "go": {
        "image": "golang:1.21-alpine",
        "command": ["./main"],
        "timeout": 30
    }
}

# Resource limits
RESOURCE_LIMITS = {
    "memory": "256m",  # Increased for compilation
    "cpus": "1.0",     # Increased for faster compilation
    "timeout": 30,     # Increased timeout
}

def ensure_image_exists(image_name: str) -> bool:
    """Ensure Docker image exists, pull if necessary."""
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
    if language not in LANGUAGE_CONFIGS:
        return {"error": f"Unsupported language: {language}"}
    
    config = LANGUAGE_CONFIGS[language]
    
    # Ensure Docker image exists
    if not ensure_image_exists(config["image"]):
        return {"error": f"Failed to pull Docker image: {config['image']}"}

    # Create temporary directory for code
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write code to file
        if language == "java":
            file_path = os.path.join(temp_dir, "Main.java")
            with open(file_path, "w") as f:
                f.write(code)
        elif language == "cpp":
            file_path = os.path.join(temp_dir, "code.cpp")
            with open(file_path, "w") as f:
                f.write(code)
        elif language == "go":
            file_path = os.path.join(temp_dir, "main.go")
            with open(file_path, "w") as f:
                f.write(code)
        else:
            file_path = os.path.join(temp_dir, f"code.{language}")
            with open(file_path, "w") as f:
                f.write(code)

        # Prepare container configuration
        container_config = {
            "image": config["image"],
            "command": config["command"],
            "volumes": {
                temp_dir: {"bind": "/app", "mode": "ro"}
            },
            "mem_limit": "512m",
            "cpu_period": 100000,
            "cpu_quota": 50000,
            "network_disabled": True,
            "remove": True
        }

        try:
            # Create and run container
            container = client.containers.run(**container_config)
            return {"output": container.decode("utf-8")}
        except docker.errors.ContainerError as e:
            return {"error": e.stderr.decode("utf-8") if e.stderr else str(e)}
    except Exception as e:
            return {"error": str(e)}

# Health check function
def check_docker_availability() -> bool:
    """Check if Docker daemon is accessible."""
    try:
        result = client.version()
        return result["Version"] != ""
    except Exception:
        return False