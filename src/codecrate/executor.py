"""Run untrusted code in short-lived, locked-down Docker containers."""
from __future__ import annotations

import base64
import logging
import threading
import time
from typing import Any, Dict, Optional

import docker
from docker.errors import DockerException, ImageNotFound

from .config import settings

logger = logging.getLogger(__name__)

# Each language: the image it runs in, the file the code is written to, and
# the command that compiles/runs that file. Only these fixed strings reach the
# shell; the user's code travels in an environment variable (see _script).
LANGUAGES: Dict[str, Dict[str, str]] = {
    "python": {
        "name": "Python",
        "image": "python:3.12-slim",
        "file": "main.py",
        "run": "python3 main.py",
    },
    "javascript": {
        "name": "JavaScript",
        "image": "node:22-slim",
        "file": "main.js",
        "run": "node main.js",
    },
    "java": {
        "name": "Java",
        "image": "eclipse-temurin:21-jdk",
        "file": "Main.java",
        "run": "javac Main.java && java -Xmx128m Main",
    },
    "cpp": {
        "name": "C++",
        "image": "gcc:14",
        "file": "main.cpp",
        "run": "g++ -O2 -o main main.cpp && ./main",
    },
    "go": {
        "name": "Go",
        # Built locally from sandbox/go (docker compose builds it for you): golang
        # plus a pre-compiled standard library, copied into each run's scratch space
        "image": "codecrate-go:1.23",
        "build_context": "sandbox/go",
        "file": "main.go",
        "run": 'cp -r /gocache "$GOCACHE" && go run main.go',
    },
}

# Kept for compatibility with the original module's name
SUPPORTED_LANGUAGES = LANGUAGES

WORKDIR = "/tmp/run"
TIMEOUT_EXIT_CODE = 124  # same code coreutils `timeout` uses


def _script(language: str) -> str:
    """Shell script that decodes the code from $CODE_B64 into a file and runs it."""
    cfg = LANGUAGES[language]
    return (
        f"mkdir -p {WORKDIR} && cd {WORKDIR} && "
        f'printf %s "$CODE_B64" | base64 -d > {cfg["file"]} && '
        f'{cfg["run"]}'
    )


def _truncate(data: bytes) -> str:
    text = data.decode("utf-8", errors="replace")
    limit = settings.max_output_chars
    if len(text) > limit:
        return text[:limit] + f"\n... output truncated at {limit} characters"
    return text


class CodeExecutor:
    def __init__(self, client: Optional[docker.DockerClient] = None):
        self._client = client
        self._slots = threading.BoundedSemaphore(settings.max_concurrent)

    @property
    def client(self) -> Optional[docker.DockerClient]:
        """Docker client from the environment (DOCKER_HOST or the local socket)."""
        if self._client is None:
            try:
                self._client = docker.from_env()
            except DockerException as e:
                logger.error("Cannot connect to Docker: %s", e)
                return None
        return self._client

    def check_availability(self) -> bool:
        client = self.client
        if client is None:
            return False
        try:
            return bool(client.ping())
        except Exception:
            return False

    def ensure_image(self, image: str) -> bool:
        client = self.client
        if client is None:
            return False
        try:
            client.images.get(image)
            return True
        except ImageNotFound:
            local = next((c for c in LANGUAGES.values() if c["image"] == image and "build_context" in c), None)
            if local:
                logger.error(
                    "Image %s is missing: build it with `docker build -t %s %s` "
                    "(docker compose up --build does this automatically)",
                    image, image, local["build_context"],
                )
                return False
            logger.info("Pulling %s ...", image)
            try:
                client.images.pull(image)
                return True
            except Exception as e:
                logger.error("Failed to pull %s: %s", image, e)
                return False
        except Exception as e:
            logger.error("Cannot inspect image %s: %s", image, e)
            return False

    def prepull(self) -> None:
        """Pull every language image up front so first runs don't wait on downloads."""
        for cfg in LANGUAGES.values():
            self.ensure_image(cfg["image"])

    def run_code(self, language: str, code: str) -> Dict[str, Any]:
        """Run `code` and return output, stderr, exit code and duration."""
        if language not in LANGUAGES:
            return {"exitCode": -1, "error": f"Unsupported language: {language}"}
        client = self.client
        if client is None:
            return {"exitCode": -1, "error": "Docker is not available"}

        cfg = LANGUAGES[language]
        # Pull outside the timed section so a first-time download isn't a timeout
        if not self.ensure_image(cfg["image"]):
            hint = (
                f" (build it with: docker build -t {cfg['image']} {cfg['build_context']})"
                if "build_context" in cfg else ""
            )
            return {"exitCode": -1, "error": f"Could not get Docker image {cfg['image']}{hint}"}

        if not self._slots.acquire(timeout=settings.timeout_seconds):
            return {"exitCode": -1, "error": "Server is busy, please try again"}
        container = None
        try:
            container = client.containers.run(
                cfg["image"],
                ["sh", "-c", _script(language)],
                environment={
                    "CODE_B64": base64.b64encode(code.encode("utf-8")).decode("ascii"),
                    "HOME": "/tmp",
                    "GOCACHE": "/tmp/.gocache",
                    "GOTOOLCHAIN": "local",
                    # Keep Go's compiler within pids_limit (threads count as pids)
                    "GOMAXPROCS": "2",
                    "GOFLAGS": "-p=1 -trimpath",  # -trimpath matches the cached build
                },
                detach=True,
                user="65534:65534",  # nobody
                network_disabled=True,
                read_only=True,
                tmpfs={"/tmp": f"rw,exec,nosuid,size={settings.tmp_size}"},
                mem_limit=settings.memory_limit,
                memswap_limit=settings.memory_limit,  # no swap on top
                nano_cpus=int(settings.cpus * 1e9),
                pids_limit=settings.pids_limit,
                cap_drop=["ALL"],
                security_opt=["no-new-privileges"],
            )
            started = time.monotonic()
            timed_out = False
            try:
                status = container.wait(timeout=settings.timeout_seconds)
                exit_code = int(status.get("StatusCode", -1))
            except Exception:
                # requests raises ReadTimeout/ConnectionError when the wait times out
                timed_out = True
                exit_code = TIMEOUT_EXIT_CODE
                try:
                    container.kill()
                except Exception:
                    pass
            elapsed = round(time.monotonic() - started, 3)

            stdout = _truncate(container.logs(stdout=True, stderr=False))
            stderr = _truncate(container.logs(stdout=False, stderr=True))
            result: Dict[str, Any] = {
                "output": stdout,
                "stderr": stderr or None,
                "exitCode": exit_code,
                "executionTime": elapsed,
                "error": None,
            }
            if timed_out:
                result["error"] = f"Execution timed out after {settings.timeout_seconds} seconds"
            elif exit_code == 137:
                result["error"] = "Process was killed (memory limit exceeded?)"
            return result
        except Exception as e:
            logger.exception("Execution failed")
            return {"exitCode": -1, "error": f"Execution failed: {e}"}
        finally:
            self._slots.release()
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    pass


executor = CodeExecutor()


def run_code(language: str, code: str) -> Dict[str, Any]:
    return executor.run_code(language, code)


def check_docker_availability() -> bool:
    return executor.check_availability()


__all__ = [
    "CodeExecutor",
    "LANGUAGES",
    "SUPPORTED_LANGUAGES",
    "check_docker_availability",
    "executor",
    "run_code",
]
