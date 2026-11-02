"""HTTP API for CodeCrate."""
import logging
import threading
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from . import __version__
from . import executor as runner
from .config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.prepull_images and runner.check_docker_availability():
        # Download the language images in the background; the API is usable meanwhile
        threading.Thread(target=runner.executor.prepull, daemon=True).start()
    yield


app = FastAPI(
    title="CodeCrate API",
    description="Run code in isolated, resource-limited Docker containers.",
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class CodeRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"language": "python", "code": "print('Hello, World!')"}}
    )

    language: str = Field(..., description="One of: " + ", ".join(runner.LANGUAGES))
    code: str = Field(..., description="Source code to run")


class CodeResponse(BaseModel):
    output: Optional[str] = Field(None, description="Standard output")
    stderr: Optional[str] = Field(None, description="Standard error (compiler errors land here)")
    error: Optional[str] = Field(None, description="Set when the run could not finish normally")
    exitCode: int = Field(..., description="Process exit code (124 = timed out)")
    executionTime: float = Field(0, description="Run time in seconds")


class HealthResponse(BaseModel):
    status: str
    docker_available: bool
    supported_languages: List[str]
    version: str


class Metrics(BaseModel):
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time: float = 0
    language_usage: Dict[str, int] = {}


_metrics = Metrics()
_metrics_lock = threading.Lock()


def _record(language: str, ok: bool, seconds: float) -> None:
    with _metrics_lock:
        m = _metrics
        m.total_executions += 1
        if ok:
            m.successful_executions += 1
        else:
            m.failed_executions += 1
        m.average_execution_time = round(
            m.average_execution_time + (seconds - m.average_execution_time) / m.total_executions, 3
        )
        m.language_usage[language] = m.language_usage.get(language, 0) + 1


@app.get("/", tags=["General"])
def root():
    return {"name": "CodeCrate API", "version": __version__, "docs": "/api/docs"}


@app.get("/health", response_model=HealthResponse, tags=["Health"])
@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
def health():
    available = runner.check_docker_availability()
    return HealthResponse(
        status="healthy" if available else "unhealthy",
        docker_available=available,
        supported_languages=list(runner.LANGUAGES),
        version=__version__,
    )


@app.get("/api/v1/languages", tags=["Languages"])
def languages():
    return {
        "languages": [
            {"id": lang, "name": cfg["name"], "image": cfg["image"]}
            for lang, cfg in runner.LANGUAGES.items()
        ]
    }


@app.post("/api/v1/execute", response_model=CodeResponse, tags=["Execution"])
async def execute(request: CodeRequest):
    if request.language not in runner.LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language: {request.language}. "
            f"Supported: {', '.join(runner.LANGUAGES)}",
        )
    if len(request.code.encode("utf-8")) > settings.max_code_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Code is larger than {settings.max_code_bytes} bytes",
        )
    if not runner.check_docker_availability():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Docker is not available on the server",
        )

    result = await run_in_threadpool(runner.run_code, request.language, request.code)
    response = CodeResponse(
        output=result.get("output"),
        stderr=result.get("stderr"),
        error=result.get("error"),
        exitCode=result.get("exitCode", -1),
        executionTime=result.get("executionTime", 0),
    )
    _record(request.language, response.exitCode == 0 and not response.error, response.executionTime)
    logger.info(
        "Ran %s in %.2fs, exit code %d", request.language, response.executionTime, response.exitCode
    )
    return response


@app.get("/api/v1/metrics", response_model=Metrics, tags=["Monitoring"])
def metrics():
    with _metrics_lock:
        return _metrics.model_copy(deep=True)
