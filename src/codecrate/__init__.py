"""
CodeCrate - A secure online code execution platform
"""

__version__ = "0.1.0"

from .executor import run_code, check_docker_availability
 
__all__ = ['run_code', 'check_docker_availability'] 