"""Executor tests with a fake Docker client: no Docker needed."""
import base64
from unittest.mock import MagicMock

import docker
import pytest
import requests
from docker.errors import DockerException

from codecrate.config import settings
from codecrate.executor import LANGUAGES, TIMEOUT_EXIT_CODE, CodeExecutor


def make_client(exit_code=0, stdout=b"hi\n", stderr=b"", wait_error=None):
    container = MagicMock()
    if wait_error:
        container.wait.side_effect = wait_error
    else:
        container.wait.return_value = {"StatusCode": exit_code}
    container.logs.side_effect = lambda stdout=True, stderr=False: (
        stdout_bytes if stdout else stderr_bytes
    )
    stdout_bytes, stderr_bytes = stdout, stderr
    client = MagicMock()
    client.containers.run.return_value = container
    client.ping.return_value = True
    return client, container


def run_kwargs(client):
    return client.containers.run.call_args


def test_unsupported_language_never_starts_a_container():
    client, _ = make_client()
    result = CodeExecutor(client).run_code("cobol", "DISPLAY 'HI'")
    assert result["exitCode"] == -1
    assert "Unsupported language" in result["error"]
    client.containers.run.assert_not_called()


def test_successful_run_returns_output_and_cleans_up():
    client, container = make_client(stdout=b"Hello\n")
    result = CodeExecutor(client).run_code("python", "print('Hello')")
    assert result["exitCode"] == 0
    assert result["output"] == "Hello\n"
    assert result["error"] is None
    container.remove.assert_called_once_with(force=True)


@pytest.mark.parametrize("language", list(LANGUAGES))
def test_code_is_passed_as_data_not_spliced_into_the_shell(language):
    code = "print('it''s') ; $(touch /pwned) `id` \"quotes\" \\ \n"
    client, _ = make_client()
    CodeExecutor(client).run_code(language, code)
    args, kwargs = run_kwargs(client)
    image, command = args
    assert image == LANGUAGES[language]["image"]
    assert command[:2] == ["sh", "-c"]
    assert code not in command[2]
    assert "pwned" not in command[2]
    assert base64.b64decode(kwargs["environment"]["CODE_B64"]).decode() == code


def test_container_is_locked_down():
    client, _ = make_client()
    CodeExecutor(client).run_code("python", "print(1)")
    _, kw = run_kwargs(client)
    assert kw["network_disabled"] is True
    assert kw["read_only"] is True
    assert kw["cap_drop"] == ["ALL"]
    assert "no-new-privileges" in kw["security_opt"]
    assert kw["user"] == "65534:65534"
    assert kw["pids_limit"] == settings.pids_limit
    assert kw["mem_limit"] == kw["memswap_limit"] == settings.memory_limit
    assert kw["nano_cpus"] == int(settings.cpus * 1e9)


def test_timeout_kills_the_container():
    client, container = make_client(wait_error=requests.exceptions.ReadTimeout())
    result = CodeExecutor(client).run_code("python", "while True: pass")
    container.kill.assert_called_once()
    container.remove.assert_called_once_with(force=True)
    assert result["exitCode"] == TIMEOUT_EXIT_CODE
    assert "timed out" in result["error"]


def test_compile_errors_come_back_on_stderr():
    client, _ = make_client(exit_code=1, stdout=b"", stderr=b"main.cpp:1: error")
    result = CodeExecutor(client).run_code("cpp", "int main( {")
    assert result["exitCode"] == 1
    assert result["stderr"] == "main.cpp:1: error"
    assert result["error"] is None


def test_out_of_memory_is_reported():
    client, _ = make_client(exit_code=137, stdout=b"")
    result = CodeExecutor(client).run_code("python", "x = 'a' * 10**10")
    assert "memory" in result["error"]


def test_huge_output_is_truncated():
    client, _ = make_client(stdout=b"x" * (settings.max_output_chars + 10))
    result = CodeExecutor(client).run_code("python", "print('x' * 10**6)")
    assert result["output"].endswith(f"truncated at {settings.max_output_chars} characters")


def test_docker_unavailable(monkeypatch):
    def no_docker():
        raise DockerException("no socket")

    monkeypatch.setattr(docker, "from_env", no_docker)
    result = CodeExecutor().run_code("python", "print(1)")
    assert result["error"] == "Docker is not available"
