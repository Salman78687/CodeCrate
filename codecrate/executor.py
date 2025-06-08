import uuid
import os
import subprocess
import logging
import json
import base64
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SUPPORTED_LANGUAGES = {
    "py": {"image": "python:3.9-slim", "cmd": ["python", "-c"]},
    "cpp": {"image": "gcc:latest", "cmd": ["bash", "-c"], "wrapper": "echo '{code}' > /tmp/main.cpp && cd /tmp && g++ main.cpp -o main && chmod +x main && ./main"},
    "java": {"image": "openjdk:17-slim", "cmd": ["bash", "-c"], "wrapper": "echo '{code}' > /tmp/Main.java && cd /tmp && javac Main.java && java Main"},
    "js": {"image": "node:18-slim", "cmd": ["node", "-e"]},
    "go": {"image": "golang:1.21-alpine", "cmd": ["sh", "-c"], "wrapper": "cd /tmp && echo '{code}' > main.go && go run main.go"},
}

# Resource limits
RESOURCE_LIMITS = {
    "memory": "256m",  # Increased for compilation
    "cpus": "1.0",     # Increased for faster compilation
    "timeout": 30,     # Increased timeout
}

def ensure_image_exists(image: str) -> bool:
    """Pull Docker image if it doesn't exist locally."""
    try:
        # Check if image exists
        result = subprocess.run(
            ["docker", "images", "-q", image],
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            logger.info(f"Pulling Docker image: {image}")
            pull_result = subprocess.run(
                ["docker", "pull", image],
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes for pulling
            )
            if pull_result.returncode != 0:
                logger.error(f"Failed to pull image {image}: {pull_result.stderr}")
                return False
            logger.info(f"Successfully pulled image: {image}")
        
        return True
    except Exception as e:
        logger.error(f"Error checking/pulling image {image}: {str(e)}")
        return False

def run_code(language: str, code: str) -> Dict[str, Any]:
    """
    Execute code in an isolated Docker container.
    
    Args:
        language: Programming language identifier
        code: Source code to execute
        
    Returns:
        Dict with either 'output' or 'error' key
    """
    code_id = str(uuid.uuid4())
    
    # Validate language
    if language not in SUPPORTED_LANGUAGES:
        logger.warning(f"Unsupported language requested: {language}")
        return {"error": f"Unsupported language: {language}. Supported: {list(SUPPORTED_LANGUAGES.keys())}", "exitCode": -1}
    
    lang_config = SUPPORTED_LANGUAGES[language]
    image = lang_config["image"]
    
    # Ensure image exists
    if not ensure_image_exists(image):
        return {"error": f"Failed to pull Docker image: {image}", "exitCode": -1}
    
    # Build docker command
    docker_cmd = [
        "docker", "run", "--rm",
        "--network", "none",  # Security: no network access
        "--memory", RESOURCE_LIMITS["memory"],
        "--cpus", RESOURCE_LIMITS["cpus"],
        "--security-opt", "no-new-privileges",  # Security: prevent privilege escalation
        "-w", "/tmp",  # Set working directory to /tmp
        image
    ]
    
    # Add command and code
    docker_cmd.extend(lang_config["cmd"])
    
    # Prepare the code based on language
    if "wrapper" in lang_config:
        # For compiled languages, escape quotes properly
        # Replace single quotes with '\'' to properly escape them in bash
        escaped_code = code.replace("\\", "\\\\").replace("'", "'\"'\"'")
        code_to_execute = lang_config["wrapper"].format(code=escaped_code)
    else:
        # For interpreted languages, we can pass code directly
        code_to_execute = code
    
    docker_cmd.append(code_to_execute)
    
    logger.info(f"Executing {language} code in container with image: {image}")
    logger.debug(f"Docker command: {' '.join(docker_cmd[:10])}...")  # Log first part of command
    
    try:
        # Execute
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=RESOURCE_LIMITS["timeout"]
        )
        
        output = result.stdout
        error = result.stderr
        
        # Prepare response
        if result.returncode == 0:
            response = {"output": output, "exitCode": 0}
            if error:  # Include stderr if present (some languages use it for warnings)
                response["stderr"] = error
        else:
            response = {
                "error": error or output or f"Process exited with code {result.returncode}",
                "exitCode": result.returncode
            }
            
        logger.info(f"Execution completed with exit code: {result.returncode}")
        return response
            
    except subprocess.TimeoutExpired:
        logger.warning(f"Code execution timed out after {RESOURCE_LIMITS['timeout']}s")
        return {"error": f"Code execution timed out after {RESOURCE_LIMITS['timeout']} seconds", "exitCode": -1}
    except subprocess.CalledProcessError as e:
        logger.error(f"Docker command failed: {str(e)}")
        return {"error": f"Docker execution failed: {str(e)}", "exitCode": e.returncode}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {"error": f"Internal error: {str(e)}", "exitCode": -1}

# Health check function
def check_docker_availability() -> bool:
    """Check if Docker daemon is accessible."""
    try:
        result = subprocess.run(
            ["docker", "version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False 