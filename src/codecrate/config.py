"""Settings, read from environment variables (all optional)."""
import os
from dataclasses import dataclass, field
from typing import List


def _int(name: str, default: int) -> int:
    return int(os.getenv(name, default))


def _float(name: str, default: float) -> float:
    return float(os.getenv(name, default))


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def _list(name: str, default: str) -> List[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    # Per-run sandbox limits
    timeout_seconds: int = field(default_factory=lambda: _int("CODECRATE_TIMEOUT", 15))
    memory_limit: str = field(default_factory=lambda: os.getenv("CODECRATE_MEMORY", "256m"))
    cpus: float = field(default_factory=lambda: _float("CODECRATE_CPUS", 0.5))
    pids_limit: int = field(default_factory=lambda: _int("CODECRATE_PIDS_LIMIT", 64))
    tmp_size: str = field(default_factory=lambda: os.getenv("CODECRATE_TMP_SIZE", "128m"))
    max_output_chars: int = field(default_factory=lambda: _int("CODECRATE_MAX_OUTPUT", 65536))
    max_code_bytes: int = field(default_factory=lambda: _int("CODECRATE_MAX_CODE_BYTES", 65536))

    # Server
    max_concurrent: int = field(default_factory=lambda: _int("CODECRATE_MAX_CONCURRENT", 4))
    prepull_images: bool = field(default_factory=lambda: _bool("CODECRATE_PREPULL", True))
    cors_origins: List[str] = field(
        default_factory=lambda: _list("CODECRATE_CORS_ORIGINS", "http://localhost:3000")
    )


settings = Settings()
